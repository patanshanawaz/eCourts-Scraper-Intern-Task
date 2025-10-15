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

Additional options:

- Run browser visibly (useful to record the browser):

```
python main.py --state <state_code> --district <district_code> --complex <complex_code> --court <court_code> --no-headless
```

- Download only the cause list (save JSON and PDF if available):

```
python main.py --state <state_code> --district <district_code> --complex <complex_code> --court <court_code> --causelist
```

- Search for a case (CNR or text) in the cause list for today/tomorrow/specific date:

```
python main.py --state <state_code> --district <district_code> --complex <complex_code> --court <court_code> --case "CNR123456789" --today --no-headless
```

Recording the run (suggested):

1. Use QuickTime Player: File -> New Screen Recording. Start recording and then run the script with `--no-headless`.
2. Or use OBS (recommended for better control): capture the Chrome window, start recording, then run the script with `--no-headless`.
3. Optionally use the provided helper `run_record.sh` to give you a few seconds to start the recorder, then automatically launch the script:

```
./run_record.sh <state> <district> <complex> <court> [--case "query"] [--causelist]
```

Uploading video to YouTube:

- Manual: Go to YouTube -> Create -> Upload video, follow the prompts.
- Automated: Use YouTube Data API v3 with OAuth credentials and `google-api-python-client`. This requires setting up a Google Cloud Project and OAuth client credentials — see Google docs. I can provide a script if you want to automate uploads.

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
