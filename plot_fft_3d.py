#!/usr/bin/python

import sys

from pyqtgraph.Qt import QtCore, QtGui
import pyqtgraph as pg
import pyqtgraph.opengl as gl
import scipy.ndimage as ndi
import numpy as np
from pyrf.devices.thinkrf import WSA4000
from pyrf.util import read_data_and_reflevel
from pyrf.numpy_util import compute_fft
from pyqtgraph_util import represent_fft_to_plot
from pyqtgraph_util import create_color_heatmap

zSize = 128

STATIC_REFLEVEL = -35
dut = WSA4000()
dut.connect('10.126.110.101')
powerSize = dut.spp()
dut.request_read_perm()
## Create a GL View widget to display data
app = QtGui.QApplication([])
w = gl.GLViewWidget()

w.show()
w.setWindowTitle('pyqtgraph example: GLSurfacePlot')
w.setCameraPosition(distance=100)

# add grid
gridSize = QtGui.QVector3D(4,5,6)
g = gl.GLGridItem(size=gridSize)
g.scale(5.85,5,0)
g.setDepthValue(1)

w.addItem(g)

xSize = 128
ySize = 150

## Manually specified colors
z = np.random.normal(size=(xSize,ySize))

x = np.linspace(-73.5, 144.3, xSize)
y = np.linspace(50, 300, ySize)
colors = np.ones((xSize,ySize,4), dtype=float)
colors[:,:,0] = 0
colors[:,:,1] = 0
colors[:,:,2] = 1

p3 = gl.GLSurfacePlotItem(z=z,x=x, y=y,colors=colors.reshape(xSize*ySize,4), shader='shaded', smooth=False)

# determine the size
p3.scale(16./49., 16./49., 1.0)

# determine the location on the gride
p3.translate(-12, -50, 0)
w.addItem(p3)

w.pan(-10,-10,-10)
def update():
    global p3, z, colors
    zSize = 128
    powerSize = 2048
    data, reflevel = read_data_and_reflevel(dut, powerSize)

    reflevel.fields['reflevel'] = -35
    # compute the fft of the complex data
    powData = compute_fft(dut, data, reflevel)
    
    zData = represent_fft_to_plot(powData)
    x = 0
    for i in range (ySize):
        if i == 0:
            continue
        else:
            colors[:,ySize - i,:] = colors[:, ySize - i - 1,:]
            z[:,ySize - i] = z[:, ySize - i - 1]
        z[:,0] = zData[:,0]

    colors[:,0,:] = create_color_heatmap(powData)
    colors[:,1,:] = create_color_heatmap(powData)
    p3.setData(z=z, colors=colors.reshape(xSize*ySize,4))

timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(0.11)
  
## Start Qt event loop unless running in interactive mode.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()
  