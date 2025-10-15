import argparse
import datetime
import json
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from webdriver_manager.chrome import ChromeDriverManager

def download_cause_list(state_code, district_code, court_complex_code, court_code, date_str, headless=True):
    options = webdriver.ChromeOptions()
    if headless:
        # Use headless mode by default; allow visible browser for recording with --no-headless
        options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/index")

        # Wait for the form to load
        WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.ID, "sess_state_code")))

        # Select state
        select_state = Select(driver.find_element(By.ID, "sess_state_code"))
        select_state.select_by_value(state_code)

        # Wait for district
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "sess_dist_code")))
        select_district = Select(driver.find_element(By.ID, "sess_dist_code"))
        select_district.select_by_value(district_code)

        # Court complex
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "sess_court_complex_code")))
        select_complex = Select(driver.find_element(By.ID, "sess_court_complex_code"))
        select_complex.select_by_value(court_complex_code)

        # Court
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "sess_court_code")))
        select_court = Select(driver.find_element(By.ID, "sess_court_code"))
        select_court.select_by_value(court_code)

        # Date
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "date")))
        date_input = driver.find_element(By.ID, "date")
        date_input.clear()
        date_input.send_keys(date_str)

        # Submit
        WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "submit")))
        submit_button = driver.find_element(By.ID, "submit")
        submit_button.click()

        # Wait for results
        WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.TAG_NAME, "table")))

        # Extract table data
        table = driver.find_element(By.TAG_NAME, "table")
        rows = table.find_elements(By.TAG_NAME, "tr")
        data = []
        for row in rows[1:]:  # skip header
            cols = row.find_elements(By.TAG_NAME, "td")
            if cols:
                data.append([col.text for col in cols])

        # Try to find a court name/title on the page (best-effort)
        court_name = None
        try:
            # many pages show a heading above the table
            headings = driver.find_elements(By.TAG_NAME, "h2") + driver.find_elements(By.TAG_NAME, "h3")
            for h in headings:
                text = h.text.strip()
                if text:
                    court_name = text
                    break
        except:
            court_name = None

        # Save to JSON
        filename_json = f"cause_list_{date_str.replace('/', '_')}.json"
        with open(filename_json, "w") as f:
            json.dump(data, f)
        print(f"Saved cause list to {filename_json}")

        # Try to download PDF if available
        filename_pdf = None
        try:
            pdf_link_element = driver.find_element(By.PARTIAL_LINK_TEXT, ".pdf")
            pdf_link = pdf_link_element.get_attribute("href")
            response = requests.get(pdf_link)
            filename_pdf = f"cause_list_{date_str.replace('/', '_')}.pdf"
            with open(filename_pdf, "wb") as f:
                f.write(response.content)
            print(f"Downloaded PDF to {filename_pdf}")
        except Exception:
            print("PDF not available")

        # Return structured result for further processing
        return {
            "data": data,
            "json": filename_json,
            "pdf": filename_pdf,
            "court_name": court_name,
            "date": date_str,
            "state": state_code,
            "district": district_code,
            "court_complex": court_complex_code,
            "court_code": court_code,
        }

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

def check_case_status(cnr):
    # For case status, but since captcha, perhaps not implement fully
    print("Case status check not implemented due to captcha")


def find_case_in_cause_list(state, district, complex_code, court_code, date_str, case_query, headless=True):
    """Fetch the cause list for the given court/date and search for case_query (CNR or case string).
    Returns a dict with matches (list of {serial, row, court_name}) or empty list if none found.
    """
    result = download_cause_list(state, district, complex_code, court_code, date_str, headless=headless)
    data = result.get("data", [])
    court_name = result.get("court_name")

    matches = []
    q = case_query.strip().lower()
    for row in data:
        # try to get serial number from first column if numeric
        serial = None
        if len(row) >= 1:
            first = row[0].strip()
            if first.isdigit():
                serial = first
        # search in any column
        found = False
        for col in row:
            if q in col.lower():
                found = True
                break
        if found:
            matches.append({
                "serial": serial,
                "row": row,
                "court_name": court_name,
            })

    # Save matches to file for review
    out_file = f"case_search_{case_query.replace(' ', '_')}_{date_str.replace('/','_')}.json"
    with open(out_file, "w") as f:
        json.dump(matches, f)

    return {
        "matches": matches,
        "output_file": out_file,
        "cause_list_json": result.get("json"),
        "cause_list_pdf": result.get("pdf"),
        "court_name": court_name,
    }

def main():
    parser = argparse.ArgumentParser(description="eCourts Scraper")
    parser.add_argument("--state", required=True, help="State code")
    parser.add_argument("--district", required=True, help="District code")
    parser.add_argument("--complex", required=True, help="Court complex code")
    parser.add_argument("--court", required=True, help="Court code")
    parser.add_argument("--no-headless", dest="no_headless", action="store_true", help="Run browser in visible mode for recording")
    parser.add_argument("--date", help="Date in dd/mm/yyyy")
    parser.add_argument("--today", action="store_true", help="Download for today")
    parser.add_argument("--tomorrow", action="store_true", help="Download for tomorrow")
    parser.add_argument("--cnr", help="CNR number to check case status")
    parser.add_argument("--case", help="Case query to search inside the cause list (CNR or text)")
    parser.add_argument("--causelist", action="store_true", help="Only download the cause list for the given court/date")

    args = parser.parse_args()

    if args.date:
        date_str = args.date
    elif args.tomorrow:
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        date_str = tomorrow.strftime("%d/%m/%Y")
    else:
        today = datetime.date.today()
        date_str = today.strftime("%d/%m/%Y")

    if args.cnr:
        check_case_status(args.cnr)
    else:
        headless_mode = not args.no_headless
        if args.causelist:
            # just download and save cause list
            res = download_cause_list(args.state, args.district, args.complex, args.court, date_str, headless=headless_mode)
            print(json.dumps({"saved_json": res.get("json"), "saved_pdf": res.get("pdf")}, indent=2))
        elif args.case:
            res = find_case_in_cause_list(args.state, args.district, args.complex, args.court, date_str, args.case, headless=headless_mode)
            if res["matches"]:
                print(f"Found {len(res['matches'])} matches for '{args.case}' (saved to {res['output_file']})")
                for m in res["matches"]:
                    print(f"Serial: {m['serial']}, Court: {m.get('court_name')}, Row: {m['row']}")
            else:
                print(f"No matches found for '{args.case}' on {date_str}")
        else:
            # default: download cause list
            res = download_cause_list(args.state, args.district, args.complex, args.court, date_str, headless=headless_mode)
            print(json.dumps({"saved_json": res.get("json"), "saved_pdf": res.get("pdf")}, indent=2))

if __name__ == "__main__":
    main()

