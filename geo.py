# import requests
# import gspread
# from oauth2client.service_account import ServiceAccountCredentials
# from datetime import datetime
# import time

# # Replace with your actual API key and target URL
# api_key = 'AIzaSyBSIOigkrHJzpyOkh5t8-Vuoj5MkC4gAmA'
# url = 'https://www.geo.tv'

# # Google Sheets setup
# scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# creds = ServiceAccountCredentials.from_json_keyfile_name('key6.json', scope)
# client = gspread.authorize(creds)

# # Open the Google Sheet by its name
# # sheet = client.open('lcp geo').sheet1
# sheet = client.open_by_key('1t62-kGyrF6ROgsaUd8kjGqgxaHaUABsk-XsBf6kUgW8').sheet1

# def fetch_lcp(strategy):
#     """Fetch the Largest Contentful Paint (LCP) for a given strategy (mobile or desktop)."""
#     print(f"Fetching LCP for {strategy}...")
#     api_url = f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={url}&strategy={strategy}&key={api_key}'
#     response = requests.get(api_url)

#     print(f"Response Status Code for {strategy}: {response.status_code}")
#     if response.status_code == 200:
#         try:
#             data = response.json()
#             try:
#                 lcp_ms = data['loadingExperience']['metrics']['LARGEST_CONTENTFUL_PAINT_MS']['percentile']
#                 lcp_seconds = lcp_ms / 1000
#                 print(f"{strategy.capitalize()} Field Data - Largest Contentful Paint: {lcp_seconds} seconds")
#             except KeyError:
#                 print(f"{strategy.capitalize()} Field Data unavailable. Checking Lab Data...")
#                 lcp_ms = data['lighthouseResult']['audits']['largest-contentful-paint']['numericValue']
#                 lcp_seconds = lcp_ms / 1000
#                 print(f"{strategy.capitalize()} Lab Data - Largest Contentful Paint: {lcp_seconds} seconds")
#             return lcp_seconds
#         except KeyError as e:
#             print(f"Error processing JSON response for {strategy}: {e}")
#             return None
#     else:
#         print(f"Failed to retrieve data for {strategy}. Error: {response.text}")
#         return None

# print("Script started...") 

# try:
#     # Check if sheet is empty and add headers if necessary
#     if not sheet.get_all_values():
#         print("Adding headers to Google Sheet...")
#         header = ['Timestamp', 'Label', 'LCP (s)', 'Label', 'LCP (s)']
#         sheet.append_row(header)

#     print("Entering while loop...")
#     # while True:
#     print("Fetching LCP values...")
#     mobile_lcp = fetch_lcp('mobile')
#     desktop_lcp = fetch_lcp('desktop')

#     print(f"Mobile LCP: {mobile_lcp}, Desktop LCP: {desktop_lcp}")
#     if mobile_lcp is None or desktop_lcp is None:
#         print("Skipping data row append due to missing values.")
#     else:
#         # Get the current timestamp
#         now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#         # Prepare the data row
#         data_row = [now, 'Mobile', mobile_lcp, 'Desktop', desktop_lcp]
#         print("Appending data row to Google Sheet...")
#         sheet.append_row(data_row)

#     # print("Sleeping for 24 hours...")
#     # time.sleep(24 * 60 * 60)  # Sleep for 24 hours

# except Exception as e:
#     print(f"An error occurred: {e}")





















import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# ==========================================
# GOOGLE PAGESPEED API KEY
# ==========================================

api_key = 'AIzaSyBSIOigkrHJzpyOkh5t8-Vuoj5MkC4gAmA'

# ==========================================
# WEBSITES TO MONITOR
# ==========================================

websites = {
    'Geo': 'https://www.geo.tv',
    'TN': 'https://thenews.com.pk',
    'JE': 'https://jang.com.pk/en'
}

# ==========================================
# GOOGLE SHEETS SETUP
# ==========================================

scope = [
    'https://spreadsheets.google.com/feeds',
    'https://www.googleapis.com/auth/drive'
]

creds = ServiceAccountCredentials.from_json_keyfile_name(
    'key6.json',
    scope
)

client = gspread.authorize(creds)

# Open spreadsheet by ID
spreadsheet = client.open_by_key(
    '1t62-kGyrF6ROgsaUd8kjGqgxaHaUABsk-XsBf6kUgW8'
)

# ==========================================
# FETCH LCP FUNCTION
# ==========================================

def fetch_lcp(url, strategy):

    print(f"\nFetching {strategy} LCP for {url}")

    api_url = (
        f'https://www.googleapis.com/pagespeedonline/v5/runPagespeed'
        f'?url={url}'
        f'&strategy={strategy}'
        f'&key={api_key}'
    )

    response = requests.get(api_url)

    print(f"Status Code: {response.status_code}")

    if response.status_code != 200:

        print(f"API Error: {response.text}")
        return None

    try:

        data = response.json()

        try:
            # FIELD DATA
            lcp_ms = data['loadingExperience']['metrics'][
                'LARGEST_CONTENTFUL_PAINT_MS'
            ]['percentile']

            print(f"{strategy} FIELD data used")

        except KeyError:
            # LAB DATA FALLBACK
            lcp_ms = data['lighthouseResult']['audits'][
                'largest-contentful-paint'
            ]['numericValue']

            print(f"{strategy} LAB data used")

        lcp_seconds = round(lcp_ms / 1000, 5)

        return lcp_seconds

    except Exception as e:

        print(f"JSON Error: {e}")
        return None


# ==========================================
# MAIN SCRIPT
# ==========================================

print("\n========== SCRIPT STARTED ==========\n")

for site_name, site_url in websites.items():

    print(f"\n========== PROCESSING {site_name} ==========")

    try:

        # ==========================================
        # OPEN OR CREATE WORKSHEET
        # ==========================================

        try:

            sheet = spreadsheet.worksheet(site_name)

            print(f"Worksheet found: {site_name}")

        except gspread.exceptions.WorksheetNotFound:

            print(f"Creating worksheet: {site_name}")

            sheet = spreadsheet.add_worksheet(
                title=site_name,
                rows="1000",
                cols="20"
            )

        # ==========================================
        # ADD HEADERS IF EMPTY
        # ==========================================

        if not sheet.get_all_values():

            print("Adding headers...")

            headers = [
                'Timestamp',
                'Mobile LCP (s)',
                'Desktop LCP (s)'
            ]

            sheet.append_row(headers)

        # ==========================================
        # FETCH LCP VALUES
        # ==========================================

        mobile_lcp = fetch_lcp(site_url, 'mobile')
        desktop_lcp = fetch_lcp(site_url, 'desktop')

        print(f"Mobile LCP: {mobile_lcp}")
        print(f"Desktop LCP: {desktop_lcp}")

        # ==========================================
        # SAVE DATA
        # ==========================================

        if mobile_lcp is not None and desktop_lcp is not None:

            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            row = [
                now,
                mobile_lcp,
                desktop_lcp
            ]

            print("Appending row to sheet...")

            sheet.append_row(row)

            print(f"{site_name} data saved successfully")

        else:

            print(f"{site_name} skipped due to missing data")

    except Exception as e:

        print(f"Error processing {site_name}: {e}")

print("\n========== SCRIPT COMPLETED ==========\n")
