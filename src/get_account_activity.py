import os, json, pathlib
from datetime import datetime
import requests
from zoneinfo import ZoneInfo

'''

Description:
    this script gets account activity (such as trades, margin fees, pass through fees (aka margin lender interest), regulatory fees, and all other types of account activity).

Sources:
    Get Account Activities of Multiple Types: https://docs.alpaca.markets/reference/getaccountactivities-2
    Get Account Activities of One Type: https://docs.alpaca.markets/reference/getaccountactivitiesbyactivitytype-1
        according to the "response" > "ACCOUNTNONTRADINGACTIVITIES" section:
        "symbol: The symbol of the security involved with the activity. Not present for all activity types."
    Account Activities: https://docs.alpaca.markets/docs/account-activities
    this link shows "symbol" as a field too
    https://alpaca.markets/sdks/python/api_reference/trading/enums.html#activitytype
    NOTE: for unknown reasons getting account activities is not part of alpaca-py lib
    https://alpaca-community.slack.com/archives/CEL9HCSN4/p1715635459217939?thread_ts=1708544979.396449&cid=CEL9HCSN4
        i think he meant to say "isn't", not "is"
    TODO: if you want you could also use this "lower level client.get method to implement it"
    https://alpaca-community.slack.com/archives/CEL9HCSN4/p1715635459217939?thread_ts=1708544979.396449&cid=CEL9HCSN4
    https://github.com/alpacahq/alpaca-py/blob/d60770670e042cad260cdc745a16a912ecc46fc3/alpaca/common/rest.py#L210

'''

REPO_PATH = str(pathlib.Path(__file__).resolve().parent.parent.parent)
LIVE_TRADING = False
CREDENTIALS_FILEPATH = os.path.join(
    str(pathlib.Path(REPO_PATH).resolve().parent),
    "alpaca", "alpaca-algo-trading-utils", "src", "credentials.json") # shared partition
with open(CREDENTIALS_FILEPATH) as f:
    creds = json.load(f)
    ENDPOINT   = creds['live_trading' if LIVE_TRADING else 'paper_trading']['ENDPOINT']
    API_KEY    = creds['live_trading' if LIVE_TRADING else 'paper_trading']['API_KEY_ID']
    API_SECRET = creds['live_trading' if LIVE_TRADING else 'paper_trading']['SECRET_KEY']
HEADERS = {
    "accept": "application/json",
    "APCA-API-KEY-ID": API_KEY,
    "APCA-API-SECRET-KEY": API_SECRET,
}
TIMEZONE = 'US/Eastern' # 'US/Pacific' # 'UTC'

url = f"{ENDPOINT}/v2/account/activities"
# url = f"{ENDPOINT}/v2/account/activities?activity_types=FEE%2CINT%2CPTC%2CPTR?after=2024-02-26T00%3A00%3A00" # specify a list of activity types to filter by
# url = f"{ENDPOINT}/v2/account/activities/after=2024-02-26T00%3A00%3A00"
params = {
    'activity_types': ['FEE', 'INT', 'PTC', 'PTR'],
    'after': datetime(2024, 2, 26, tzinfo=ZoneInfo(TIMEZONE)).isoformat(),
}
# error w/ datetime iso format: https://forum.alpaca.markets/t/what-is-the-correct-after-input-for-getorders/12021/2
# resolved w/ specifying timezone

response = requests.get(url, headers=HEADERS, params=params)
# print(response.text)
activities = json.loads(response.text)
print(f'\n{len(activities)} activit{"y" if len(activities) == 1 else "ies"} found:\n')
for activity in activities:
    print(json.dumps(activity, indent=4))


