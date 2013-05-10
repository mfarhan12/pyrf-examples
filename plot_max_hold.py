#!/usr/bin/python

# import required libraries
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyrf.devices.thinkrf import WSA4000
from pyrf.util import read_data_and_context
from pyrf.config import TriggerSettings
from pyrf.numpy_util import compute_fft
import sys

# plot constants
center_freq = 2450 * 1e6 
SAMPLE_SIZE = 1024
RF_GAIN = 'high'
IF_GAIN = 0
DECIMATION = 1
bandwidth = (125 *1e6) / DECIMATION
FREQ_SHIFT = 0

# declare the GUI
app = QtGui.QApplication([])
win = pg.GraphicsWindow()
win.resize(1000,600)
win.setWindowTitle("PYRF Max Hold Example")

# connect to WSA4000 device
dut = WSA4000()
dut.connect(sys.argv[1])

# initialize WSA constants
dut.reset()
dut.request_read_perm()
dut.freq(center_freq)
dut.gain(RF_GAIN)
dut.ifgain(IF_GAIN)
dut.fshift(FREQ_SHIFT)
dut.decimation(DECIMATION)

# initialize fft plot
fft_plot = win.addPlot(title="Power (dBm) Vs. Frequency (MHz)")

# initialize plot axes limits
plot_xmin = (center_freq) - (bandwidth / 2)
plot_xmax = (center_freq) + (bandwidth / 2)

plot_ymin = -130
plot_ymax = 20

# initialize the frequency range (Hz)
freq_range = np.linspace(plot_xmin , plot_xmax, SAMPLE_SIZE)

# initialize the x-axis of the fft plot
fft_plot.setXRange(plot_xmin,plot_xmax)
fft_plot.setLabel('bottom', text= 'Frequency', units = 'Hz', unitPrefix=None)

# initialize the y-axis of the fft plot
fft_plot.setYRange(plot_ymin ,plot_ymax)
fft_plot.setLabel('left', text= 'Power', units = 'dBm', unitPrefix=None)
fft_plot.clear()
# disable auto size of the x-y axis
fft_plot.enableAutoRange('xy', False)

# initialize FFT curve
fft_curve = fft_plot.plot(pen='g')

# initialize max hold curve
max_curve = fft_plot.plot(pen='y')

# initialize the max hold curve with a very large negative number
max_hold = np.zeros(SAMPLE_SIZE) - 500 

def update():
    global dut, fft_curve, max_curve,fft_plot, freq_range
    
    # read data from wsa
    data, context = read_data_and_context(dut, SAMPLE_SIZE)

    # compute the fft and plot the data
    pow_data = compute_fft(dut, data, context)
    
    # update the max curve
    for i in range(len(pow_data)):
        if pow_data[i] > max_hold[i]:
            max_hold[i] = pow_data[i]

    # plot the standard FFT curve
    fft_curve.setData(freq_range,pow_data,pen = 'g')
    
    # plot the max hold curve
    max_curve.setData(x=freq_range,y=max_hold,pen = 'y')
 
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(10)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
