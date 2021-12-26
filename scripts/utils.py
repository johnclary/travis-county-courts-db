import json
import os

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


def get_max_case_date():
    query = MAX_FILED_DATE_QUERY
    res = requests.post(
        HASURA_GRAPHQL_ENDPOINT, headers=HASURA_HEADERS, json={"query": query}
    )
    res.raise_for_status()
    data = res.json()

    validate_response(res)

    max_case_date = data["data"]["cases"][0]["filed_date"]
    return dateutil.parser.isoparse(max_case_date)


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
    except (AssertionError, json.decoder.JSONDecodeError, KeyError):
        breakpoint()
        raise ValueError(f"Upsert failed: {res.text}")


def upsert_record(record, events):
    query = UPSERT_CASE_MUTATION
    res = requests.post(
        HASURA_GRAPHQL_ENDPOINT,
        headers=HASURA_HEADERS,
        json={"query": query, "variables": record},
    )
    validate_response(res)

    for event in events:
        print(event)
        query = UPSERT_EVENT_MUTATION
        res = requests.post(
            HASURA_GRAPHQL_ENDPOINT,
            headers=HASURA_HEADERS,
            json={"query": query, "variables": event},
        )
        validate_response(res)

    return res.json()["data"]
