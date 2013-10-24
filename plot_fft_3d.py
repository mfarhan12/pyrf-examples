#!/usr/bin/python

# import all the necessary Libraries
import sys
import numpy as np

from pyrf.devices.thinkrf import WSA4000
from pyrf.util import read_data_and_context
from pyrf.config import TriggerSettings
from pyrf.numpy_util import compute_fft

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph.opengl as gl
from pyqtgraph_util import represent_fft_to_plot
from pyqtgraph_util import create_color_heatmap

# hold a constant reflevel
STATIC_REFLEVEL = -35
xSize = 128
ySize = 150

dut = WSA4000()
dut.connect(sys.argv[1])
powerSize = dut.spp()

if len(sys.argv) > 2:
    center_freq = int(sys.argv[2]) * 1e6
else:
    center_freq = 2450e6

# setup WSA settings
dut.reset()
dut.request_read_perm()
dut.ifgain(0)
dut.freq(center_freq)
dut.gain('high')
dut.fshift(0)
dut.decimation(0)

# Create a GL View widget to display data
app = QtGui.QApplication([])
w = gl.GLViewWidget()

w.show()
w.setWindowTitle('PYRF pyqtgraph example: 3D FFT Plot')

w.setCameraPosition(distance=100)

# add grid
gridSize = QtGui.QVector3D(4,5,6)
g = gl.GLGridItem(size=gridSize)
g.scale(5.85,5,0)
w.addItem(g)

# the initial plot data before data is received
z = np.random.normal(size=(xSize,ySize))

# initialize the x-y boundries of the plot
x = np.linspace(-73.5, 144.3, xSize)
y = np.linspace(0.1, 5, ySize)

# initialize the colors of the plots (light blue)
colors = np.ones((xSize,ySize,4), dtype=float)
colors[:,:,0] = 0
colors[:,:,1] = 0.4
colors[:,:,2] = 1

# plot the data
p3 = gl.GLSurfacePlotItem(x = x, y = y, z = z, shader = 'shaded',
                            colors = colors.reshape(xSize*ySize,4), smooth=False)

# determine the size
p3.scale(16./49., 20, 0.1)

# determine the location on the gride
p3.translate(-12, -50, 0)
w.addItem(p3)
w.pan(-10,-10,-10)
def update():
    # update the plot to show new data
    global p3, z, colors
    
    # read data
    data, context = read_data_and_context(dut, powerSize)
    
    # ignore the reference level so plot doesn't change positions
    context['reflevel'] = STATIC_REFLEVEL
    # compute the fft of the complex data
    powData = compute_fft(dut, data, context)
    zData = represent_fft_to_plot(powData)

    # move the data stream as well as colours back to show new data
    for i in range (ySize):
        if i == 0:
            continue
        else:
            colors[:,ySize - i,:] = colors[:, ySize - i - 1,:]
            z[:,ySize - i] = z[:, ySize - i - 1]
        z[:,0] = zData[:,0]

    # grab new color
    colors[:,0,:] = create_color_heatmap(powData)
    colors[:,1,:] = create_color_heatmap(powData)
    
    # update the plot
    p3.setData(z = z, colors = colors.reshape(xSize*ySize,4))

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(5)
  
## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
  
  