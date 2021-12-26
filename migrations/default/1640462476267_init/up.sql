SET check_function_bodies = false;
CREATE FUNCTION public.set_last_updated() RETURNS trigger
    LANGUAGE plpgsql
    AS $$ BEGIN NEW.updated_at := NOW();
RETURN NEW;
END;
$$;
CREATE TABLE public.cases (
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    case_id numeric NOT NULL,
    case_number text,
    precinct text,
    status text,
    type text,
    style text,
    filed_date timestamp without time zone,
    party_one text,
    party_two text,
    party_three text
);
CREATE VIEW public.evic_by_date AS
 SELECT cases.filed_date,
    cases.precinct,
    count(cases.case_id) AS count
   FROM public.cases
  WHERE (cases.type = 'Eviction'::text)
  GROUP BY cases.precinct, cases.filed_date
  ORDER BY cases.filed_date DESC;
ALTER TABLE ONLY public.cases
    ADD CONSTRAINT cases_pkey PRIMARY KEY (case_id);
CREATE INDEX cases_filed_date_idx ON public.cases USING btree (filed_date);
CREATE TRIGGER set_case_last_updated BEFORE INSERT OR UPDATE ON public.cases FOR EACH ROW EXECUTE FUNCTION public.set_last_updated();
