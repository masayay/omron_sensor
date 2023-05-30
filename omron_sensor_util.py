import os, csv
from datetime import datetime
from prometheus_client import CollectorRegistry, Gauge
import configparser
from socket import gethostname
from logging import getLogger, FileHandler, Formatter
    
"""
Load config.ini
"""
class Config():
    def __init__(self):
        config = configparser.ConfigParser()
        config_path = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(config_path, 'config.ini')
        config.read(config_path, 'UTF-8')
        
        self.HOSTNAME = gethostname()
        # Base
        self.LOG_LEVEL = config["BASE"]["LOG_LEVEL"]
        self.LOG_DIR = config["BASE"]["LOG_DIR"]
        self.ENABLE_CSV = config.getboolean("BASE","ENABLE_CSV")
        self.CSV_DIR = config["BASE"]["CSV_DIR"]
        # Sensor
        self.SERIAL_PORT = config["SENSOR"]["SERIAL_PORT"]
        self.BAUD_RATE = config.getint("SENSOR", "BAUD_RATE")
        self.SCAN_PERIOD = config.getfloat("SENSOR", "SCAN_PERIOD")
        self.WRITE_WAIT = config.getfloat("SENSOR","WRITE_WAIT")
        # Prometheus
        self.ENABLE_NODEEXPORTER = config.getboolean("PROMETHEUS","ENABLE_NODEEXPORTER")
        self.NODE_OUTPUT_DIR = config["PROMETHEUS"]["NODE_OUTPUT_DIR"]
        self.ENABLE_PUSHGATEWAY= config.getboolean("PROMETHEUS","ENABLE_PUSHGATEWAY")
        self.PUSHGATEWAY = config["PROMETHEUS"]["PUSHGATEWAY"]
        self.PUSHGATEWAY_TIMEOUT = config.getfloat("PROMETHEUS","PUSHGATEWAY_TIMEOUT")
        # gRPC
        self.ENABLE_gRPC = config.getboolean("gRPC","ENABLE_gRPC")
        self.gRPC_SERVER = config["gRPC"]["gRPC_SERVER"]
        self.gRPC_TIMEOUT = config.getfloat("gRPC","gRPC_TIMEOUT")
        self.gRPC_STREAM = config.getboolean("gRPC","gRPC_STREAM")
        # Create filename
        self.LOG_FILE = self.LOG_DIR + self.HOSTNAME + "-sensor.log"
        self.CSV_FILE = self.CSV_DIR + self.HOSTNAME + "-sensor.csv"
        self.PROM_FILE = self.NODE_OUTPUT_DIR + self.HOSTNAME + ".prom"

    def setLogger(self, name):
        logger = getLogger(name)
        logger.setLevel(self.LOG_LEVEL)
        if not logger.hasHandlers():
            handler = FileHandler(filename=self.LOG_FILE)
            handler.setFormatter(Formatter("%(asctime)s %(levelname)6s %(message)s"))
            logger.addHandler(handler)
        return logger

"""
CSV File
"""
Headers = ['Time measured', 'Temperature', 'Relative humidity', 'Ambient light',
          'Barometric pressure', 'Sound noise', 'eTVOC', 'eCO2', 'Discomfort index',
          'Heat stroke', 'Vibration information', 'SI value', 'PGA', 'Seismic intensity',
          'Temperature flag', 'Relative humidity flag', 'Ambient light flag',
          'Barometric pressure flag', 'Sound noise flag', 'eTVOC flag', 'eCO2 flag',
          'Discomfort index flag', 'Heat stroke flag', 'SI value flag', 'PGA flag',
          'Seismic intensity flag']

Headers_short = ['Time measured', 'Temperature', 'Relative humidity', 'Ambient light',
          'Barometric pressure', 'Sound noise', 'eTVOC', 'eCO2', 'Discomfort index',
          'Heat stroke', 'Vibration information', 'SI value', 'PGA', 'Seismic intensity'
          ]

