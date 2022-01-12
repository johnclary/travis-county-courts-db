CREATE
OR REPLACE VIEW "public"."evic_by_date" AS
SELECT
  cases.filed_date,
  count(cases.case_id) AS count
FROM
  cases
WHERE
  (cases.type = 'Eviction' :: text)
GROUP BY
  cases.filed_date
ORDER BY
  cases.filed_date DESC;
