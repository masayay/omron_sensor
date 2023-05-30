#!/usr/bin/python3
import serial, sys, time, os, signal, sdnotify
import omron_sensor_util
from prometheus_client import write_to_textfile, push_to_gateway
import urllib
from grpc_client import grpcClient

"""
Config
"""
conf = omron_sensor_util.Config()
"""
Logging
"""
logger = conf.setLogger(__name__)
"""
Main
"""
def main():
    with OmronSensor() as sensor:
        # gRPC stream
        if conf.gRPC_STREAM:
            generator = sensor.run()
            try:
                sensor.grpc_conn.start(generator)
            except Exception as e:
                logger.error("stop gRPC stream {0}".format(e))
                time.sleep(60)
                # program will be restarted automatically by systemd (Restart on-failure)
                raise e
        else:
            generator = sensor.run()
            try:
                generator.__next__()
            except StopIteration:
                logger.info("StopIteration.")

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
       conn = serial.Serial(conf.SERIAL_PORT,
                            conf.BAUD_RATE,
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
        if conf.ENABLE_CSV and not os.path.isdir(conf.CSV_DIR):
            logger.error("Could not open csv dir: {}".format(conf.CSV_DIR))
            sys.exit(1)
        if conf.ENABLE_NODEEXPORTER and not os.path.isdir(conf.NODE_OUTPUT_DIR):
            logger.error("Could not open prom dir: {}".format(conf.NODE_OUTPUT_DIR))
            sys.exit(1)
        
        # Get serial connection
        self.conn = get_serial_connection()
        
        # Set signal handler for systemd termination command
        signal.signal(signal.SIGTERM, sig_handler)
        
        # LED on
        self.led_on()
        
        # gRPC
        if conf.ENABLE_gRPC:
            self.grpc_conn = grpcClient()
            self.grpc_conn.open()
                    
        # Inform systemd that finished startup sequence...
        n = sdnotify.SystemdNotifier()
        n.notify("READY=1")
        
    def __enter__(self):
        return self
    
    def __exit__(self, exception_type, exception_value, traceback):
        self.led_off()
        self.conn.close()
        if conf.ENABLE_gRPC:
            self.grpc_conn.close()
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
                time.sleep(conf.WRITE_WAIT)
                
                data = self.conn.read(self.conn.inWaiting())
                try:
                    #perse_data = omron_sensor_util.perse_latest_data(data)
                    perse_data = omron_sensor_util.perse_latest_data_short(data)
                except IndexError:
                    logger.error("Sensor Data null or broken.")
                    time.sleep(conf.SCAN_PERIOD - conf.WRITE_WAIT)
                    continue
                
                # Logging data
                logger.info(perse_data)
                
                # Write csv
                if conf.ENABLE_CSV:
                    #omron_sensor_util.write_csv(CSV_FILE, perse_data)
                    omron_sensor_util.write_csv_short(conf.CSV_FILE, perse_data)
                
                # Register data for prometheus
                if conf.ENABLE_NODEEXPORTER or conf.ENABLE_PUSHGATEWAY:
                    registry = omron_sensor_util.write_prom_registry(perse_data)
                
                # Output to prometheus
                if conf.ENABLE_NODEEXPORTER:
                    write_to_textfile(conf.PROM_FILE, registry)
                
                if conf.ENABLE_PUSHGATEWAY:
                    try:
                        push_to_gateway(conf.PUSHGATEWAY, job=conf.HOSTNAME,
                                        registry=registry, timeout=conf.PUSHGATEWAY_TIMEOUT)
                    except urllib.error.URLError as e:
                        logger.error("Can not connect to prometheus gateway {}".format(e))
                        pass
                
                # gRPC
                if conf.ENABLE_gRPC:
                    self.grpc_conn.push_value(conf.HOSTNAME, perse_data)
                    #self.grpc_conn.push_value("sensor-client1", perse_data)
                
                if conf.gRPC_STREAM:
                    logger.debug("gRPC pushValues")
                    yield self.grpc_conn.get_value()
                
                # Wait for next scan
                time.sleep(conf.SCAN_PERIOD - conf.WRITE_WAIT)
        
        except KeyboardInterrupt:
            logger.info("Stopped by keyboard input (ctrl-C)")
        except TerminatedExecption:
            logger.info("Stopped by systemd.")
        except OSError as e:
            logger.exception("Network Error", stack_info=True)
            time.sleep(1)
            # program will be restarted automatically by systemd (Restart on-failure)
            raise e
        except Exception:
            logger.exception("Other Error", stack_info=True)

if __name__ == '__main__':
    main()
