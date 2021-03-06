#!/usr/bin/python

from astropy.io import ascii
import numpy as np
import os
from astropy.time import Time
from datetime import datetime, timedelta
import time 
import socket
import sys

cwd = os.getcwd()

def spectrumGrab():
    s=socket.socket()
    s.connect(('131.217.63.179', 5025))
    s.send(b'FREQ:SPAN 999MHZ\rn\n')
    s.send(b'FREQ:CENT 505MHZ\r\n')
    s.send(b'SWE:POIN 333\r\n')
    s.send(b'TRAC? TRACE2\r\n')
    time.sleep(0.8)
    a=s.recv(16384)
    if len(a) == 5994: # will need to change this if you change number of sweep points! Test the expected length then update script - stops incomplete scans getting appended.
        a_list = a.decode("utf-8").split(',')
        try:
            float_list = [float(point) for point in a_list]
        except: # this handles the rare instance when a trace is not correctly received from the spectrum analyser
            float_list = ''
    else:
        float_list = ''
    return float_list 
    
def writeOut(spectra_list, scan_time_list, on_off, current_scan_element):
    spec_array = np.array(spectra_list) # covert list of lists to a X by Y array
    np.savetxt(cwd + '/' + str(scan_time_list[current_scan_element]) + '.txt', spec_array, header='Scan start time: ' + str(scan_time_list[current_scan_element]) + ' jd', delimiter=",", fmt='%s')
    print("File for scan " + str(scan_time_list[current_scan_element]) + " written out.")   
    

def main(scantime_file):
    # load in the scaninfo file output by the schedule generator
    print("Loading scan time file.")
    with open(scantime_file, 'r') as f:
        time_data = [float(line.split()[0]) for line in f]
    scan_times = Time(time_data, format='jd', scale='utc')
    # make frequency range axis for output - assuming 1 GHz range (from 1.1 to 2.1 GHz) and 501 sweep points
    x_inc = 999.0/333.0
    freq_range = np.arange(1100,2100,x_inc)
    # start the recording
    print("Starting recording loop.")
    spec_list = []
    try:
        while True:
            currenttime = Time(datetime.utcnow()) # grab current UTC time
            for i in range(0, len(scan_times)-1): 
                if scan_times[i+1] > currenttime > (scan_times[i] + timedelta(seconds=5)): # check whether current time falls within 90s of the start of any scan and the end of that same scan
                    #if not os.path.exists(cwd + '/' + str(scan_times[i]) + '.dat'): # create a data file for this scan if it doesn't already exist
                    #    open(cwd + '/' + str(scan_times[i]) + '.txt', 'a').close()
                    spectrum = spectrumGrab() # grab the spectrum at this time
                    spec_list.append(spectrum) # append it to the list containing all spectra for this current scan
                    time.sleep(0.2)
                    current_scan = i # this is used for writing out the data between scans
                    break    
                elif i == len(scan_times)-2 and len(spec_list) > 0: # if spectrum data exists and the iterator maxes out then we are between scans - here we write out the data to a file
                    writeOut(spec_list, scan_times, current_scan)
                    spec_list = []
                else:
                    continue                
    except KeyboardInterrupt:
        if len(spec_list) > 0:
            print('Interrupted - writing out currently recorded spectra.')
            writeOut(spec_list, scan_times, current_scan)
            spec_list = []
    else:
        print('Interrupted')

if __name__ == '__main__':
    main(sys.argv[1])
