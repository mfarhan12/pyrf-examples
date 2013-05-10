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
import gc
import msvcrt

# plot constants
CENTER_FREQ = 2450 * 1e6 
SAMPLE_SIZE = 1024
RF_GAIN = 'high'
IF_GAIN = 0
DECIMATION = 1
bandwidth = (125 *1e6) / DECIMATION
FREQ_SHIFT = 0

# declare the GUI
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="ThinkRF FFT Plot Example")

label = pg.LabelItem(justify='right')
win.addItem(label)
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
fft_plot = win.addPlot(title="Power Vs. Frequency",row=1, col =0)
fft_plot.setAutoVisible(y=True)

# initialize axes limits
plot_xmin = (CENTER_FREQ) - (bandwidth / 2)
plot_xmax = (CENTER_FREQ) + (bandwidth / 2)

plot_ymin = -130
plot_ymax = 20

# initialize the frequency range (Hz)
freq_range = np.linspace(plot_xmin , plot_xmax, SAMPLE_SIZE)

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

# add a scatter plot to plot the maximum point
max_location = pg.ScatterPlotItem()
fft_plot.addItem(max_location)

def update():
    global dut, curve, fft_plot, freq_range, max_location

    # read data
    data, context = read_data_and_context(dut, SAMPLE_SIZE)
    
    # retrieve freq and bandwidth to update axis
    center_freq = context['rffreq']
    bandwidth = context['bandwidth']
    
    # update axes limits
    plot_xmin = (center_freq) - (bandwidth / 2)
    plot_xmax = (center_freq) + (bandwidth / 2)

    # update the frequency range (Hz)
    freq_range = np.linspace(plot_xmin , plot_xmax, SAMPLE_SIZE)
    
    # update the x-axis of the plot
    fft_plot.setXRange(plot_xmin,plot_xmax)
    fft_plot.setLabel('bottom', text= 'Frequency', units = 'Hz', unitPrefix=None)
    
    # compute the fft and plot the data
    pow_data = compute_fft(dut, data, context)
           
    # determine the index of the maximum point
    max_index = np.argmax(pow_data)
    
    # retrieve maximum power and freq of max power
    max_freq = freq_range[max_index]
    max_pow = pow_data[max_index]
    
    # update label
    label.setText("<span style='color: green'>Max Frequency Location=%0.1f MHz,  Power=%0.1f dBm</span>" % (max_freq/1e6, max_pow))

    # TODO: Find a better way then using an array with small random values
    # create array of small numbers
    pos = np.random.normal(size=(2,1), scale=1e-9)
    
    # update scatter plot
    max_location.setData(x =pos[0] + max_freq , y =  pos[0] + max_pow, size = 20, symbol = 't')
    
    # update fft curve
    curve.setData(freq_range,pow_data, pen = 'g')
  
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
