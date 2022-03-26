import EVRP
import math
import gc
import os
import datetime

maxTrials = 0
log_performance = []
perfOfTrials = []

'''Used to output offline performance and population diversity'''
def open_stats(probInstName,numTrials):
  global perfOfTrials
  global log_performance
  global maxTrials
  maxTrials = numTrials
  log_performance = open('Benchmarks/Stats/stats-' + os.path.basename(probInstName.name) + '.txt', 'a')
  perfOfTrials = [0.0 for x in range(maxTrials)]
  if log_performance == None:
    exit()


def get_mean(r, value):
  global perfOfTrials
  perfOfTrials[r] = value


def mean(values, size):
  m = 0.0
  for i in range(size):
    m += values[i]
  m = m / float(size)
  return m


def standardDeviation(values, size, average):
  dev = 0.0
  if size <= 1:
    return 0.0
  for i in range(size):
    dev += (float(values[i]) - average) * (float(values[i]) - average)
  return math.sqrt(dev / float(size - 1))


def bestOfVector(values, l):
  k = 0
  mmin = float(values[k])
  for k in range(l):
    if values[k] < mmin:
      mmin = values[k] 
  return mmin


def worstOfVector(values, l):
  k = 0
  mmax = float(values[k])
  for k in range(l):
    if values[k] > mmax:
      mmax = values[k]
  return mmax


def close_stats():
  global log_performance
  log_performance.write("\n")
  log_performance.write("#####################################################################\n")
  log_performance.write(str(datetime.datetime.now()) + ' Log\n\n')
  for i in range(maxTrials):
    log_performance.write(str(perfOfTrials[i]) + '\n')
  perfMeanValue = mean(perfOfTrials, maxTrials)
  perfStdevValue = standardDeviation(perfOfTrials, maxTrials, perfMeanValue)
  log_performance.write("Mean \t" + str(perfMeanValue))
  log_performance.write(" Std Dev \t" + str(perfStdevValue) + '\n')
  log_performance.write("Min \t" + str(bestOfVector(perfOfTrials,maxTrials)) + '\n')
  log_performance.write("Max \t" + str(worstOfVector(perfOfTrials, maxTrials)) + '\n')
  if EVRP.exceedVehicles:
    log_performance.write("The Solution Exceed number of Vehicles at minimum result\n")
  else:
    log_performance.write("The Solution fits number of Vehicles at minimum result\n")  
  log_performance.write("#####################################################################\n")
  log_performance.close()

def free_stats():
  global perfOfTrials
  del perfOfTrials
  gc.collect()


