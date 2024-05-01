import numpy as np


def ubx_nav_pvt(data):
    # Parse UBX-NAV-PVT message

    msg_t = np.dtype(
        [
            ("class", "u1"),
            ("id", "u1"),
            ("length", "<u2"),
            ("iTOW", "u4"),
            ("year", "u2"),
            ("month", "u1"),
            ("day", "u1"),
            ("hour", "u1"),
            ("min", "u1"),
            ("sec", "u1"),
            ("valid", "u1"),
            ("tAcc", "u4"),
            ("nano", "i4"),
            ("fixType", "u1"),
            ("flags", "u1"),
            ("flags2", "u1"),
            ("numSV", "u1"),
            ("lon", "i4"),
            ("lat", "i4"),
            ("height", "i4"),
            ("hMSL", "i4"),
            ("hAcc", "u4"),
            ("vAcc", "u4"),
            ("velN", "i4"),
            ("velE", "i4"),
            ("velD", "i4"),
            ("gSpeed", "i4"),
            ("headMot", "i4"),
            ("sAcc", "u4"),
            ("headAcc", "u4"),
            ("pDOP", "u2"),
            ("flags3", "u2"),
            ("reserved0", "u1", 4),
            ("headVeh", "i4"),
            ("magDec", "i2"),
            ("magAcc", "u2"),
        ]
    )

    msg = np.frombuffer(data, dtype=msg_t, count=1, offset=2)[0]

    return msg
