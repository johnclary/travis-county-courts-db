CREATE TABLE public.cases_criminal (
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    case_id numeric NOT NULL,
    citation_number text NOT NULL,
    precinct text NOT NULL,
    status text NOT NULL,
    charges text NOT NULL,
    filed_date timestamp without time zone,
    jurisdiction_county text NOT NULL,
    jurisdiction_state text NOT NULL,
    case_type text NOT NULL,
    primary key(case_id, jurisdiction_county, jurisdiction_state)
);
