#!/usr/bin/python
from datetime import datetime
import numpy as np

""" Converts radiosignal originally stored in a list to binary strings which are then converted to the transmitted data in plain text. """


def convert(signal):
    """ Retruns two parallel arrays with times and signal when given a list of times and signal in parallel lists. """

    timeArray = np.array(signal[0],dtype=float)
    signalArray = np.array(signal[1], dtype='b')
    return(signalArray, timeArray)


def analyse(signalArray, timeArray):             
    """ Retruns a "binary" string when given two parallel arrays with times and signal. """

    stepTimes = timeArray[np.logical_xor(signalArray, np.roll(signalArray,1))]      # roll 1 in signalArray and compare using XOR with orignial, use as mask for timeArray to find all times with a step
    
    plateauTimes = stepTimes - np.roll(stepTimes,1)                                 # subtrct from stepTimes the stepTimes when rolled 1

    warnings = 0
    binary = ''
    tooManyErrors = False
    n = plateauTimes.size-1
    for i in range(n-1, 0, -2):
        if plateauTimes[i] >= 0.0016 and plateauTimes[i] <= 0.0025:                 # long time low means "1"
            binary = '0' + binary
            continue
        elif plateauTimes[i] >= 0.0037 and plateauTimes[i] < 0.0045:                # long time low means "1"
            binary = '1' + binary
            continue
        elif plateauTimes[i] >= 0.0083 and plateauTimes[i] < 0.0089:                # double time low means end of repetition, separates repeats of signal with a "_" in the binary
            binary = '_' + binary
            continue
        else:
            warnings = warnings + 1                                                 # anything else means either communication error or end of digital signal, indicates this with a "w" in the binary
            binary = 'w' + binary
        
    # code below this point has not been optimised. It selects and returns the first data repetition in the binary which is free of errors (if possible)
    longBinary = binary
    binaries=binary.split('_')
    whichToUse = len(binaries)
    binary = binaries[whichToUse-1]
    if 'w' in binary:
        binary = ''                    
    while len(binary) != 36 and whichToUse>=0:
        binary = binaries[whichToUse-1]
        if len(binary)>36:
            binary = binary[:36]            
        if 'w' in binary:
            binary = ''
        whichToUse = whichToUse - 1
    return(binary, longBinary, tooManyErrors)
    
    
def postprocess(binary, longBinary, tooManyErrors):
    """ Prints the data in plain text when given a proper binary string. """

    if len(binary) == 36 and tooManyErrors == False:
        word1 = binary[19:28]
        temperature= int(word1,2)/10.0
        word2 = binary[28:36]
        moisture = int(word2,2)        
        print(longBinary)
        print(binary,'translates into'+' '*(4-len(str(temperature))), temperature,'grader C' , moisture ,'%RH  -  sent from sensor',int(binary[:19],2) )
    else:
        print('Communication error')


""" main """

# the data is here read from a file instead of being a result of an rf transmission
signal=[[],[]]
with open("./radiosignaler/24 3 signal2021-03-02 11-16-50.636838.txt","r") as f:
    for data in f:
        signal[0].append(data[:-3])
        signal[1].append(data[-2:-1])
       
# the code below this point is mostly to print the times during speed optimisation 
starttime = datetime.now()
signalArray, timeArray = convert(signal)
print('Time for conversion: ', datetime.now()-starttime)
starttime = datetime.now()
binary, longBinary, tooManyErrors = analyse(signalArray, timeArray)
print('Time for analysis: ', datetime.now()-starttime)
starttime = datetime.now()
postprocess(binary, longBinary, tooManyErrors)
print('Time for postprocessing: ', datetime.now()-starttime)
