create table _log_scraper_search (
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    search_payload jsonb not null,
    search_date_str text not null,
    search_prefix text not null,
    search_url text not null,
    case_type text not null,
    state text not null,
    county text not null,
    url text not null,
    record_count integer not null
);

alter table _log_scraper_search add primary key (search_date_str, search_prefix, case_type, state, county);

alter table _log_scraper_search drop column url;

alter table "public"."_log_scraper_search" add column "id" serial
 not null unique;

CREATE TRIGGER set_search_log_last_updated BEFORE UPDATE ON public._log_scraper_search FOR EACH ROW EXECUTE FUNCTION public.set_last_updated();

alter table _log_scraper_search add column search_date timestamp without time zone not null;

alter table "public"."_log_scraper_search" add column "file_path" text
 not null;
