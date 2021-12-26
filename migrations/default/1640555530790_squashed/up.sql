
CREATE TABLE "public"."events" ("id" text NOT NULL, "event_id" text NOT NULL, "name" text NOT NULL, "date" timestamptz NOT NULL, PRIMARY KEY ("id") );


alter table "public"."events" add column "case_id" integer
 not null;

alter table "public"."events"
  add constraint "events_case_id_fkey"
  foreign key ("case_id")
  references "public"."cases"
  ("case_id") on update restrict on delete restrict;

alter table "public"."cases" add column "defendant_city" text
 null;

alter table "public"."cases" add column "defendant_state" text
 null;

alter table "public"."cases" add column "defendant_zip" text
 null;

alter table "public"."cases" add column "plaintiff_city" text
 null;

alter table "public"."cases" add column "plaintiff_state" text
 null;

alter table "public"."cases" add column "plaintiff_zip" text
 null;

alter table "public"."events" add column "event_sequence" integer
 null;

