#!/usr/bin/env python

import time
#import psyco

#psyco.full()

TIMEFORMAT = "%m/%d/%y %H:%M:%S"
INTERVAL = 0.2

def getTimeList():
    statFile = file("/proc/stat", "r")
    timeList = statFile.readline().split(" ")[2:6]
    statFile.close()
    for i in range(len(timeList)) :
        timeList[i] = int(timeList[i])
    return timeList

def deltaTime(interval) :
    x = getTimeList()
    time.sleep(interval)
    y = getTimeList()
    for i in range(len(x)) :
        y[i] -= x[i]
    return y

if __name__ == "__main__" :
#    while True :
        dt = deltaTime(INTERVAL)
        #timeStamp = time.strftime(TIMEFORMAT)
        cpuPct = 100 - (dt[len(dt) - 1] * 100.00 / sum(dt))
        #print timeStamp + "\t" + str('%.4f' %cpuPct)
        print str('%.4f' %cpuPct)
