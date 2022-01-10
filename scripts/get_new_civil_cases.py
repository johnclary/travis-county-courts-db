import argparse
from datetime import datetime, timedelta
import logging
import time
import sys

from bs4 import BeautifulSoup
import dateutil.parser
import requests

from utils import get_max_case_date, upsert_record, CASE_TYPES
from utils_details import parse_details

# URLs and such
LOGIN_BASE_URL = "https://odysseypa.traviscountytx.gov/JPPublicAccess/Login.aspx?ReturnUrl=%2fJPPublicAccess%2fSearch.aspx%3fID%3d100&ID="
SEARCH_BASE_URL = "https://odysseypa.traviscountytx.gov/JPPublicAccess/Search.aspx?ID="
CASE_DETAIL_URL = "https://odysseypa.traviscountytx.gov/JPPublicAccess/CaseDetail.aspx"
SEARCH_TYPE_IDS = {
    "civil": 200,
}
# app state validators hidden in <input> ID props on search page - must be passed in search payload
SESSION_DATA_KEYS = ["__VIEWSTATE", "__VIEWSTATEGENERATOR", "__EVENTVALIDATION"]
# Settings
SLEEP_SECONDS = 0.1
SEARCH_RESULTS_TABLE_NUMBER = 5
# column names, in order, expected from search results table
FIELDNAMES = [
    "case_number",
    "style",
    "filed_location",
    "type_status",
    "case_id",
]


def login(session, search_id):
    """Initiate a session and save session cookies by "logging in".

    This request happens automatically when you navigate to the search page via UI.

    Args:
        session (requests.Session): A requests sesssion instance
        search_id (int): The search ID (100 or 200)

    Returns:
        requests.Response: A response object, plus session is updated in-place w/
            cookies.
    """
    url = f"{LOGIN_BASE_URL}{search_id}"
    return session.get(url)


def init_search(session, search_id):
    """Initiate a search session.

    Equivalent to navigating to the search page in the UI.

    Args:
        session (requests.Session): A requests sesssion instance
        search_id (int): The search ID (100 or 200)

    Returns:
        str: The search page HTML, plus session is updated in-place w/ cookies.
    """
    url = f"{SEARCH_BASE_URL}{search_id}"
    res = session.get(url)
    return res.text


def parse_session_data(html):
    """Extract .net view state controller data which we need for the search post request.

    Args:
        html (str): the raw html of the record search page

    Raises:
        ValueError: if one of the expected hidden elements iss missing.

    Returns:
        dict: with the values of interest
    """
    soup = BeautifulSoup(html, "html.parser")
    session_data = {}
    for i in SESSION_DATA_KEYS:
        el = soup.find("input", {"id": i})
        if not el:
            raise ValueError(f"Unabled to find <input> with ID: {i}")
        session_data[i] = el.get("value")
    return session_data


def format_search_payload(d, prefix, session_data):
    payload = {
        "NodeID": "100,110,200,210,300,310,320,330,340,350,1100,1200,1300,1310,1320,1330,1340,1350,2100,2200,2300,2310,2320,2330,2340,2350",
        "NodeDesc": "All Courts",
        "SearchBy": "0",
        "ExactName": "on",
        "CaseSearchMode": "CaseNumber",
        "CaseSearchValue": f"{prefix}*",
        "DateFiledOnAfter": d,
        "DateFiledOnBefore": d,
        "SortBy": "casenumber",
        "SearchSubmit": "Search",
        "SearchType": "CASE",
        "SearchMode": "CASENUMBER",
        "StatusType": "true",
        "AllStatusTypes": "true",
        "RequireFirstName": "False",
    }
    payload.update(session_data)
    return payload


def fetch_records(session, search_id, payload):
    """POST a record query.

    Args:
        session (requests.Session): A requests sesssion instance
        search_id (int): The search ID (100 or 200)
        payload (dict): The request payload

    Returns:
        requests.Response: The response data
    """
    res = session.post(SEARCH_BASE_URL, data=payload)
    res.raise_for_status()
    return res


def fetch_details(session, case_id):
    res = session.post(CASE_DETAIL_URL, params={"CaseID": case_id})
    res.raise_for_status()
    return res.text


def parse_results_html(html):
    """Parse search HTML into dicts

    Args:
        html (str): HTML returned from case search

    Returns:
        list: A list of case record dicts
    """
    records = []
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")
    table = tables[SEARCH_RESULTS_TABLE_NUMBER]
    for row in table.find_all("tr"):
        cols = row.find_all("td")
        # ignore some <tr> that are actually headers
        if len(cols) <= 1:
            continue
        # extract case id from <a> tag value in first column
        # e.g.  "CaseDetail.aspx?CaseID=898087"
        case_meta = cols[0].find("a").get("href")
        case_id = int(case_meta.split("=")[1])
        col_values = [ele.text.strip() for ele in cols]
        # the charges value is a nested table, with only one row
        # the value is duplicated, leaving an extra column
        col_values = col_values[0:6]
        col_values.append(case_id)
        row_dict = dict(zip(FIELDNAMES, col_values))
        records.append(row_dict)
    return records


