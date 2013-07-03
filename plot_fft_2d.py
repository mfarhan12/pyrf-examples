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
CENTER_FREQ = 2450 * 1e6 
SAMPLE_SIZE = 1024
RF_GAIN = 'high'
IF_GAIN = 0
DECIMATION = 4
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
dut.freq(CENTER_FREQ)
dut.gain(RF_GAIN)
dut.ifgain(IF_GAIN)
dut.fshift(FREQ_SHIFT)
dut.decimation(DECIMATION)

# initialize plot
fft_plot = win.addPlot(title="Power Vs. Frequency")

# initialize axes limits
plot_xmin = (CENTER_FREQ) - (bandwidth / 2)
plot_xmax = (CENTER_FREQ) + (bandwidth / 2)

plot_ymin = -130
plot_ymax = 20

# initialize the x-axis of the plot
fft_plot.setXRange(plot_xmin,plot_xmax)
fft_plot.setLabel('bottom', text= 'Frequency', units = 'Hz', unitPrefix=None)

# initialize the y-axis of the plot
fft_plot.setYRange(plot_ymin ,plot_ymax)
fft_plot.setLabel('left', text= 'Power', units = 'dBm', unitPrefix=None)

# disable auto size of the x-y axis
fft_plot.enableAutoRange('xy', False)

# initialize a curve for the plot 
curve = fft_plot.plot(pen='g')

def update():
    global dut, curve, fft_plot, CENTER_FREQ, bandwidth
    # read data
    data, context = read_data_and_context(dut, SAMPLE_SIZE)
    CENTER_FREQ = context['rffreq']
    bandwidth = context['bandwidth']
    
    # update axes limits
    plot_xmin = (CENTER_FREQ) - (bandwidth / 2)
    plot_xmax = (CENTER_FREQ) + (bandwidth / 2)
    
    # update the frequency range (Hz)
    freq_range = np.linspace(plot_xmin , plot_xmax, SAMPLE_SIZE)
    
    # initialize the x-axis of the plot
    fft_plot.setXRange(plot_xmin,plot_xmax)
    fft_plot.setLabel('bottom', text= 'Frequency', units = 'Hz', unitPrefix=None)
    
    # compute the fft and plot the data
    pow_data = compute_fft(dut, data, context)
    curve.setData(freq_range,pow_data, pen = 'g')

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
