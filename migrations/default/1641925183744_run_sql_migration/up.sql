create or replace view evic_by_status_by_day as (select filed_date, status, count(status) as count from cases where type = 'Eviction' group by filed_date, status order by filed_date desc);
