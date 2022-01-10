create or replace view evict_by_plaintiff as (select party_one, count(party_one) as count, filed_date from cases where type = 'Eviction'  group by party_one, filed_date order by filed_date desc);
