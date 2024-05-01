import ubx


gps = ubx.UBX(baudrate=115200)

gps.disableNMEA()
# gps.disableAllMessages()
gps.enablePVT()
# gps.enableRAWX()
# gps.enableSFRBX()
# gps.dumpNMEA()
# gps.dumpUBX()
gps.streamPVT()
