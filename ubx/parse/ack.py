import numpy as np


def ubx_ack_ack(data):
    #  PARSE UBX-ACK-ACK

    msg_t = np.dtype(
        [
            ("class", "u1"),
            ("id", "u1"),
            ("length", "<u2"),
            ("clsID", "u1"),
            ("msgID", "u1"),
        ]
    )

    msg = np.frombuffer(data, dtype=msg_t, count=1, offset=2)

    return msg


def ubx_ack_nak(data):
    #  PARSE UBX-ACK-NAK

    msg_t = np.dtype(
        [
            ("class", "u1"),
            ("id", "u1"),
            ("length", "<u2"),
            ("clsID", "u1"),
            ("msgID", "u1"),
        ]
    )

    msg = np.frombuffer(data, dtype=msg_t, count=1, offset=2)

    return msg
