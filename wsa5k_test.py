#!/usr/bin/python

# import required libraries
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyrf.devices.thinkrf import WSA4000
import sys
from numpy_util import compute_fft, _calibrate_i_q
from pyrf.util import read_data_and_context
import heapq
# plot constants
center_freq = 16000 * 1e6 
SAMPLE_SIZE = 4096
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
dut.request_read_perm()
dut.scpiset(':INPUT:ATTENUATOR DISABLED')
if len(sys.argv) == 3:
    center_freq = int(sys.argv[2]) * 1e6
dut.freq(center_freq)
dut.fshift(FREQ_SHIFT)
dut.decimation(DECIMATION)

# initialize plot
plot = win.addPlot(title="IQ Plot")
win.nextRow()
fftPlot = win.addPlot(title = 'FFT Plot')
# initialize axes limits
plot_xmin = 0
plot_xmax = 1000

plot_ymin = -400
plot_ymax = 800

# initialize the frequency range (Hz)
freq_range = np.linspace(plot_xmin , plot_xmax, SAMPLE_SIZE)

# initialize the x-axis of the plot
plot.setXRange(plot_xmin,plot_xmax)
plot.setLabel('bottom', text= 'Time', units = None, unitPrefix=None)

# initialize the y-axis of the plot
plot.setYRange(plot_ymin ,plot_ymax)

# disable auto size of the x-y axis
plot.enableAutoRange('xy', False)

# initialize the i-q curves for the plot 
i_curve = plot.plot()
q_curve = plot.plot()
# update axes limits
plot_xmin = (center_freq) - (bandwidth / 2)
plot_xmax = (center_freq) + (bandwidth / 2)
    
# initialize the x-axis of the plot
fftPlot.setXRange(2300e6, 2600e6)
fftPlot.showGrid(True, True)
fftPlot.enableAutoRange('xy', False)
fftPlot.setYRange(20 , -130)
fft_curve = fftPlot.plot()
fftPlot.setXRange(plot_xmin, plot_xmax)
def update():

    global dut, i_curve, q_curve, fft_curve, fftPlot
    
    # read data
    data, context = read_data_and_context(dut, SAMPLE_SIZE)
    
    iq_data = data.data.numpy_array()
    
    i_data = np.array(iq_data[:,0], dtype=float)
    q_data = np.array(iq_data[:,1], dtype=float)

    pow_data = compute_fft(dut,data,context)

    CENTER_FREQ = context['rffreq']
    bandwidth = context['bandwidth']
    # print noiselevel_offset
    # update axes limits
    plot_xmin = (CENTER_FREQ) - (bandwidth / 2)
    plot_xmax = (CENTER_FREQ) + (bandwidth / 2)
    # fftPlot.setXRange(plot_xmin, plot_xmax)
    
    # update the frequency range (Hz)
    freq_range2 = np.linspace(plot_xmin , plot_xmax, len(pow_data))
   
    i_curve.setData(freq_range, i_data, pen = 'g')
    q_curve.setData(freq_range, q_data, pen = 'r')
    # print np.mean(pow_data)
    fft_curve.setData(x = freq_range2, y = pow_data, pen = (0,255,236))    

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
