#!/usr/bin/python

# import required libraries
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyrf.devices.thinkrf import WSA4000
from pyrf.util import read_data_and_context
from pyrf.config import TriggerSettings
from pyrf.numpy_util import compute_fft
from pyqtgraph_util import convert_freq_to_index
import sys
import gc
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
win.resize(1000,600)
win.setWindowTitle("PYRF FFT Plot Example")

# add the label to display the position
label = pg.LabelItem(justify='right')
win.addItem(label)

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

# initialize region selection lines
region_selection_lines = pg.LinearRegionItem([CENTER_FREQ - 10e6,CENTER_FREQ + 10e6])
region_selection_lines.setZValue(-10)   
fft_plot.addItem(region_selection_lines)

def update():
    global dut, curve, fft_plot, freq_range
    gc.collect()
    # read data
    data, context = read_data_and_context(dut, SAMPLE_SIZE)
    center_freq = context['rffreq']
    bandwidth = context['bandwidth']
    
    # update axes limits
    plot_xmin = (center_freq) - (bandwidth / 2)
    plot_xmax = (center_freq) + (bandwidth / 2)

    # update the frequency range (Hz)
    freq_range = np.linspace(plot_xmin , plot_xmax, SAMPLE_SIZE)
    
    # initialize the x-axis of the plot
    fft_plot.setXRange(plot_xmin,plot_xmax)
    fft_plot.setLabel('bottom', text= 'Frequency', units = 'Hz', unitPrefix=None)
    
    # compute the fft and plot the data
    powData = compute_fft(dut, data, context)
    
    # grab new cursor region
    cursor_region = region_selection_lines.getRegion()
    index_region = np.zeros(2)

    index_region[0] =  int((cursor_region[0] - plot_xmin) * SAMPLE_SIZE/bandwidth)
    if index_region[0] < 0:
        index_region[0] = 0
    
    index_region[1] =  int((cursor_region[1] - plot_xmin) * SAMPLE_SIZE/bandwidth)
    if index_region[1] > SAMPLE_SIZE:
        index_region[1] = SAMPLE_SIZE
    
    print index_region[1]
    curve.setData(freq_range,powData, pen = 'g')
  
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
