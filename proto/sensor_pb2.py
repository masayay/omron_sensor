# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: proto/sensor.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12proto/sensor.proto\x12\x06sensor\"\x06\n\x04Null\"\xd1\x02\n\x0bsensorValue\x12\x10\n\x08HostName\x18\x01 \x01(\t\x12\x13\n\x0bTemperature\x18\x02 \x01(\x01\x12\x18\n\x10RelativeHumidity\x18\x03 \x01(\x01\x12\x14\n\x0c\x41mbientLight\x18\x04 \x01(\x01\x12\x1a\n\x12\x42\x61rometricPressure\x18\x05 \x01(\x01\x12\x12\n\nSoundNoise\x18\x06 \x01(\x01\x12\r\n\x05\x45TVOC\x18\x07 \x01(\x01\x12\x0c\n\x04\x45\x43O2\x18\x08 \x01(\x01\x12\x17\n\x0f\x44iscomfortIndex\x18\t \x01(\x01\x12\x12\n\nHeatStroke\x18\n \x01(\x01\x12\x1c\n\x14VibrationInformation\x18\x0b \x01(\x01\x12\x0f\n\x07SiValue\x18\x0c \x01(\x01\x12\x0b\n\x03Pga\x18\r \x01(\x01\x12\x18\n\x10SeismicIntensity\x18\x0e \x01(\x01\x12\x1b\n\x13UnixTimeMillisecond\x18\x0f \x01(\x03\x32k\n\x06sensor\x12.\n\tpushValue\x12\x13.sensor.sensorValue\x1a\x0c.sensor.Null\x12\x31\n\npushValues\x12\x13.sensor.sensorValue\x1a\x0c.sensor.Null(\x01\x42\nZ\x08./sensorb\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'proto.sensor_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  DESCRIPTOR._serialized_options = b'Z\010./sensor'
  _NULL._serialized_start=30
  _NULL._serialized_end=36
  _SENSORVALUE._serialized_start=39
  _SENSORVALUE._serialized_end=376
  _SENSOR._serialized_start=378
  _SENSOR._serialized_end=485
# @@protoc_insertion_point(module_scope)
