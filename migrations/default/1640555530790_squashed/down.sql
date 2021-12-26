

alter table "public"."events" rename column "id" to "id_text";

alter table "public"."events" alter column "id" set default nextval('events_id_seq'::regclass);
alter table "public"."events" alter column "id" drop not null;
alter table "public"."events" add column "id" int4;

alter table "public"."events" drop constraint "events_pkey";
alter table "public"."events"
    add constraint "events_pkey"
    primary key ("id");

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- alter table "public"."events" add column "id_text" text
--  not null;

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- alter table "public"."events" add column "event_sequence" integer
--  null;

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- alter table "public"."cases" add column "plaintiff_zip" text
--  null;

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- alter table "public"."cases" add column "plaintiff_state" text
--  null;

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- alter table "public"."cases" add column "plaintiff_city" text
--  null;

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- alter table "public"."cases" add column "defendant_zip" text
--  null;

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- alter table "public"."cases" add column "defendant_state" text
--  null;

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- alter table "public"."cases" add column "defendant_city" text
--  null;

alter table "public"."events" drop constraint "events_case_id_fkey";

-- Could not auto-generate a down migration.
-- Please write an appropriate down migration for the SQL below:
-- alter table "public"."events" add column "case_id" integer
--  not null;

DROP TABLE "public"."events";
