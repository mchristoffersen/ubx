import numpy as np


def ubx_mon_rf(data):
    # Parse UBX-MON-RF message

    # Fixed length portion
    hdr_t = np.dtype(
        [
            ("class", "u1"),
            ("id", "u1"),
            ("length", "<u2"),
            ("version", "<u1"),
            ("nBlocks", "<u1"),
            ("reserved0", "u1", 2),
        ]
    )

    hdr = np.frombuffer(data, dtype=hdr_t, count=1, offset=2)[0]

    # Variable length
    msg_t = np.dtype(
        [
            ("blockId", "<u1"),
            ("flags", "<u1"),
            ("antStatus", "<u1"),
            ("antPower", "<u1"),
            ("postStatus", "<u4"),
            ("reserved1", "<u1", 4),
            ("noisePerMS", "<u2"),
            ("agcCnt", "<u2"),
            ("cwSuppression", "<u1"),
            ("ofsI", "<i1"),
            ("magI", "<u1"),
            ("ofsQ", "<i1"),
            ("magQ", "<u1"),
            ("reserved2", "<u1", 3)
        ]
    )

    msg = np.frombuffer(
        data, dtype=msg_t, count=hdr["nBlocks"], offset=2 + hdr_t.itemsize
    )

    return (hdr, msg)