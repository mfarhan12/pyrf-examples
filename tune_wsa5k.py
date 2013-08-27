
from pyrf.devices.thinkrf import WSA4000
import sys
# plot constants
center_freq = 16000 * 1e6 
SAMPLE_SIZE = 2048
DECIMATION = 1
bandwidth = (125 *1e6) / DECIMATION
FREQ_SHIFT = 0

# connect to WSA4000 device
dut = WSA4000()
dut.connect('10.126.110.106')
center_freq = int(sys.argv[1]) * 1e6
dut.freq(center_freq)