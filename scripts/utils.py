from datetime import timedelta
import json
import os
import time

import dateutil.parser
import requests

from queries import MAX_FILED_DATE_QUERY, UPSERT_CASE_MUTATION, UPSERT_EVENT_MUTATION, NO_DEF_CITY_QUERY

HASURA_GRAPHQL_ADMIN_SECRET = os.getenv("HASURA_GRAPHQL_ADMIN_SECRET")
HASURA_GRAPHQL_ENDPOINT = os.getenv("HASURA_GRAPHQL_ENDPOINT")
HASURA_HEADERS = {"x-hasura-admin-secret": HASURA_GRAPHQL_ADMIN_SECRET}

KEYS = [
    {"key": "case_number", "type": "string"},
    {"key": "style", "type": "string"},
    {"key": "filed_location", "type": "string"},
    {"key": "type_status", "type": "string"},
    {"key": "case_id", "type": "number"},
    {"key": "filed_date", "type": "string"},
    {"key": "precinct", "type": "string"},
    {"key": "party_one", "type": "string"},
    {"key": "party_two", "type": "string"},
    {"key": "party_three", "type": "string"},
    {"key": "type", "type": "string"},
    {"key": "status", "type": "string"},
]

# gleaned from reviewing data
CASE_TYPES = [
    "Administrative Case",
    "AG Parent Child Relationship",
    "AG Paternity",
    "Bond Forfeiture",
    "Debt Claim",
    "Eviction Diversion",
    "Eviction",
    "Expunction(s)",
    "EXPUNCTION",
    "Forcible Entry and Detainer",
    "Garnishment",
    "Illegal Tow",
    "Justice Court (Non-FED)",
    "Non Disclosure",
    "Occupational Driver's License",
    "Occupational Drivers License",
    "OTHER",
    "Order of Retrieval",
    "Peace Bond",
    "Protective Order",
    "Repair and Remedy",
    "Small Claims",
    "Special District Cases",
    "Tax Cases",
    "Toll Habitual Violator",
    "Truant Conduct 17+",
    "Writ of Re-Entry",
    "Writ of Restoration of Utilities",
]


def make_obj(obj):
    for k in ["style", "party_one", "party_two", "party_three"]:
        if '"' in obj[k]:
            obj[k] = obj[k].replace('"', '\\"')
        if "\n" in obj[k]:
            obj[k] = obj[k].replace("\n", " ")
        if "\\" in obj[k]:
            obj[k] = obj[k].replace("\\", "\\\\")
    entries = [f"""{key}: \"{value}\"""" for key, value in obj.items()]
    return f"{{ {','.join(entries)} }}"


def get_max_case_date(minus_days=14):
    query = MAX_FILED_DATE_QUERY
    res = requests.post(
        HASURA_GRAPHQL_ENDPOINT, headers=HASURA_HEADERS, json={"query": query}
    )
    res.raise_for_status()
    data = res.json()
    validate_response(res)
    max_case_date_str = data["data"]["cases_civil"][0]["filed_date"]
    max_case_date = dateutil.parser.isoparse(max_case_date_str)
    return max_case_date - timedelta(days=minus_days)


def get_records_missing_def(start_date_str):
    query = NO_DEF_CITY_QUERY
    res = requests.post(
        HASURA_GRAPHQL_ENDPOINT, headers=HASURA_HEADERS, json={"query": query, "variables": {"filed_date": start_date_str}}
    )
    res.raise_for_status()
    data = res.json()
    validate_response(res)
    return data["data"]["cases"]


def validate_response(res):
    res.raise_for_status()
    try:
        assert res.json()["data"]
    except KeyError:
        msg = res.json()["errors"][0]["message"]
        if "limit" in msg:
            return False
        else:
            raise ValueError(f"Upsert failed: {res.text}")    
    except (AssertionError, json.decoder.JSONDecodeError):
        raise ValueError(f"Upsert failed: {res.text}")
    return True


def upsert_record(record, events):
    query = UPSERT_CASE_MUTATION
    
    success = False
    while not success:
        res = requests.post(
            HASURA_GRAPHQL_ENDPOINT,
            headers=HASURA_HEADERS,
            json={"query": query, "variables": record},
        )
        success = validate_response(res)
        if not success:
            print("sleeping for rate limit...")
            time.sleep(1)

    for event in events:
        success = False
        while not success:
            print(event)
            query = UPSERT_EVENT_MUTATION
            res = requests.post(
                HASURA_GRAPHQL_ENDPOINT,
                headers=HASURA_HEADERS,
                json={"query": query, "variables": event},
            )
            success = validate_response(res)
            if not success:
                print("sleeping for rate limit...")
                time.sleep(1)

    return res.json()["data"]
