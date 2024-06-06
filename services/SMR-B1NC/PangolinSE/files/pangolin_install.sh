#!/bin/sh
if [ ! -d /pgdata ]; then
    
    #create user
    echo "CREATE USER..."
    useradd postgres
    echo "$POSTGRES_PASSWD" | passwd postgres --stdin

    #create directory
    echo "CREATE DIR..."
    mkdir distrib

    #copy distributive
    echo "CP DISTRIB..."
    cp CI04742057-D-06.001.04-12_sl8_r1_31_0_2-distrib.tar.gz ./distrib

    #untar
    echo "UNPACK tar..."
    cd distrib/
    tar -xvf CI04742057-D-06.001.04-12_sl8_r1_31_0_2-distrib.tar.gz

    #install rpm
    echo ""
    echo "INSTALL rpm..."
    yum -v -y install platform-v-pangolin-dbms-06.001.04-sberlinux8.8.x86_64.rpm
    rm CI04742057-D-06.001.04-12_sl8_r1_31_0_2-distrib.tar.gz

    #create directory for pangolin
    echo ""
    echo "Starting create directory..."
    mkdir -p /pgdata/06/data
    chown -R postgres:postgres /pgdata/06/data
    mkdir -p /pgerrorlogs/06
    chown -R postgres:postgres /pgerrorlogs/06

    #install postgres-server
    # echo ""
    # echo "Install Packages..."
    
    #cahnge user
    echo ""
    echo "Delete files..."    
    cd ../
    # cp ./change.sh /home/postgres
    # cp ./export.sh /home/postgres
    # cp ./start.sh /home/postgres
    # su -s /bin/bash - postgres -c './export.sh'
    rm ./CI04742057-D-06.001.04-12_sl8_r1_31_0_2-distrib.tar.gz
else
    echo "Pangolin SE installed"
fi

echo "END"

