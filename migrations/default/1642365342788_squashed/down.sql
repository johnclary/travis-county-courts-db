
-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- ALTER TABLE cases drop column path_search_html;
-- ALTER TABLE cases drop column path_detail_html;
-- ALTER TABLE cases drop column search_retrieved_at;
-- ALTER TABLE cases drop column detail_retrieved_at;

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- alter table "public"."_log_scraper_search" add column "file_path" text
--  not null;

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- alter table _log_scraper_search add column search_date timestamp without time zone not null;

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- CREATE TRIGGER set_search_log_last_updated BEFORE UPDATE ON public._log_scraper_search FOR EACH ROW EXECUTE FUNCTION public.set_last_updated();

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- alter table "public"."_log_scraper_search" add column "id" serial
--  not null unique;

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- alter table _log_scraper_search drop column url;

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- alter table _log_scraper_search add primary key (search_date_str, search_prefix, case_type, state, county);

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- create table _log_scraper_search (
--     created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
--     updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
--     search_payload jsonb not null,
--     search_date_str text not null,
--     search_prefix text not null,
--     search_url text not null,
--     case_type text not null,
--     state text not null,
--     county text not null,
--     url text not null,
--     record_count integer not null
-- );

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- ALTER TABLE cases add column path_search_html text;
-- ALTER TABLE cases add column path_detail_html text;
-- ALTER TABLE cases add column search_retrieved_at timestamp without time zone;
-- ALTER TABLE cases add column detail_retrieved_at timestamp without time zone;
