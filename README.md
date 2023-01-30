# Omron Sensor Daemon
Omron 2JCIE-BU Daemon for Raspberry Pi.

## Install
~~~
apt -y install git
git clone https://github.com/masayay/omron_sensor.git
cd omron_sensor
bash install.sh
~~~
Make sure connected 2JCIE-BU01 on Raspberry Pi USB correctly then reboot
~~~
reboot
~~~

## Usage
### Check CSV data & log
~~~
tail /var/lib/omron/data/`hostname`-sensor.csv
tail /var/log/omron/`hostname`-sensor.log
~~~

### start / stop service
~~~
systemctl start omron-sensor
systemctl stop omron-sensor
~~~

## Connecting with Prometheus
### prometheus-node-exporter
~~~
apt -y install prometheus-node-exporter
sed -i 's/ARGS=""/ARGS="--collector.textfile.directory \/var\/lib\/omron\/prom\/"/' /etc/default/prometheus-node-exporter
systemctl restart prometheus-node-exporter
~~~

### prometheus pushgateway
~~~
vi /var/log/omron/config.ini
~~~

~~~
# pushgateway configuration
ENABLE_PUSHGATEWAY = True
PUSHGATEWAY = X.X.X.X:9091
PUSHGATEWAY_TIMEOUT = 1
~~~

## Remove
~~~
bash install.sh remove
~~~
