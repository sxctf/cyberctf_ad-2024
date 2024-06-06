#!/bin/bash

sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" $PGDATA/postgresql.conf
# sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '172.26.0.2'/g" $PGDATA/postgresql.conf
sed -i "s/#port = 5432/port = 5433/g" $PGDATA/postgresql.conf   
sed -i "s/_auth_methods = ''/_auth_methods = 'peer, trust'/" $PGDATA/postgresql.conf
sed -i "s/sec_admin_default_auth/#sec_admin_default_auth/" $PGDATA/postgresql.conf
