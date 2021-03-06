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
#       <experiment_code>_scaninfo.out - text file with julian date start times, average elevation and average range for each 5 minute schedule block - this is required by the spectrum analyser recording script and is useful for analysis.
# Example:
#       ./scheduleGeneration.py azel.csv at0001

cwd = os.getcwd()

def scanAvgElRange(data_table, scantimes):
    scan_avg_el = []
    scan_avg_range = []
    for time in scantimes:
        mid_scan_offset = 0.002246944 # offset to midpoint of scan (90s settle time + 210/2) in day fraction
        offset_time = time + mid_scan_offset
        # Need to match this offset time to a elevation and range from the original CSV data
        time_diff = abs(data_table['jd'] - offset_time)
        min_diff_index = list(time_diff).index(min(time_diff))
        scan_avg_el.append(data_table['el'][min_diff_index])
        scan_avg_range.append(data_table['range'][min_diff_index])
    return scan_avg_el, scan_avg_range
    
def main(input_file, exp_code):
    exp_code = str(exp_code)
    # Load data from CSV file
    data = ascii.read(input_file, format='csv', comment='#', header_start=0)
    # Yoink header from CSV file
    with open(input_file, 'r') as f:
        header_string = f.readline().rstrip()
        if not header_string[0] == '#':
            header_string = ''
            print('No header data available!')
    # Convert data into desired form
    az_deg = data['un_az']*180*(1/np.pi)
    el_deg = data['el']*180*(1/np.pi)
    rang = data['range']
    jd = data['jd']
    # Generate master schedule file
    print('Creating master schedule file.')
    with open(exp_code+'_master.out', 'w') as f:
        print(header_string, file=f)
        for i in range(0, len(data)):
            print("JD : " + format(jd[i], '.8f') + " ; Az : " + format(az_deg[i], '.3f') + " ; El : " + format(el_deg[i], '.3f') + " ; Rn :    0.0 ", file=f)
    print('Done!')
    # Now generate block schedules
    print('Generating scantime info for recorder.')
    interval = 0.00347 # 5 minutes in fraction of day
    start_time = jd[0]
    end_time = max(jd)
    num_scans = math.ceil((end_time - start_time)/interval) # calculate how many 5 min chunks are needed rounded up
    scantime_array = np.arange(start_time, start_time + (num_scans+0.1)*interval, interval) # the 0.1 makes sure we have a final value > the end time
    print('Done!')
    # Write out the scan information of each 5 min block - for use with spectrum analyser recording and data reduction
    avg_el_list, avg_range_list = scanAvgElRange(data, scantime_array)
    print('Writing out scan information for recording and analysis.')
    if os.path.exists(cwd + '/'+exp_code+ '_scaninfo.out'):
        os.remove(cwd + '/'+exp_code+ '_scaninfo.out')
    with open(cwd + '/'+exp_code+ '_scaninfo.out','w') as f:
        for i in range(0, len(scantime_array)):
            print(scantime_array[i], avg_el_list[i], avg_range_list[i], file=f)
    print('Done!')
    
if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])

