#!/bin/sh
# 2 5 * * * sudo cd /home/ec2-user/travis-county-courts-db/scripts/ && ./get_data.sh
docker run -d --rm --env-file /home/ec2-user/travis-county-courts-db/scripts/env_file -v /home/ec2-user/travis-county-courts-db/scripts:/app evictions python get_new_civil_cases.py
