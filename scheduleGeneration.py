#!/usr/bin/python
from astropy.io import ascii
from astropy.time import Time
import sys
import numpy as np
import math
import os
from datetime import timedelta

# This script takes a CSV file of a satellite track from the data structures created in MATLAB - located at /LEVEL5/sched_data.scan.stat.epoch.
# The CSV file is then converted into a format readable by the sattrk software on the Hobart 26m telescope.
# Input:
#       CSV filename 
#       Experiment code - for file naming purposes
# Output:
#       <experiment_code>_master.out - sattrk readable schedule for the whole track.
#       <experiment_code>_blocks/<experiment_code>_bXXX.out - directory containing a series of 5 minute schedule blocks used to alternate between 'onsource' and offset tracks of the satellite.
#       <experiment_code>_wrapper.sh - shell script wrapper to feed alternating scheudle blocks into sattrk software with offsets on every other scan.
#       <experiment_code>_scantimes.out - text file with julian date start times for each 5 minute schedule block - this is required by the spectrum analyser recording script.
# Example:
#       ./scheduleGeneration.py azel.csv at0001

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
    print('Creating master schedule file.')
    with open(exp_code+'_master.out', 'w') as f:
        for i in range(0, len(data)):
            print("JD : " + format(jd[i], '.8f') + " ; Az : " + format(az_deg[i], '.3f') + " ; El : " + format(el_deg[i], '.3f') + " ; Rn :    0.0 ", file=f)
    print('Done!')
    # Now generate block schedule
    print('Generating schedule blocks.')
    interval = 0.00347 # 5 minutes in fraction of day
    start_time = jd[0]
    end_time = max(jd)
    num_scans = math.ceil((end_time - start_time)/interval) # calculate how many 5 min chunks are needed rounded up
    scantime_array = np.arange(start_time, start_time + (num_scans+0.1)*interval, interval) # the 0.1 makes sure we have a final value > the end time
    with open(exp_code+'_master.out', 'r') as file_read:
        if not os.path.exists(cwd + '/' + exp_code+'_blocks'): # check if subdir exists
            os.mkdir(cwd + '/' + exp_code+'_blocks') # create if it does not
        for line in file_read: # iterate through each line of master schedule file
            jd_time = float(line[5:21]) # extract JD time value
            scan_index = max(np.where((round(jd_time,8)/np.around(scantime_array, 8)) >= 1.0)[0]) # determine the scan that the given time will fall on - rounding required because of floating point rounding errors
            block_file_name = exp_code + '_b' + str(scan_index+1).zfill(3) + '.out' # determine the name of that scan's file
            with open(cwd + '/' + exp_code+'_blocks/' + block_file_name , 'a') as file_write: # write the data to the relevant file
                print(str.rstrip(line), file=file_write) # strip \n before printing
    print('Done!')
    # create shell script wrapper
    print('Creating shell script wrapper.')
    if os.path.exists(cwd + '/'+exp_code+ '_wrapper.sh'):
        os.remove(cwd + '/'+exp_code+ '_wrapper.sh')
    scan_times = Time(scantime_array, format='jd', scale='utc')
    scan_times.format = 'isot'
    with open(cwd + '/'+exp_code+ '_wrapper.sh', 'w') as f:
        print('#!/bin/bash\n', file=f) # append shebang to shell scripts
        print('currenttime=$(date +%s)\n', file=f) 
        block_list = sorted(os.listdir(cwd + '/'+exp_code+'_blocks')) # read block schedule subdirectory
        for i in range(0, len(block_list)):
            if (i % 2) == 0: # if even track normally
                print('if [ $currenttime -le $(date -d ' + str(scan_times[i]+ timedelta(seconds=30)) + ' +%s) ]',file=f) # extra 30s is to account for the few seconds it takes for previous sattrk scan to finish
                print('then\n    sattrk -b -d 1/xs -i ' + block_list[i] + ' sys26m\nfi\n', file=f)
            else: # if odd track with offset
                print('if [ $currenttime -le $(date -d ' + str(scan_times[i]+ timedelta(seconds=30)) + ' +%s) ]',file=f) # extra 30s is to account for the few seconds it takes for previous sattrk scan to finish
                print('then\n    sattrk -b -d 1/xs -x 2 -i ' + block_list[i] + ' sys26m\nfi\n', file=f) 
    print('Done!')
    # Write out the start times of each 5 min block - for use with spectrum analyser recording
    print('Writing out schedule block start times.')
    if os.path.exists(cwd + '/'+exp_code+ '_scantimes.out'):
        os.remove(cwd + '/'+exp_code+ '_scantimes.out')
    with open(cwd + '/'+exp_code+ '_scantimes.out','w') as f:
        for element in scantime_array:
            print(element, file=f)
    print('Done!')
    
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