def write_csv(filepath, data):
    if not os.path.isfile(filepath):
        # File does not exsist, create new
        with open(filepath, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=Headers)
            w.writeheader()
            w.writerow(data)
    elif not os.path.getsize(filepath):
        # File exsists but empty
        with open(filepath, 'a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=Headers)
            w.writeheader()
            w.writerow(data)
    else:
        # File exsists and not empty
        with open(filepath, 'a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=Headers)
            w.writerow(data)

def write_csv_short(filepath, data):
    if not os.path.isfile(filepath):
        # File does not exsist, create new
        with open(filepath, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=Headers_short)
            w.writeheader()
            w.writerow(data)
    elif not os.path.getsize(filepath):
        # File exsists but empty
        with open(filepath, 'a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=Headers_short)
            w.writeheader()
            w.writerow(data)
    else:
        # File exsists and not empty
        with open(filepath, 'a', newline='') as f:
            w = csv.DictWriter(f, fieldnames=Headers_short)
            w.writerow(data)

"""
Prometheus exporter
"""
def write_prom_registry(data):
    
    # Prepare prometheus registry
    registry = CollectorRegistry()
    g_temperature = Gauge('temperature', 'Temperature', registry=registry)
    g_relative_humidity = Gauge('relative_humidity', 'Relative humidity', registry=registry)
    g_ambient_light = Gauge('ambient_light', 'Ambient light', registry=registry)
    g_barometric_pressure = Gauge('barometric_pressure', 'Barometric pressure', registry=registry)
    g_sound_noise = Gauge('sound_noise', 'Sound noise', registry=registry)
    g_eTVOC = Gauge('eTVOC', 'eTVOC', registry=registry)
    g_eCO2 = Gauge('eCO2', 'eCO2', registry=registry)
    g_discomfort_index = Gauge('discomfort_index', 'Discomfort index', registry=registry)
    g_heat_stroke = Gauge('heat_stroke', 'Heat stroke', registry=registry)
    g_vibration_information = Gauge('vibration_information', 'Vibration information', registry=registry)
    g_si_value = Gauge('si_value', 'SI value', registry=registry)
    g_pga = Gauge('pga', 'PGA', registry=registry)
    g_seismic_intensity = Gauge('seismic_intensity', 'Seismic intensity', registry=registry)
    
    # Set data
    g_temperature.set(data["Temperature"])
    g_relative_humidity.set(data["Relative humidity"])
    g_ambient_light.set(data["Ambient light"])
    g_barometric_pressure.set(data["Barometric pressure"])
    g_sound_noise.set(data["Sound noise"])
    g_eTVOC.set(data["eTVOC"])
    g_eCO2.set(data["eCO2"])
    g_discomfort_index.set(data["Discomfort index"])
    g_heat_stroke.set(data["Heat stroke"])
    g_vibration_information.set(data["Vibration information"])
    g_si_value.set(data["SI value"])
    g_pga.set(data["PGA"])
    g_seismic_intensity.set(data["Seismic intensity"])
    
    return registry


"""
Sensor Util
"""
def s16(value):
    return -(value & 0x8000) | (value & 0x7fff)

def calc_crc(buf, length):
    """
    CRC-16 calculation.
    """
    crc = 0xFFFF
    for i in range(length):
        crc = crc ^ buf[i]
        for i in range(8):
            carrayFlag = crc & 1
            crc = crc >> 1
            if (carrayFlag == 1):
                crc = crc ^ 0xA001
    crcH = crc >> 8
    crcL = crc & 0x00FF
    return (bytearray([crcL, crcH]))

def perse_latest_data_short(data):
    
    sensor_data = {}
    
    time_measured = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    temperature = str( s16(int(hex(data[9]) + '{:02x}'.format(data[8]), 16)) / 100)
    relative_humidity = str(int(hex(data[11]) + '{:02x}'.format(data[10]), 16) / 100)
    ambient_light = str(int(hex(data[13]) + '{:02x}'.format(data[12]), 16))
    barometric_pressure = str(int(hex(data[17]) + '{:02x}'.format(data[16])
                                  + '{:02x}'.format(data[15]) + '{:02x}'.format(data[14]), 16) / 1000)
    sound_noise = str(int(hex(data[19]) + '{:02x}'.format(data[18]), 16) / 100)
    eTVOC = str(int(hex(data[21]) + '{:02x}'.format(data[20]), 16))
    eCO2 = str(int(hex(data[23]) + '{:02x}'.format(data[22]), 16))
    discomfort_index = str(int(hex(data[25]) + '{:02x}'.format(data[24]), 16) / 100)
    heat_stroke = str(s16(int(hex(data[27]) + '{:02x}'.format(data[26]), 16)) / 100)
    vibration_information = str(int(hex(data[28]), 16))
    si_value = str(int(hex(data[30]) + '{:02x}'.format(data[29]), 16) / 10)
    pga = str(int(hex(data[32]) + '{:02x}'.format(data[31]), 16) / 10)
    seismic_intensity = str(int(hex(data[34]) + '{:02x}'.format(data[33]), 16) / 1000)
    
    sensor_data["Time measured"] = time_measured
    sensor_data["Temperature"] = temperature
    sensor_data["Relative humidity"] = relative_humidity
    sensor_data["Ambient light"] = ambient_light
    sensor_data["Barometric pressure"] = barometric_pressure
    sensor_data["Sound noise"] = sound_noise
    sensor_data["eTVOC"] = eTVOC
    sensor_data["eCO2"] = eCO2
    sensor_data["Discomfort index"] = discomfort_index
    sensor_data["Heat stroke"] = heat_stroke
    sensor_data["Vibration information"] = vibration_information
    sensor_data["SI value"] = si_value
    sensor_data["PGA"] = pga
    sensor_data["Seismic intensity"] = seismic_intensity
    
    return sensor_data

def perse_latest_data(data):
    
    sensor_data = {}
    
    time_measured = datetime.now().strftime("%Y/%m/%d %H:%M:%S")
    temperature = str( s16(int(hex(data[9]) + '{:02x}'.format(data[8]), 16)) / 100)
    relative_humidity = str(int(hex(data[11]) + '{:02x}'.format(data[10]), 16) / 100)
    ambient_light = str(int(hex(data[13]) + '{:02x}'.format(data[12]), 16))
    barometric_pressure = str(int(hex(data[17]) + '{:02x}'.format(data[16])
                                  + '{:02x}'.format(data[15]) + '{:02x}'.format(data[14]), 16) / 1000)
    sound_noise = str(int(hex(data[19]) + '{:02x}'.format(data[18]), 16) / 100)
    eTVOC = str(int(hex(data[21]) + '{:02x}'.format(data[20]), 16))
    eCO2 = str(int(hex(data[23]) + '{:02x}'.format(data[22]), 16))
    discomfort_index = str(int(hex(data[25]) + '{:02x}'.format(data[24]), 16) / 100)
    heat_stroke = str(s16(int(hex(data[27]) + '{:02x}'.format(data[26]), 16)) / 100)
    vibration_information = str(int(hex(data[28]), 16))
    si_value = str(int(hex(data[30]) + '{:02x}'.format(data[29]), 16) / 10)
    pga = str(int(hex(data[32]) + '{:02x}'.format(data[31]), 16) / 10)
    seismic_intensity = str(int(hex(data[34]) + '{:02x}'.format(data[33]), 16) / 1000)
    temperature_flag = str(int(hex(data[36]) + '{:02x}'.format(data[35]), 16))
    relative_humidity_flag = str(int(hex(data[38]) + '{:02x}'.format(data[37]), 16))
    ambient_light_flag = str(int(hex(data[40]) + '{:02x}'.format(data[39]), 16))
    barometric_pressure_flag = str(int(hex(data[42]) + '{:02x}'.format(data[41]), 16))
    sound_noise_flag = str(int(hex(data[44]) + '{:02x}'.format(data[43]), 16))
    etvoc_flag = str(int(hex(data[46]) + '{:02x}'.format(data[45]), 16))
    eco2_flag = str(int(hex(data[48]) + '{:02x}'.format(data[47]), 16))
    discomfort_index_flag = str(int(hex(data[50]) + '{:02x}'.format(data[49]), 16))
    heat_stroke_flag = str(int(hex(data[52]) + '{:02x}'.format(data[51]), 16))
    si_value_flag = str(int(hex(data[53]), 16))
    pga_flag = str(int(hex(data[54]), 16))
    seismic_intensity_flag = str(int(hex(data[55]), 16))
    
    sensor_data["Time_measured"] = time_measured
    sensor_data["Temperature"] = temperature
    sensor_data["Relative_humidity"] = relative_humidity
    sensor_data["Ambient_light"] = ambient_light
    sensor_data["Barometric_pressure"] = barometric_pressure
    sensor_data["Sound_noise"] = sound_noise
    sensor_data["eTVOC"] = eTVOC
    sensor_data["eCO2"] = eCO2
    sensor_data["Discomfort_index"] = discomfort_index
    sensor_data["Heat_stroke"] = heat_stroke
    sensor_data["Vibration_information"] = vibration_information
    sensor_data["SI_value"] = si_value
    sensor_data["PGA"] = pga
    sensor_data["Seismic_intensity"] = seismic_intensity
    sensor_data["Temperature_flag"] = temperature_flag
    sensor_data["Relative_humidity_flag"] = relative_humidity_flag
    sensor_data["Ambient_light_flag"] = ambient_light_flag
    sensor_data["Barometric_pressure_flag"] = barometric_pressure_flag
    sensor_data["Sound_noise_flag"] = sound_noise_flag
    sensor_data["eTVOC_flag"] = etvoc_flag
    sensor_data["eCO2_flag"] = eco2_flag
    sensor_data["Discomfort_index_flag"] = discomfort_index_flag
    sensor_data["Heat_stroke_flag"] = heat_stroke_flag
    sensor_data["SI_value_flag"] = si_value_flag
    sensor_data["PGA_flag"] = pga_flag
    sensor_data["Seismic_intensity_flag"] = seismic_intensity_flag
    
    return sensor_data


