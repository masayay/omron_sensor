import grpc
from proto import sensor_pb2_grpc, sensor_pb2
import time
import omron_sensor_util

"""
Config
"""
conf = omron_sensor_util.Config()
"""
Logging
"""
logger = conf.setLogger(__name__)

class grpcClient():
    def open(self):
        self.sensor_value = sensor_pb2.sensorValue()
        self.channel = grpc.insecure_channel(conf.gRPC_SERVER)
        self.stub = sensor_pb2_grpc.sensorStub(self.channel)
        logger.info("Open gPRC connection: {0}".format(conf.gRPC_SERVER))
        
    def close(self):
        self.channel.close()
        logger.info("Close gPRC connection")

    def start(self, generator):
        try:
            logger.info("start gPRC pushValues")
            self.stub.pushValues(generator)
        except Exception as e:
            logger.error("gRPC pushValue error {0}".format(e))
        
    
    def get_value(self):
        return self.sensor_value
             
    def push_value(self, hostname, data):
        self.sensor_value = sensor_pb2.sensorValue(
            HostName = hostname,
            Temperature = float(data["Temperature"]),
            RelativeHumidity = float(data["Relative humidity"]),
            AmbientLight = int(data["Ambient light"]),
            BarometricPressure = float(data["Barometric pressure"]),
            SoundNoise = float(data["Sound noise"]),
            ETVOC = int(data["eTVOC"]),
            ECO2 = int(data["eCO2"]),
            DiscomfortIndex = float(data["Discomfort index"]),
            HeatStroke = float(data["Heat stroke"]),
            VibrationInformation = int(data["Vibration information"]),
            SiValue = float(data["SI value"]),
            Pga = float(data["PGA"]),
            SeismicIntensity = float(data["Seismic intensity"]),
            UnixTimeMillisecond = int(time.time() * 1000)
            )
        
        if not conf.gRPC_STREAM:
            try:
                self.stub.pushValue(self.sensor_value)
                logger.info("gRPC pushValue success")
                             
            except Exception as e:
                logger.error("gRPC pushValue error {0}".format(e))
        
        
        