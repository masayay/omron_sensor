# OMRON 2JCIE-BU Systemd Service
* Reading sensing data from serial communication (USB port) and writing data on csv file.
* Export sensing data to prometheus-node-exporter/pushgateway.
* Register as systemd service

## Install
~~~
apt -y install git
git clone https://github.com/masayay/omron_sensor.git
cd omron_sensor
sudo bash install.sh
~~~
**Connect 2JCIE-BU on USB port correctly then reboot**
~~~
reboot
~~~

## Usage
### Check CSV data & log
~~~
tail -f /var/lib/omron/data/`hostname`-sensor.csv
tail -f /var/log/omron/`hostname`-sensor.log
~~~

### CSV OUTPUT
~~~
Time measured,Temperature,Relative humidity,Ambient light,Barometric pressure,Sound noise,eTVOC,eCO2,Discomfort index,Heat stroke,Vibration information,SI value,PGA,Seismic intensity
2023/01/30 14:55:06,24.92,34.69,572,998.887,67.68,3,420,70.08,19.1,2,152.3,1002.0,6.708
2023/01/30 14:55:07,24.89,34.77,572,998.881,67.54,3,420,70.05,19.1,2,152.3,1002.0,6.708
2023/01/30 14:55:08,24.84,34.85,756,998.877,67.66,2,415,70.0,19.06,2,152.3,1002.0,6.708
2023/01/30 14:55:09,24.81,34.89,756,998.876,67.2,2,415,69.97,19.03,2,152.3,1002.0,6.708
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
cd omron_sensor
bash install.sh remove
~~~

## Troubleshooting
Source was tested on "Raspberry Pi 4 Model B (Debian version 11 installed). User "omron" need to access 2JCIE-BU serial port "/dev/ttyUSBX". Check "group" of serial port and add user "omron" to that group.
~~~
1) Check group
ls -l /dev/ttyUSB0 |awk '{print $4}'
##GROUP_NAME##

2) Add omron on group
gpasswd -a omron ##GROUP_NAME##
~~~
