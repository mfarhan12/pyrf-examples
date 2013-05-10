import numpy as np

PLOT_SIZE = 128
MAX_DBM_DIFFERENCE = 60

def represent_fft_to_plot(pow_data):
    # represent an FFT in a 128 integer array to be represented in a 3D plot
    
    zData = np.zeros(shape =(PLOT_SIZE,1))
    fftSize = len(pow_data)
    for i in range(PLOT_SIZE):
        startIndex = i * (fftSize / PLOT_SIZE)
        endIndex = (i * (fftSize / PLOT_SIZE)) + ((fftSize / PLOT_SIZE) - 1)
        zData[i] = (np.amax(pow_data[startIndex:endIndex]) + 100)
    
    return zData
    
def create_color_heatmap(pow_data):
# create a colored array to represent an FFT
    
    fftSize = len(pow_data)
    colorArray = np.ones((PLOT_SIZE,4), dtype = float)
    pow_dataAverage = np.average(pow_data)
    pow_dataMin = pow_dataAverage - 5
    pow_dataMax = pow_dataAverage + (-1 *  pow_dataMin)+ MAX_DBM_DIFFERENCE
    
    for i in range(PLOT_SIZE):
        startIndex = i * (fftSize / PLOT_SIZE)
        endIndex = (i * (fftSize / PLOT_SIZE)) + ((fftSize / PLOT_SIZE) - 1)
        fftAreaMax = np.amax(pow_data[startIndex:endIndex]) 
        
        # max data is red
        if fftAreaMax > pow_dataMax:
            colorArray[i,0] = 1
            colorArray[i,1] = 0
            colorArray[i,2] = 0
            continue
        # min data is blue
        elif fftAreaMax < pow_dataMin :
            colorArray[i,0] = 0
            colorArray[i,1] = 0
            colorArray[i,2] = 1
            continue
        
        # scale everything in between    
        scaledVal = fftAreaMax + (-1 * pow_dataMin)
        
        # colours for lower bound (blue - green transition)
        if scaledVal < (pow_dataMax/2):
            colorArray[i,0] = 0
            colorArray[i,1] = 0.2 + scaledVal/pow_dataMax
            colorArray[i,2] = 1 - (scaledVal/pow_dataMax)
        
        # colours for upper bound (green - red transition)
        elif scaledVal >= (pow_dataMax/2):
            colorArray[i,0] = scaledVal/pow_dataMax
            colorArray[i,1] = 1 - (scaledVal/pow_dataMax)
            colorArray[i,2] = 0
       
    return colorArray
    
        
def find_max_index(array):
    # returns the maximum index of an array         
    
    # keep track of max index
    index = 0
    
    array_size = len(array)
    
    max_value = 0
    for i in range(array_size):
        
        if i == 0:
            max_value = array[i]
            index = i
        elif array[i] > max_value:
            max_value = array[i]
            index = i
    
    
    return index
    
    