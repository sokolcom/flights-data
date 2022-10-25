sudo vim /etc/postgresql/13/main/pg_hba.conf

<...>
host    replication      postgres       10.0.3.0/24            md5
host    all              postgres       10.0.3.0/24            md5
<...>

###################################################################

sudo vim /etc/postgresql/13/main/postgresql.conf

<...>
listen_addresses = 'localhost, 10.0.3.1'

wal_level = hot_standby

wal_log_hints = on

max_wal_senders = 8
wal_keep_segments = 64

hot_standby = on
<...>

###################################################################

sudo service postgresql restart