#!/usr/bin/bash

INSTALL_DIR=/var/lib/omron
LOG_DIR=/var/log/omron

## Step1: Install required packages
apt -y install python3
apt -y install pip
pip install -r requirements.txt

# Step2: Add 2jcie-bu01-usb rules
cat<<EOF> /etc/udev/rules.d/80-2jcie-bu01-usb.rules
ACTION=="add", ATTRS{idVendor}=="0590", ATTRS{idProduct}=="00d4", RUN+="/sbin/modprobe ftdi_sio" RUN+="/bin/sh -c 'echo 0590 00d4 > /sys/bus/usb-serial/drivers/ftdi_sio/new_id'", SYMLINK+="2JCIE-BU"
EOF

# Step3: Prepare User
mkdir -p ${INSTALL_DIR}/data ${INSTALL_DIR}/prom ${LOG_DIR}
groupadd -r omron
useradd -g omron -s /usr/sbin/nologin -d ${INSTALL_DIR} -r omron
gpasswd -a omron dialout  ## Require to access /dev/ttyUSBX

# Step4: Install pkg
cp omron_sensor.py omron_sensor_util.py ${INSTALL_DIR}
cp config-sample.ini ${INSTALL_DIR}/config.ini
chmod 755 ${INSTALL_DIR}/omron_sensor.py
chown -R omron:omron ${INSTALL_DIR} ${LOG_DIR}

# Step5: Start omron-sensor.service
cp omron-sensor.service /etc/systemd/system/omron-sensor.service
systemctl daemon-reload
systemctl enable omron-sensor

# Step5: Logrotate
cat<<EOF> /etc/logrotate.d/omron
/var/log/omron/*.log
/var/lib/omron/data/*.csv
{
	missingok
	rotate 90
	dateext
	compress
	delaycompress
	daily
	notifempty
	create 0640 omron omron
	sharedscripts
	copytruncate
}
EOF
