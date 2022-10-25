sudo service postgresql stop
sudo -u postgres

cd /var/lib/postgresql/13/
tar -cvzf main_backup-`date +%s`.tgz main
rm -rf main
mkdir main
chmod go-rwx main
pg_basebackup -P -R -X stream -c fast -h 10.0.3.1 -U postgres -D ./main

###################################################################

sudo vim /etc/postgresql/13/main/postgresql.conf

<...>
recovery_target_timeline = 'latest'

recovery_min_apply_delay = 10min
<...>

###################################################################

sudo service postgresql start