import ubx


gps = ubx.UBX()

gps.disableNMEA()
# gps.disableAllMessages()
gps.enablePVT()
gps.enableRF()
# gps.enableRAWX()
# gps.enableSFRBX()
# gps.dumpNMEA()
gps.dumpUBX()
# gps.streamPVT()
