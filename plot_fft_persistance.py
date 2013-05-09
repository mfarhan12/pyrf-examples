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
fft_plot = win.addPlot(title="Power Vs. Frequency")

# initialize axes limits
plot_xmin = (center_freq) - (bandwidth / 2)
plot_xmax = (center_freq) + (bandwidth / 2)

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

# initialize multiple curves to represent multiple colours
number_of_curves = 128
number_of_fade_curves = 5
curve = []
curve = [None] * number_of_curves
for i in range(number_of_curves):    
    curve[i] = fft_plot.plot(pen='g')

fade_curve = []
fade_curve = [None] * number_of_fade_curves
for i in range(number_of_fade_curves):    
    fade_curve[i] = fft_plot.plot(pen='g')
    
cont_pow_data = np.zeros([number_of_fade_curves,SAMPLE_SIZE]) + 500


def update():
    global dut, curve, fft_plot, freq_range, center_freq, bandwidth, cont_pow_data, fade_curve
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

    for i in range(number_of_fade_curves):

        #fade_curve[i].setData(freq_range,cont_pow_data[i,:],pen = (255,0,255,i * (255 / number_of_fade_curves)) )
        
        if i ==  number_of_fade_curves - 1:
            cont_pow_data[i,:] = powData
        else:
            cont_pow_data[i,:] = cont_pow_data[i + 1,:]
    
    variance = np.zeros(number_of_curves)
    for i in range(number_of_curves):
        variance[i] = np.std(cont_pow_data[:,i])
        
        if variance[i] < 10:
            color = 'r'
        else:
            color = 'b'
            
        x = np.array(freq_range[i * 8:(i * 8) + 7])
        y = np.array(powData[i * 8:(i * 8) + 7])
        if i == 57:
            color = 'g'
        curve[i].setData(x,y,pen = color)

    
   


timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
