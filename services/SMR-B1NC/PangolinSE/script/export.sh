#!/bin/bash

#export env
export LD_LIBRARY_PATH=/usr/pangolin-6.1.4/lib 
export PG_PLUGINS_PATH=/usr/pangolin-6.1.4/lib 
export PGHOME=/usr/pangolin-6.1.4 
export PGDATABASE=postgres 
export PGUSER=postgres 
export PGHOST=127.0.0.1
export PGPORT=5433 
export PGCLIENTENCODING=UTF8 
export PGDATA=/pgdata/06/data 
export PATH=$PATH:/usr/pangolin-6.1.4/bin 
export MANPATH=$MANPATH:/usr/pangolin-6.1.4/share/man 
export PG_LICENSE_PATH=/pangolin/distrib/additional_files/

if [ "$(ls -A /pgdata/06/data/ 2> /dev/null)" == "" ]; then
    # The directory is empty
    echo ""
    echo "INITDB..."
    initdb -k -D /pgdata/06/data/ 

    #Set password AUTH
    echo ""
    echo "CHANGE CONFIG..."
    ./change.sh

    #START pangolin
    echo ""
    echo "START Pangolin SE..."
    pg_ctl -D /pgdata/06/data/ -l /pgerrorlogs/06/postgresql.log start
    psql -p 5433 -c "ALTER USER postgres PASSWORD 'secret'"
    psql -p 5433 -c "CREATE DATABASE smartbalance"
    pg_ctl stop

    #change auth_method
    sed -i 's/trust/scram-sha-256/g' $PGDATA/pg_hba.conf
    sed -i 's/127.0.0.1\/32/172.26.0.0\/29/g' $PGDATA/pg_hba.conf
    # sed -i 's/127.0.0.1\/32/all/g' $PGDATA/pg_hba.conf
    echo ""
    echo "Try to start Pangolin SE..."
    pg_ctl -D /pgdata/06/data/ -l /pgerrorlogs/06/postgresql.log start
else
    #Final launch
    echo ""
    echo "PangolinSE started..."
    pg_ctl -D /pgdata/06/data/ -l /pgerrorlogs/06/postgresql.log start
fi


