#!/usr/bin/python
from datetime import datetime

""" converts radiosignal to binary strings"""


def convert(signal):
    signalTime=float(signal[0][0])
    for i in range(len(signal[0])):
        signal[0][i] = float(signal[0][i]) - signalTime
        signal[1][i] = int(signal[1][i])
    return(signal)


def analyse(signal):             
    n = len(signal[0]) - 1
    
    while signal[1][n] == 0 and n>0: n = n - 1
    up = signal[0][n]
    m = n
    while signal[1][m] == 1 and m>0: m = m - 1
    high = n - m
    
    binary=''
    n = n - int(high/2)
    
    warnings = 0
    first = 0
    tooManyErrors = False
    
    while len(binary)<250 and n>20 and warnings<3:
        if warnings > len(binary): tooManyErrors = True
        up = signal[0][n]
        while signal[1][n] == 1 or signal[1][n-1] == 1: n = n - 1
        down = signal[0][n]
        while signal[1][n] == 0 or signal[1][n-1] == 0: n = n - 1
        up = signal[0][n]
        lowTime = down - up
        
        if lowTime >= 0.0016 and lowTime <= 0.0025:
            binary = '0' + binary
            continue
        elif lowTime >= 0.0037 and lowTime < 0.0045: 
            binary = '1' + binary
            continue
        elif lowTime >= 0.0083 and lowTime < 0.0089:
            binary = '_' + binary
            continue
        else:
            warnings = warnings + 1
            binary = 'w' + binary
            if warnings == 1: first = int(10000*lowTime)
                    
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

signal=[[],[]]
with open("./radiosignaler/24 3 signal2021-03-02 11-16-50.636838.txt","r") as f:
    for data in f:
        signal[0].append(data[:-3])
        signal[1].append(data[-2:-1])
       
starttime = datetime.now()
convertedSignal = convert(signal)
print('Time for conversion: ', datetime.now()-starttime)
starttime = datetime.now()
binary, longBinary, tooManyErrors = analyse(convertedSignal)
print('Time for analysis: ', datetime.now()-starttime)
starttime = datetime.now()
postprocess(binary, longBinary, tooManyErrors)
print('Time for postprocessing: ', datetime.now()-starttime)
