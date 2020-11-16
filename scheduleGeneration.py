#!/usr/bin/python
from astropy.io import ascii
import sys
import numpy as np
import math
import os

cwd = os.getcwd()

def main(input_file, exp_code):
    exp_code = str(exp_code)
    # Load data from CSV file
    data = ascii.read(input_file)
    # Convert data into desired form
    az_deg = data['un_az']*180*(1/np.pi)
    el_deg = data['el']*180*(1/np.pi)
    jd = data['jd']
    # Generate master schedule file
    with open(exp_code+'_master.out', 'w') as f:
        for i in range(0, len(data)):
            print("JD : " + format(jd[i], '.8f') + " ; Az : " + format(az_deg[i], '.3f') + " ; El : " + format(el_deg[i], '.3f') + " ; Rn :    0.0 ", file=f)
    # Now generate block schedule
    interval = 0.00347
    start_time = jd[0]
    end_time = max(jd)
    num_scans = math.ceil((end_time - start_time)/interval) # calculate how many 5 min chunks are needed rounded up
    scantime_array = np.arange(start_time, start_time + (num_scans+0.1)*interval, interval) # the 0.1 makes sure we have a final value > the end time
    with open(exp_code+'_master.out', 'r') as file_read:
        if not os.path.exists(cwd + '/' + exp_code+'_blocks'): # check if subdir exists
            os.mkdir(cwd + '/' + exp_code+'_blocks') # create if it does not
        for line in file_read: # iterate through each line of master schedule file
            jd_time = float(line[5:21]) # extract JD time value
            scan_index = max(np.where((jd_time/scantime_array) >= 1)[0]) # determine the scan that the given time will fall on
            block_file_name = exp_code + '_b' + str(scan_index+1).zfill(3) + '.out' # determine the name of that scan's file
            with open(cwd + '/' + exp_code+'_blocks/' + block_file_name , 'a') as file_write: # write the data to the relevant file
                print(str.rstrip(line), file=file_write) # strip \n before printing
    
    # create shell script wrapper
    if os.path.exists(cwd + '/'+exp_code+ '_wrapper.sh'):
        os.remove(cwd + '/'+exp_code+ '_wrapper.sh')
    # generate new script
    with open(cwd + '/'+exp_code+ '_wrapper.sh', 'w') as f:
        print('#!/bin/bash', file=f) # append shebang to shell script
        block_list = sorted(os.listdir(cwd + '/'+exp_code+'_blocks')) # read block schedule subdirectory
        for i in range(0, len(block_list)):
            if (i % 2) == 0: # if even track normally
                print('sattrk -b -d 1/xs -i ' + block_list[i] + ' sys26m', file=f)
            else: # if odd track with offset
                print('sattrk -b -d 1/xs -x 2 -i ' + block_list[i] + ' sys26m', file=f) 
    
    
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

