# eCourts Scraper

This script scrapes cause lists from eCourts India website and saves them as JSON and PDF.

## Setup

1. Install Python 3.8+
2. Install dependencies: `pip install -r requirements.txt`
3. Run the script with appropriate arguments.

## Usage

To download cause list for today:

```
python main.py --state <state_code> --district <district_code> --complex <complex_code> --court <court_code>
```

For tomorrow:

```
python main.py --state <state_code> --district <district_code> --complex <complex_code> --court <court_code> --tomorrow
```

For specific date:

```
python main.py --state <state_code> --district <district_code> --complex <complex_code> --court <court_code> --date dd/mm/yyyy
```

## Finding Codes

Visit https://services.ecourts.gov.in/ecourtindia_v6/?p=cause_list/index and inspect the dropdowns to find the values for state, district, etc.

## Note

Case status check is not implemented due to captcha.

## Requirements

- Chrome browser
- Internet connection

## Output
- `cause_list_dd_mm_yyyy.json`: JSON array of table rows
- `cause_list_dd_mm_yyyy.pdf`: PDF if available
