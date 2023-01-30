#!/usr/bin/python3
import configparser, serial, sys, time, os, signal, sdnotify
from logging import getLogger, FileHandler, Formatter
import omron_sensor_util
from socket import gethostname
from prometheus_client import write_to_textfile, push_to_gateway
import urllib
"""
Load config.ini
"""
config = configparser.ConfigParser()
config_path = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(config_path, 'config.ini')
config.read(config_path, 'UTF-8')
HOSTNAME = gethostname()
# Base
LOG_LEVEL = config["BASE"]["LOG_LEVEL"]
LOG_DIR = config["BASE"]["LOG_DIR"]
ENABLE_CSV = config.getboolean("BASE","ENABLE_CSV")
CSV_DIR = config["BASE"]["CSV_DIR"]
# Sensor
SERIAL_PORT = config["SENSOR"]["SERIAL_PORT"]
BAUD_RATE = config.getint("SENSOR", "BAUD_RATE")
SCAN_PERIOD = config.getfloat("SENSOR", "SCAN_PERIOD")
WRITE_WAIT = config.getfloat("SENSOR","WRITE_WAIT")
# Prometheus
ENABLE_NODEEXPORTER = config.getboolean("PROMETHEUS","ENABLE_NODEEXPORTER")
NODE_OUTPUT_DIR = config["PROMETHEUS"]["NODE_OUTPUT_DIR"]
ENABLE_PUSHGATEWAY= config.getboolean("PROMETHEUS","ENABLE_PUSHGATEWAY")
PUSHGATEWAY = config["PROMETHEUS"]["PUSHGATEWAY"]
PUSHGATEWAY_TIMEOUT = config.getfloat("PROMETHEUS","PUSHGATEWAY_TIMEOUT")
# Create filename
LOG_FILE = LOG_DIR + HOSTNAME + "-sensor.log"
CSV_FILE = CSV_DIR + HOSTNAME + "-sensor.csv"
PROM_FILE = NODE_OUTPUT_DIR + HOSTNAME + ".prom"

"""
Logging
"""
logger = getLogger(__name__)
logger.setLevel(LOG_LEVEL)
if not logger.hasHandlers():
    handler = FileHandler(filename=LOG_FILE) 
    handler.setFormatter(Formatter("%(asctime)s %(levelname)6s %(message)s"))
    logger.addHandler(handler)

"""
Main
"""
def main():
    with OmronSensor() as sensor:
        sensor.run()

"""
Systemd service termination
"""
class TerminatedExecption(Exception):
    pass

def sig_handler(signum, frame) -> None:
    raise TerminatedExecption()

"""
Serial Port
"""
def get_serial_connection():
    try:
       conn = serial.Serial(SERIAL_PORT,
                            BAUD_RATE,
                            serial.EIGHTBITS,
                            serial.PARITY_NONE)
       logger.info("Serial Port connected.")
    except serial.serialutil.SerialException as e:
        logger.error(f"Cannot connect serial port: {e}")
        sys.exit(1)
    return conn

"""
Omron Sensor
"""
class OmronSensor(object):
    # LED display rule. Normal Off.
    LED_OFF = 0

    # LED display rule. Normal On.
    LED_ON = 1
    
    def __init__(self):
        # Check diretory
        if ENABLE_CSV and not os.path.isdir(CSV_DIR):
            logger.error("Could not open csv dir: {}".format(CSV_DIR))
            sys.exit(1)
        if ENABLE_NODEEXPORTER and not os.path.isdir(NODE_OUTPUT_DIR):
            logger.error("Could not open prom dir: {}".format(NODE_OUTPUT_DIR))
            sys.exit(1)
        
        # Get serial connection
        self.conn = get_serial_connection()
        
        # Set signal handler for systemd termination command
        signal.signal(signal.SIGTERM, sig_handler)
        
        # LED on
        self.led_on()
        
        # Inform systemd that finished startup sequence...
        n = sdnotify.SystemdNotifier()
        n.notify("READY=1")
        
    def __enter__(self):
        return self
    
    def __exit__(self, exception_type, exception_value, traceback):
        self.led_off()
        self.conn.close()
        logger.info("Serial port close")
        sys.exit
    
    def led_on(self):
        # LED On. Color of Green.
        command = bytearray([0x52, 0x42, 0x0a, 0x00, 0x02, 0x11, 0x51, self.LED_ON, 0x00, 0, 255, 0])
        command = command + omron_sensor_util.calc_crc(command, len(command))
        self.conn.write(command)
        time.sleep(0.1)
        logger.info("Omron Sensor LED on")    

    def led_off(self):
        # LED On. Color of Green.
        command = bytearray([0x52, 0x42, 0x0a, 0x00, 0x02, 0x11, 0x51, self.LED_OFF, 0x00, 0, 0, 0])
        command = command + omron_sensor_util.calc_crc(command, len(command))
        self.conn.write(command)
        time.sleep(0.1)
        logger.info("Omron Sensor LED off")

    def run(self):
        logger.info("Omron Sensor Started.")
        
        try:
            # Read data
            data = self.conn.read(self.conn.inWaiting())
        
            while self.conn.isOpen():
                # Get Latest data Long.
                command = bytearray([0x52, 0x42, 0x05, 0x00, 0x01, 0x21, 0x50])
                command = command + omron_sensor_util.calc_crc(command, len(command))
                self.conn.write(command)
                time.sleep(WRITE_WAIT)
                
                data = self.conn.read(self.conn.inWaiting())
                try:
                    #perse_data = omron_sensor_util.perse_latest_data(data)
                    perse_data = omron_sensor_util.perse_latest_data_short(data)
                except IndexError:
                    logger.error("Sensor Data null or broken.")
                    time.sleep(SCAN_PERIOD - WRITE_WAIT)
                    continue
                
                # Logging data
                logger.info(perse_data)
                
                # Write csv
                if ENABLE_CSV:
                    #omron_sensor_util.write_csv(CSV_FILE, perse_data)
                    omron_sensor_util.write_csv_short(CSV_FILE, perse_data)
                
                # Register data for prometheus
                if ENABLE_NODEEXPORTER or ENABLE_PUSHGATEWAY:
                    registry = omron_sensor_util.write_prom_registry(perse_data)
                
                # Output to prometheus
                if ENABLE_NODEEXPORTER:
                    write_to_textfile(PROM_FILE, registry)
                
                if ENABLE_PUSHGATEWAY:
                    try:
                        push_to_gateway(PUSHGATEWAY, job=HOSTNAME,
                                        registry=registry, timeout=PUSHGATEWAY_TIMEOUT)
                    except urllib.error.URLError as e:
                        logger.error("Can not connect to prometheus gateway {}".format(e))
                        pass
                
                # Wait for next scan
                time.sleep(SCAN_PERIOD - WRITE_WAIT)
        
        except KeyboardInterrupt:
            logger.info("Stopped by keyboard input (ctrl-C)")
        except TerminatedExecption:
            logger.info("Stopped by systemd.")
        except OSError as e:
            logger.exception("Network Error", stack_info=True)
            # program will be restarted automatically by systemd (Restart on-failure)
            raise e
        except Exception:
            logger.exception("Other Error", stack_info=True)

if __name__ == '__main__':
    main()
