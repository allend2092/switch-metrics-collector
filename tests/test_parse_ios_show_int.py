from switchmetrics.parse_ios_show_int import parse_show_interfaces

RAW = """FastEthernet0/47 is up, line protocol is up (connected)
  5 minute input rate 3000 bits/sec, 2 packets/sec
  5 minute output rate 3000 bits/sec, 3 packets/sec
     114907 packets input, 16112767 bytes, 0 no buffer
     713844 packets output, 912638310 bytes, 0 underruns
"""

def test_parse_basic():
    c = parse_show_interfaces(RAW)
    assert c.iface == "FastEthernet0/47"
    assert c.input_pkts == 114907
    assert c.input_bytes == 16112767
    assert c.output_pkts == 713844
    assert c.output_bytes == 912638310
    assert c.five_min_input_bps == 3000
