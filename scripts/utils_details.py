from datetime import datetime
from unicodedata import normalize

from bs4 import BeautifulSoup

PARTY_IDS = {"defendant": "PIr11", "plaintiff": "PIr12"}


def decruft(text):
    # see: https://stackoverflow.com/questions/10993612/how-to-remove-xa0-from-string-in-python
    nocruft = normalize("NFKD", text)
    nocruft = nocruft.replace("\n", "")
    return nocruft.strip()


def format_party_info(city, state, zip, kind):
    return {f"{kind}_city": city, f"{kind}_state": state, f"{kind}_zip": zip}


def parse_city_zip(text):
    print(f"PARSING: {text}")
    city, state, zip = [None, None, None]
    if text:
        # i've seen dupe commas in here...hmm
        text = text.replace(",,", ",")
        stuff = text.split(",")
        # handle city
        city = stuff[0]
        if len(stuff) == 1:
            # hmmmm...? leave state and zip blank
            return city, state, zip
        if len(stuff) > 2:
            # merge whatever gunk is here into city
            city = ",".join(stuff[0:-1])
        # handle state/zip
        try:
            state, zip = stuff[-1].strip().split(" ")
        except ValueError:
            # rarely but sometimes zipcode is missing
            # so cram this into state i guess :/ 
            state = stuff[-1]
    return city, state, zip


def get_party_info(soup, kind):
    el_id = PARTY_IDS[kind]
    el_th = soup.find("th", id=el_id)
    if el_th:
        city_zip_raw = el_th.parent.findNext("tr").text
        city_zip = decruft(city_zip_raw)
        city, state, zip = parse_city_zip(city_zip)
    else:
        city, state, zip = ["", "", ""]
    return format_party_info(city, state, zip, kind)


def has_event_id(tag):
    return tag.has_attr("id") and "RCDER" in tag.attrs["id"]


def has_event_header(tag):
    return tag.has_attr("headers") and any(
        ["COtherEventsAndHearings" in header for header in tag.attrs["headers"]]
    )


def format_iso_date(dt_string):
    # parsse format from mm/dd/yyyy
    month, day, year = dt_string.split("/")
    dt = datetime(year=int(year), month=int(month), day=int(day))
    return dt.isoformat()


def get_events(soup, case_id):
    events = []
    event_headers = soup.find_all(has_event_id)
    for i, th in enumerate(event_headers):
        event_id = th.attrs["id"]
        event_date = format_iso_date(th.text)
        parent = th.parent
        event_name_td = parent.find(has_event_header)
        event_name = event_name_td.text
        event_name = event_name.replace("\n", "")
        # we include our `i` value to make it easy to preserve the sequence, since event dates may be the same
        # we could parse the event_id to do this but this should make life asier
        events.append(
            {
                "id": f"{case_id}_{event_id}",
                "case_id": case_id,
                "event_sequence": i,
                "event_id": event_id,
                "date": event_date,
                "name": event_name,
            }
        )
    return events


def parse_details(html, case_id):
    soup = BeautifulSoup(html, "html.parser")
    party_info = get_party_info(soup, "defendant")
    plaintif_info = get_party_info(soup, "plaintiff")
    party_info.update(plaintif_info)
    events = get_events(soup, case_id)
    return party_info, events
