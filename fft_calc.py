import math
import numpy
import time
def _compute_fft(i_data, q_data, noise_off):
    i_removed_dc_offset = i_data - numpy.mean(i_data)
    q_removed_dc_offset = q_data - numpy.mean(q_data)
    calibrated_q = _calibrate_i_q(i_removed_dc_offset, q_removed_dc_offset)
    iq = i_removed_dc_offset + 1j * calibrated_q
    
    windowed_iq = iq * numpy.hanning(len(i_data))

    power_spectrum = numpy.fft.fftshift(numpy.fft.fft(windowed_iq))
    power_spectrum = 20 * numpy.log10(numpy.abs(power_spectrum)/len(power_spectrum))

    median_index = len(power_spectrum) // 2
    power_spectrum[median_index] = (power_spectrum[median_index - 1]
        + power_spectrum[median_index + 1]) / 2
    return power_spectrum + noise_off

def _calibrate_i_q(i_data, q_data):

    samples = len(i_data)

    sum_of_squares_i = sum(i_data ** 2)
    sum_of_squares_q = sum(q_data ** 2)

    amplitude = math.sqrt(sum_of_squares_i * 2 / samples)
    ratio = math.sqrt(sum_of_squares_i / sum_of_squares_q)

    p = (q_data / amplitude) * ratio * (i_data / amplitude)

    sinphi = 2 * sum(p) / samples
    phi_est = -math.asin(sinphi)

    return (math.sin(phi_est) * i_data + ratio * q_data) / math.cos(phi_est) 
    
    
def read_data_and_context(dut, points=1024):
    """
    Wait for and capture a data packet and collect preceeding context packets.

    :returns: (data_pkt, context_values)

    Where context_values is a dict of {field_name: value} items from
    all the context packets received.
    """
    # capture 1 packet
    dut.capture(points, 1)
    
    context_values = {}
    # read until I get 1 data packet
    while not dut.eof():
        pkt = dut.read()

        if pkt.is_data_packet():
            break

        context_values.update(pkt.fields)

    return pkt, context_values

# avoid breaking pyrf 0.2.x examples:
read_data_and_reflevel = read_data_and_context