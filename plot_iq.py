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
SAMPLE_SIZE = 2048
RF_GAIN = 'high'
IF_GAIN = 0
DECIMATION = 1
bandwidth = (125 *1e6) / DECIMATION
FREQ_SHIFT = 0

# declare the GUI
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="ThinkRF FFT Plot Example")
win.resize(1000,600)
win.setWindowTitle("PYRF FFT Plot Example")

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

# initialize plot
fft_plot = win.addPlot(title="IQ Plot")

# initialize axes limits
plot_xmin = 0
plot_xmax = 1000

plot_ymin = -1
plot_ymax = 1

# initialize the frequency range (Hz)
freq_range = np.linspace(plot_xmin , plot_xmax, SAMPLE_SIZE)

# initialize the x-axis of the plot
fft_plot.setXRange(plot_xmin,plot_xmax)
fft_plot.setLabel('bottom', text= 'Time', units = None, unitPrefix=None)

# initialize the y-axis of the plot
fft_plot.setYRange(plot_ymin ,plot_ymax)

# disable auto size of the x-y axis
fft_plot.enableAutoRange('xy', False)

# initialize the i-q curves for the plot 
i_curve = fft_plot.plot(pen='g')
q_curve = fft_plot.plot(pen='r')
def update():
    global dut, i_curve, q_curve
    
    # read data
    data, context = read_data_and_context(dut, SAMPLE_SIZE)
    iq_data = data.data.numpy_array()
    
    # extract i and q data and normalize
    i_data = (np.array(iq_data[:,0], dtype=float)) / 8192
    q_data = (np.array(iq_data[:,1], dtype=float)) / 8192
    
    # update curves
    i_curve.setData(freq_range, i_data, pen = 'g')
    q_curve.setData(freq_range, q_data, pen = 'r')
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
