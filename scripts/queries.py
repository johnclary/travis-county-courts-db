MAX_FILED_DATE_QUERY = """
    query MaxFiledDate {
    cases(order_by: {filed_date: desc}, limit: 1) {
        filed_date
    }
}
"""

UPSERT_CASE_MUTATION = """
mutation UpsertCase(
    $case_id: numeric!
    $case_number: String!
    $filed_date: timestamp!
    $party_one: String!
    $party_three: String!
    $party_two: String!
    $precinct: String!
    $status: String!
    $style: String!
    $type: String!
    $plaintiff_city: String = ""
    $plaintiff_state: String = ""
    $plaintiff_zip: String = ""
    $defendant_city: String = ""
    $defendant_state: String = ""
    $defendant_zip: String = ""
  ) {
    insert_cases_civil(
      objects: {
        case_id: $case_id
        case_number: $case_number
        filed_date: $filed_date
        party_one: $party_one
        party_three: $party_three
        party_two: $party_two
        precinct: $precinct
        style: $style
        type: $type
        status: $status
        plaintiff_city: $plaintiff_city
        plaintiff_state: $plaintiff_state
        plaintiff_zip: $plaintiff_zip
        defendant_city: $defendant_city
        defendant_state: $defendant_state
        defendant_zip: $defendant_zip
      }
      on_conflict: { constraint: cases_pkey, update_columns: [status, plaintiff_city, plaintiff_state, plaintiff_zip, defendant_city, defendant_state, defendant_zip]}
    ) {
      returning {
        case_id
      }
    }
  }
"""

UPSERT_EVENT_MUTATION = """
  mutation UpsertEvent(
    $event_id: String!
    $case_id: Int!
    $date: timestamptz!
    $event_sequence: Int!
    $id: String!
    $name: String!
  ) {
    insert_events_one(
      object: {
        case_id: $case_id
        date: $date
        event_id: $event_id
        event_sequence: $event_sequence
        id: $id
        name: $name
      }
      on_conflict: { constraint: events_pkey, update_columns: [date, event_sequence, name] }
    ) {
      id
    }
  }
"""

NO_DEF_CITY_QUERY = """
  query MyQuery($filed_date: timestamp!) {
    cases(
      where: {
        defendant_city: { _is_null: true }
        _and: {
          filed_date: { _gte: $filed_date }
          _and: { type: { _ilike: "eviction" } }
        }
      }
      order_by: { filed_date: asc }
    ) {
      case_number
    }
  }
"""
