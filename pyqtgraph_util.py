import numpy as np

PLOT_SIZE = 128
MAX_DBM_DIFFERENCE = 60
def represent_fft_to_plot(powData):
    # represent an FFT in a 128 integer array to be represented in a 3D plot
    
    zData = np.zeros(shape =(PLOT_SIZE,1))
    fftSize = len(powData)
    for i in range(PLOT_SIZE):
        startIndex = i * (fftSize / PLOT_SIZE)
        endIndex = (i * (fftSize / PLOT_SIZE)) + ((fftSize / PLOT_SIZE) - 1)
        zData[i] = (np.amax(powData[startIndex:endIndex]) + 100) / 10
    
    return zData
    
def create_color_heatmap(powData):
# create a colored array to represent an FFT
    fftSize = len(powData)
    colorArray = np.ones((PLOT_SIZE,4), dtype = float)
    powDataAverage = np.average(powData)
    powDataMin = powDataAverage - 5
    powDataMax = powDataAverage + (-1 *  powDataMin)+ MAX_DBM_DIFFERENCE
    for i in range(PLOT_SIZE):
        startIndex = i * (fftSize / PLOT_SIZE)
        endIndex = (i * (fftSize / PLOT_SIZE)) + ((fftSize / PLOT_SIZE) - 1)
        fftAreaMax = np.amax(powData[startIndex:endIndex]) 
        if fftAreaMax > powDataMax:
            colorArray[i,0] = 1
            colorArray[i,1] = 0
            colorArray[i,2] = 0
            continue
        
        elif fftAreaMax < powDataMin :
            colorArray[i,0] = 0
            colorArray[i,1] = 0
            colorArray[i,2] = 1
            continue
        scaledVal = fftAreaMax + (-1 * powDataMin)
        
        if scaledVal < (powDataMax/2):
            colorArray[i,0] = 0
            colorArray[i,1] = 0.2 + scaledVal/powDataMax
            colorArray[i,2] = 1 - (scaledVal/powDataMax)
        
        elif scaledVal >= (powDataMax/2):
            colorArray[i,0] = scaledVal/powDataMax
            colorArray[i,1] = 1 - (scaledVal/powDataMax)
            colorArray[i,2] = 0
       
    return colorArray
    
    
    
    