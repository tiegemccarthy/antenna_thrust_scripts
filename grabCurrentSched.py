#!/usr/bin/python
from mat4py import loadmat
import numpy as np
import scipy.io
import sys

# This script crads the current az/el schedule information from the VieVS temp files in the LEVEL5 data directory

def extractSchedData(matfile):
    mat = scipy.io.loadmat(matfile)
    epoch_mat = mat['sched_data'][0][0][7][0][0][2][0][0][1][0]
    sat_name = mat['sched_data'][0][0][7][0][0][7][0]
    # Turn the mat file into a more comprehensible data table and filter out data based on cutoff.
    data = []
    for i in range(0,len(epoch_mat)):
        mjd = epoch_mat[i][0][0][0]
        ra = epoch_mat[i][1][0][0]
        dec = epoch_mat[i][2][0][0]
        az = epoch_mat[i][3][0][0]
        el = epoch_mat[i][4][0][0]
        data.append([mjd, ra, dec, az, el])
    return data, sat_name
    
def outputCSV(exp_code, list_list, sat_name):
    outfile_name = exp_code + '.csv'
    with open(outfile_name, 'w') as f:
        print('# ' + exp_code + ' - ' + sat_name + 'jd, ra, dec, un_az, el', file=f)
        for line in list_list:
            print(*line, sep = ', ', file=f)
            
def main(exp_code):
    # Change the path below to that which is relevant for your VieVS installation 
    path_to_sched_data = '/home/tiege/Documents/research/geodesy/VieVS/VLBI/DATA/LEVEL5/sched_data.mat'
    # Extract data
    data_list, source_name = extractSchedData(path_to_sched_data)
    # Output CSV file
    outputCSV(exp_code, data_list, source_name)

if __name__ == '__main__':
    main(sys.argv[1])
