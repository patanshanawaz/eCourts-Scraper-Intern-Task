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

def download_cause_list(state_code, district_code, court_complex_code, court_code, date_str):
    options = webdriver.ChromeOptions()
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

        # Save to JSON
        filename_json = f"cause_list_{date_str.replace('/', '_')}.json"
        with open(filename_json, "w") as f:
            json.dump(data, f)
        print(f"Saved cause list to {filename_json}")

        # Try to download PDF if available
        try:
            pdf_link_element = driver.find_element(By.PARTIAL_LINK_TEXT, ".pdf")
            pdf_link = pdf_link_element.get_attribute("href")
            response = requests.get(pdf_link)
            filename_pdf = f"cause_list_{date_str.replace('/', '_')}.pdf"
            with open(filename_pdf, "wb") as f:
                f.write(response.content)
            print(f"Downloaded PDF to {filename_pdf}")
        except:
            print("PDF not available")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        driver.quit()

def check_case_status(cnr):
    # For case status, but since captcha, perhaps not implement fully
    print("Case status check not implemented due to captcha")

def main():
    parser = argparse.ArgumentParser(description="eCourts Scraper")
    parser.add_argument("--state", required=True, help="State code")
    parser.add_argument("--district", required=True, help="District code")
    parser.add_argument("--complex", required=True, help="Court complex code")
    parser.add_argument("--court", required=True, help="Court code")
    parser.add_argument("--date", help="Date in dd/mm/yyyy")
    parser.add_argument("--today", action="store_true", help="Download for today")
    parser.add_argument("--tomorrow", action="store_true", help="Download for tomorrow")
    parser.add_argument("--cnr", help="CNR number to check case status")

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
        download_cause_list(args.state, args.district, args.complex, args.court, date_str)

if __name__ == "__main__":
    main()

