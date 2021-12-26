
-- group by status
select filed_date, status, count(status) from cases where type = 'Eviction' and filed_date > '2021-10-01' group by filed_date, status order by filed_date desc;

-- recent evictions
select filed_date, case_number, party_one, party_two from cases where type = 'Eviction' order by filed_date desc limit 800;

-- count of cases by party
select EXTRACT(year from filed_date) || '-'|| EXTRACT(month from filed_date) as year, party_one, count(case_number) from cases where type = 'Eviction' and EXTRACT(year from filed_date) > 2020 group by year, party_one order by count desc;

-- cumulative totals
SELECT filed_date, precinct, count(case_number) 
    OVER (PARTITION BY precinct
                         ORDER BY filed_date) AS cum_amt
FROM   cases where type = 'Eviction' and filed_date > '2020-12-31'
ORDER  BY cum_amt desc;