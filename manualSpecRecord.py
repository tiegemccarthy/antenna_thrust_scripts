#!/usr/bin/python

import sys
import os
import socket
import time
import numpy as np

cwd = os.getcwd()
input_time = int(input('Enter the amount of seconds you want to run this: '))
output_file = str(input('Enter name for output text file: '))

def spectrumGrab(RBW_byte, VBW_byte):
    s=socket.socket()
    s.connect(('131.217.63.179', 5025))
    s.send(b'FREQ:SPAN 1GHZ\rn\n')
    s.send(b'BAND:RES ' + RBW_byte + b'; VID ' + VBW_byte + b'\rn\n')
    time.sleep(0.5)
    s.send(b'FREQ:CENT 505MHZ\r\n')
    s.send(b'TRAC? TRACE2\r\n')
    time.sleep(0.5)
    a=s.recv(16384)
    a_list = a.decode("utf-8").split(',')
    float_list = [float(point) for point in a_list]
    return float_list 
    
def main(max_time, filename):
    start_time = time.time()
    spec_list = []
    try:
        while (time.time() - start_time) < max_time:
            spectrum = spectrumGrab(b'3 MHZ', b'10 MHZ')
            spec_list.append(spectrum)
        spec_array = np.array(spec_list) # covert list of lists to a X by Y array
        np.savetxt(cwd + '/' + filename + '.txt', spec_array, delimiter=",")
    except KeyboardInterrupt:
        if len(spec_list) > 0:
            print('Interrupted - writing out currently recorded spectra.')
            spec_array = np.array(spec_list) # covert list of lists to a X by Y array
            np.savetxt(cwd + '/' + filename + '.txt', spec_array, delimiter=",")
        else:
            print('Interrupted.')
            
if __name__ == '__main__':
    main(input_time, output_file)
