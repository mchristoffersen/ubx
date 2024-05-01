import ubx


def case_0():
    rb = ubx.RingBuffer()
    x = b"\x01\x05\x02"
    rb.append(x)
    return rb


def test_len_0():
    rb = case_0()
    assert len(rb) == 3


def test_append_0():
    rb = case_0()
    assert rb[0] == 1 and rb[1] == 5 and rb[2] == 2


def test_advance_0():
    rb = case_0()
    rb.advance(2)
    assert rb[0] == 2


def case_1():
    rb = ubx.RingBuffer(size=5)
    x = b"\x01\x05\x02"
    rb.append(x)
    rb.advance(2)
    rb.append(x)
    rb.advance(2)
    return rb


def test_len_1():
    rb = case_1()
    assert len(rb) == 2


def test_append_1():
    rb = case_1()
    assert rb[0] == 5 and rb[1] == 2
