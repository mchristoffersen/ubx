import numpy as np


def ubx_rxm_sfrbx(data):
    # Parse UBX-RXM-SFRBX message

    # Fixed length portion
    hdr_t = np.dtype(
        [
            ("class", "u1"),
            ("id", "u1"),
            ("length", "<u2"),
            ("gnssId", "u1"),
            ("svId", "u1"),
            ("sigId", "u1"),
            ("freqId", "u1"),
            ("numWords", "u1"),
            ("chn", "u1"),
            ("version", "u1"),
            ("reserved0", "u1"),
        ]
    )

    hdr = np.frombuffer(data, dtype=hdr_t, count=1, offset=2)[0]

    # Subframe data
    msg = np.frombuffer(
        data, dtype="<u4", count=hdr["numWords"], offset=2 + hdr_t.itemsize
    )

    return (hdr, msg)


def ubx_rxm_rawx(data):
    # Parse UBX-RXM-RAWX message

    # Fixed length portion
    hdr_t = np.dtype(
        [
            ("class", "u1"),
            ("id", "u1"),
            ("length", "<u2"),
            ("rcvTow", "f8"),
            ("week", "<u2"),
            ("leapS", "i1"),
            ("numMeas", "u1"),
            ("recStat", "u1"),
            ("version", "u1"),
            ("reserved0", "u1", 2),
        ]
    )

    hdr = np.frombuffer(data, dtype=hdr_t, count=1, offset=2)[0]

    # Variable length
    msg_t = np.dtype(
        [
            ("prMes", "f8"),
            ("cpMes", "f8"),
            ("doMes", "f4"),
            ("gnssId", "u1"),
            ("svId", "u1"),
            ("sigId", "u1"),
            ("freqId", "u1"),
            ("locktime", "u2"),
            ("cno", "u1"),
            ("prStdev", "u1"),
            ("cpStdev", "u1"),
            ("doStdev", "u1"),
            ("trkStat", "u1"),
            ("reserved1", "u1"),
        ]
    )

    msg = np.frombuffer(
        data, dtype=msg_t, count=hdr["numMeas"], offset=2 + hdr_t.itemsize
    )

    return (hdr, msg)
