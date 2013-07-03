#!/usr/bin/python

# import required libraries
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from pyrf.devices.thinkrf import WSA4000
from pyrf.sweep_device import SweepDevice
import sys

# plot constants
START_FREQ = 2400e6 
STOP_FREQ = 2700e6
CENTER_FREQ = ((STOP_FREQ - START_FREQ) / 2) + START_FREQ
SAMPLE_SIZE = 1024
RF_GAIN = 'high'
FREQ_SHIFT = 0

# declare the GUI
app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="ThinkRF FFT Plot Example")
win.resize(1000,600)
win.setWindowTitle("PYRF FFT Plot Example")

# connect to WSA4000 device
dut = WSA4000()
dut.connect(sys.argv[1])
sd = SweepDevice(dut)
# initialize plot
fft_plot = win.addPlot(title="Power Vs. Frequency")


plot_ymin = -130
plot_ymax = 20



    
# initialize the x-axis of the plot
fft_plot.setXRange(START_FREQ , STOP_FREQ)
fft_plot.setLabel('bottom', text= 'Frequency', units = 'Hz', unitPrefix=None)

# initialize the y-axis of the plot
fft_plot.setYRange(plot_ymin ,plot_ymax)
fft_plot.setLabel('left', text= 'Power', units = 'dBm', unitPrefix=None)

# disable auto size of the x-y axis
fft_plot.enableAutoRange('xy', False)

# initialize a curve for the plot 
curve = fft_plot.plot(pen='g')

def update():
    global dut, curve, fft_plot, START_FREQ, STOP_FREQ, SAMPLE_SIZE, RF_GAIN
    # read data    
    fstart, fstop, pow_data = sd.capture_power_spectrum(START_FREQ, STOP_FREQ, SAMPLE_SIZE, rfgain = RF_GAIN, antenna = 1)
    
    # initialize the frequency range (Hz)
    freq_range = np.linspace(START_FREQ , STOP_FREQ, len(pow_data))
    curve.setData(freq_range,pow_data, pen = 'g')

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0)



## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
