docker run -v /home/ec2-user:/tmp -it --rm  --network host postgres:12 psql postgres://postgres:postgrespassword@localhost:5432/postgres -c "\copy (SELECT _id, filed_date, status, party_one as plaintiff, plaintiff_city, plaintiff_state, plaintiff_zip, defendant_city, defendant_state, defendant_zip FROM cases where type='Eviction' order by filed_date desc) to '/tmp/evictions.csv' with csv header"
aws s3api put-object --bucket travis-county-evictions --key evictions.csv --body /home/ec2-user/evictions.csv
