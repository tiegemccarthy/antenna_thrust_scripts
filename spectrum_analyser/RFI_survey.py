#!/usr/bin/python
# Usage: RFI_survey.py filename
# This script will use the spectrum analyzer to perform a 2-14 GHz RFI survey. 
# The results are written to the file specified on the command line
# NB - this will overwrite the file by default
# The output format is a series of long vectors recording the TRACEs on the screen
# Each individual trace consists of 501 points corresponding to the spectrum +- 500 MHz
# around the set centre frequency. 
# Odd numbered rows are the AVERaged spectra
# Even number rows are the MAX HOLD spectra 
# No time tagging at present
# Misc settings - these should be entered in the script, but this hasn't happened yet.
# RBW 1 MHz
# VBW 1 MHz
# SPAN 1 GHz
# SWT auto (2.5 ms)
# NCOUNT 1000 (actually ~300 for 30s)
# Detectors are RMS 
# TRACE1 is average
# TRACE2 is MAX HOLD 
# If loading the data into MATLAB/octave, the relevant frequency axis is:
#    frequencies=[(-.5:.002:.5)+2, (-.5:.002:.5)+2.75 , (-.5:.002:.5)+3.5, (-.5:.002:.5)+4.25, (-.5:.002:.5)+5, (-.5:.002:.5)+5.75, (-.5:.002:.5)+6.5, (-.5:.002:.5)+7.25, (-.5:.002:.5)+8, (-.5:.002:.5)+8.75, (-.5:.002:.5)+9.5, (-.5:.002:.5)+10.25,(-.5:.002:.5)+11, (-.5:.002:.5)+11.75, (-.5:.002:.5)+12.5, (-.5:.002:.5)+13.25, (-.5:.002:.5)+14];


import socket
import sys
import time 


s=socket.socket()
s.connect(('131.217.61.101', 5025))
#s.recv(1024)

s.send('FREQ:SPAN 1GHZ\rn\n')


freqs=['2', '2.75', '3.5', '4.25', '5', '5.75', '6.5','7.25', '8', '8.75', '9.5', '10.25', '11', '11.75', '12.5', '13.25', '14'] 
#freqs=['2', '2.75', '3.5']
#freqs=['2', '2.75']
#n=0
#while True:
#  for i in freqs:  

FID=open(sys.argv[1], 'w')

while True:
  outstring1=''
  outstring2=''
  for i in freqs:
    #print i
    s.send('FREQ:CENT ' + i + 'GHZ\r\n')
    time.sleep(30)
    s.send('TRAC? TRACE1\r\n')
    time.sleep(0.5)
    a=s.recv(16384)
    #print len(a)
    outstring1=outstring1+','+a.rstrip('\r\n')
    s.send('TRAC? TRACE2\r\n')
    time.sleep(0.5)
    a=s.recv(16384)
    #print len(a)
    outstring2=outstring2+','+a.rstrip('\r\n')
    time.sleep(0.5)

  FID.write(outstring1[1:]+'\n')
  FID.write(outstring2[1:]+'\n')
  FID.close()  
  FID=open(sys.argv[1], 'a')



#s.send('TRAC? TRACE1\r\n')
#a=s.recv(4096)
#b=s.recv(4096)
#c=s.recv(4096)
#if c[len(c)-1]!='\n':
#  d=s.recv(4096)
#  FID=open(sys.argv[1], 'w')
#  FID.write(a+b+c+d)
#FID.close()


#FID=open(sys.argv[1], 'w')
#FID.write(a+b+c+d)
#FID.close()

#s.send(':FREQ ' + sys.argv[1] +'GHZ\r\n')
#s.recv(1024)
#s.send(':POW ' + sys.argv[2] +'DBM\r\n')
#s.recv(1024)
#s.send(':OUTP:STAT ON\r\n')
#s.recv(1024)

#s.send(':FREQ?\r\n')
#freq=s.recv(1024)
##print freq
#if((freq=='\rSCPI> ') | (freq=='SCPI> ') ):
#   freq=s.recv(1024)
#   #print freq##

#freq2=freq.replace("SCPI> " , "")

#s.send(':POW?\r\n')
#pow=s.recv(1024)
#if((pow=='\rSCPI> ') | (pow=='SCPI> ')):
#   pow=s.recv(1024)#

#pow2=pow.replace("SCPI> " , "")

#s.send(':OUTP:STAT?\r\n')
#outp=s.recv(1024)
#if((outp=='\rSCPI> ') | (outp=='SCPI> ')):
#   outp=s.recv(1024)#

#outp2=outp.replace("SCPI> " , "")
#print 'AgilentHb is set to ' + str(float(freq2)/1E9) + ' GHz and ' + str(float#(pow2)) + ' dBm. The output is ' + outp2
#s#.close