def get_logger():
    """Return a module logger that streams to stdout and to rotating file"""
    logger = logging.getLogger(__name__)
    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s: %(message)s")
    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


def get_dates(start_date, end_date):
    """Generate a list of dates to be fetched.
    Args:
        start_date (datetime.datetime): the oldest case filed date to be queried
        end_date (datetime.datetime): the newest case filed date to be queried
    Returns:
      list: of dates one day before the max case date and to present
    """
    # subtract one from the max case date so as to include in the date range
    # just being greedy / safe
    start_date = start_date - timedelta(days=1)
    delta = end_date - start_date
    if delta.days <= 0:
        return []
    # create a range of dates (add one to delta to make inclusive of end date)
    all_dates = [start_date + timedelta(days=x) for x in range(delta.days + 1)]
    # format datestrings for API query
    return [dt.strftime("%m/%d/%Y") for dt in all_dates]


def format_iso_date(dt_string):
    # parsse format from mm/dd/yyyy
    month, day, year = dt_string.split("/")
    dt = datetime(year=int(year), month=int(month), day=int(day))
    return dt.isoformat()


def format_record(record):
    # parse date and precinct
    record["filed_date"] = format_iso_date(record["filed_location"][:10])
    record["precinct"] = record["filed_location"][10:]
    # split out parties
    parties = record["style"].split("vs.")
    record["party_one"] = parties[0].strip()
    record["party_two"] = None
    record["party_three"] = None
    if len(parties) > 1:
        record["party_two"] = parties[1].strip()
    if len(parties) == 3:
        record["party_three"] = parties[2].strip()
    elif len(parties) > 3:
        record["party_three"] = ",".join(parties[2:])
    case_type_status = record["type_status"]
    # format type/status
    record["type"] = None
    record["status"] = None
    for t in CASE_TYPES:
        if case_type_status.startswith(t):
            record["type"] = t
            record["status"] = case_type_status.replace(t, "")
            break
    record.pop("filed_location")
    record.pop("type_status")
    return record


def main(start_date_str, end_date_str):
    end_date = dateutil.parser.parse(end_date_str)

    if start_date_str:
        start_date = dateutil.parser.parse(start_date_str)
    else:
        start_date = get_max_case_date()
    dates_todo = get_dates(start_date, end_date)
    if not dates_todo:
        logger.error("No dates to search")
        return

    search_id = SEARCH_TYPE_IDS["civil"]
    session = requests.Session()
    res = login(session, search_id)
    res.raise_for_status()
    search_html = init_search(session, search_id)
    session_data = parse_session_data(search_html)
    for d in dates_todo:
        prefix = ""
        payload = format_search_payload(d, prefix, session_data)
        logger.info(f"Getting *{d}")
        res = fetch_records(session, search_id, payload)
        records = parse_results_html(res.text)
        if records:
            if len(records) > 199:
                records = []
                # max search results is 200. our search results may be incomplete
                logger.info("too many results - using prefix")
                for prefix in [
                    "UNA",
                    "PB1",
                    "J5",
                    "J4",
                    "MOD",
                    "D",
                    "J3",
                    "C",
                    "JP",
                    "J1",
                    "PR",
                    "J2",
                    "D",
                    "DL",
                ]:
                    payload = format_search_payload(d, prefix, session_data)
                    logger.info(f"Getting {prefix}{d}")
                    res = fetch_records(session, search_id, payload)
                    record_subset = parse_results_html(res.text)
                    if record_subset:
                        records.extend(record_subset)
                    else:
                        logger.info(f"no records found for prefix {prefix}")
            else:
                logger.info(f"{len(records)} records")

        for record in records:
            record = format_record(record)
            case_id = record["case_id"]
            logger.info(f"Gettings details for {record['case_number']} - {case_id}")
            time.sleep(SLEEP_SECONDS)
            details_html = fetch_details(session, case_id)
            party_info, events = parse_details(details_html, case_id)
            record.update(party_info)
            upsert_record(record, events)
            logger.info(f"Upserted {case_id}")
            time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    logger = get_logger()
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s",
        "--start",
        type=str,
        required=False,
        help=f"The start date in format yyyy-mm-dd. Defaults to max case date in DB minus one day",
    )
    parser.add_argument(
        "-e",
        "--end",
        type=str,
        required=False,
        default=datetime.today().isoformat(),
        help=f"The end date in format yyyy-mm-dd. Defaults to today",
    )
    args = parser.parse_args()
    main(args.start, args.end)
