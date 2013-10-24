#!/usr/bin/python

# import required libraries
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyrf.devices.thinkrf import WSA4000
import sys
from pyrf.numpy_util import compute_fft, _calibrate_i_q
from pyrf.util import read_data_and_context
import heapq
# plot constants
center_freq = 16000 * 1e6 
SAMPLE_SIZE = 2048
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
dut.scpiset(':INPUT:ATTENUATOR 0')
dut.scpiset(':INPUT:MODE  HDR')
if len(sys.argv) > 2:
    center_freq = int(sys.argv[2]) * 1e6
    
if len(sys.argv) > 3:
    ref = int(sys.argv[3])
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


plot.setLabel('bottom', text= 'Time', units = None, unitPrefix=None)

# initialize the y-axis of the plot
plot.setYRange(plot_ymin ,plot_ymax)


# initialize the i-q curves for the plot 
i_curve = plot.plot()
q_curve = plot.plot()
# update axes limits
plot_xmin = (center_freq) - (bandwidth / 2)
plot_xmax = (center_freq) + (bandwidth / 2)
    

fftPlot.showGrid(True, True)

fftPlot.setYRange(20 , -130)
fft_curve = fftPlot.plot()
qfft_curve = fftPlot.plot()
fftPlot.setXRange(plot_xmin, plot_xmax)
def update():

    global dut, i_curve, q_curve, fft_curve,qfft_curve, fftPlot, ref
    
    # read data
    data, context = read_data_and_context(dut, SAMPLE_SIZE)
    
    iq_data = data.data.numpy_array()
    
    i_data = np.array(iq_data, dtype=float)

    # q_data = _calibrate_i_q(i_data, q_data)
    pow_data = compute_fft(dut,data,context)

    center_freq = context['rffreq']
    bandwidth = context['bandwidth']

    # print noiselevel_offset
    # update axes limits
    plot_xmin = (center_freq) - (bandwidth / 2)
    plot_xmax = (center_freq) + (bandwidth / 2)
    fftPlot.setXRange(plot_xmin, plot_xmax)
    
    # update the frequency range (Hz)
    freq_range2 = np.linspace(plot_xmin , plot_xmax, len(pow_data))
   
    i_curve.setData(freq_range, i_data, pen = 'g')
    # print np.mean(pow_data)
    fft_curve.setData(x = freq_range2, y = pow_data, pen = 'g')    
    # qfft_curve.setData(x = freq_range2, y = q_pow - 100, pen = 'r')  
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
