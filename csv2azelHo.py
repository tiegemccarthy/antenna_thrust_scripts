#!/usr/bin/python
from astropy.io import ascii
import sys
import numpy as np

def main(csv_file, output_file):
    csv_file_string = str(csv_file)
    output_file_string = str(output_file)
    # Load data
    data = ascii.read(csv_file_string)
    # Extract required columns and do any necessary conversion
    az_deg = data['un_az']*180*(1/np.pi)
    el_deg = data['el']*180*(1/np.pi)
    jd = data['jd']
    # Write data in desired format
    with open(output_file_string, 'w') as f:
        for i in range(0, len(data)):
            print("JD : " + format(jd[i], '.8f') + " ; Az : " + format(az_deg[i], '.3f') + " ; El : " + format(el_deg[i], '.3f') + " ; Rn :    0.0 ", file=f)
    

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
