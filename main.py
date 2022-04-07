import argparse
import sys

from numpy import empty, number, percentile
import EVRP
import Heuristic
import Stats
import random
import argparse
import math
import copy
import matplotlib.pyplot as plt
import joblib
from joblib import Parallel, delayed
import os
import datetime
import gc
import re

'''
/*initialiazes a run for your heuristic*/
'''
def start_run(r):
  random.seed(r + random.random())
  rs = random.random() 
  EVRP.init_evals()
  if r == 1:
    EVRP.init_current_best()
  print("Attempt " + str(r) + " with random seed " + str(rs))

'''
/*gets an observation of the run for your heuristic*/
'''

def end_run(r,bestFit):
  if EVRP.get_current_best == sys.maxsize:
    print("Attempt " + str(r+1) + " with no solution.  Total evaluations: " + str(EVRP.get_evals()))
  else:
    Stats.get_mean(r,EVRP.get_current_best())
    print("Attempt " + str(r+1) + " with best solution quality " + str(bestFit) + " total evaluations: " + str(EVRP.get_evals()-1) + " num vehicles used: " + str(EVRP.numVehiclesUsed))

'''
/*sets the termination conidition for your heuristic*/
'''
def termination_condition(numEvals):
  if EVRP.get_evals() >= numEvals:
    flag = True
  else:
    flag = False
  return flag


'''
/* prepare data and launch run heuristic
'''
#RandomArrayPermutate

def prepare_and_launch(numEvals):
  customers_list = []
  bestPaths = list()
  for i in range(EVRP.numOfCustomers + 1):
    customers_list.append(i)
  #remove Depot
  customers_list.remove(0)
  #array of Stations to pass
  stations_list = [x for x in range(len(EVRP.cust_demand) - EVRP.numOfStations, len(EVRP.cust_demand))]
  #stations_list.append(0)
  firstRun = True
  
  EVRP.init_evals()
  if firstRun:
    firstRun = False
    best_solution = Heuristic.init_heuristic()
    best_solution = Heuristic.run_heuristic(customers_list,stations_list,best_solution)
    if not (EVRP.check_solution(best_solution.tour, best_solution.steps)):
      best_solution = Heuristic.init_heuristic()
      EVRP.init_current_best()
      best_path_temp = []
    else:
      best_path_temp = customers_list.copy()
  while not(termination_condition(numEvals)):
    best_sol_temp = Heuristic.init_heuristic()
    run_array_permutated = Heuristic.run_array_permutated(customers_list.copy())  
    #run_array_permutated = [15,16,14,1,8,11,12,20,9,13,21,4,19,10,2,3,18,6,17,7,5]
    best_sol_temp = Heuristic.run_heuristic(run_array_permutated,stations_list,best_sol_temp)
    if (EVRP.check_solution(best_sol_temp.tour, best_sol_temp.steps)):
      if best_sol_temp.tour_length < best_solution.tour_length:
        best_solution = best_sol_temp
        best_path_temp = run_array_permutated.copy()
  best_path = best_path_temp.copy()
  bestTourPath = []
  best_tourlength = float(best_solution.tour_length)
  for i in range(0,best_solution.steps):
    bestTourPath.append(best_solution.tour[i])
  bestPaths.append((best_path))
  bestPaths.append(best_tourlength)
  bestPaths.append((bestTourPath))
  bestPaths.append((best_solution.steps))
  return bestPaths

#after the Random Permutate, we pass to RandomLocalSearch!

#RandomLocalSearch part

def swapPositions(list, pos1, pos2):
    list[pos1], list[pos2] = list[pos2], list[pos1]
    return list

def couplesList(pathToSwap,numEvals):
  percKvariance = EVRP.get_evals()
  #variate the couples of swap while numEvals is increasing
  if percKvariance <= int(math.ceil((numEvals * 25 ) / 100)):
    percK = int(math.ceil((len(pathToSwap) * 20 ) / 100))
  elif percKvariance <= int(math.ceil((numEvals * 50 ) / 100)):
    percK = int(math.ceil((len(pathToSwap) * 15 ) / 100))
  elif percKvariance <= int(math.ceil((numEvals * 75 ) / 100)):
    percK = int(math.ceil((len(pathToSwap) * 10 ) / 100))
  else:
    percK = int(math.ceil((len(pathToSwap) * 5 ) / 100))
  
  #if percKvariance 
  
  if percK % 2 != 0:
    percK += 1
  coupleSwap = []
  for i in range(percK):
    flagSwap = True
    if not coupleSwap:
      randomN = random.randint(0, len(pathToSwap) - 1)
      coupleSwap.append(randomN)
    else:
      while flagSwap:
        randomN = random.randint(0, len(pathToSwap) - 1)
        if randomN not in coupleSwap:
          coupleSwap.append(randomN)
          flagSwap = False
  i = 0
  while i < percK:
    pathToSwap = swapPositions(pathToSwap,coupleSwap[i],coupleSwap[i+1])
    i = i + 2
  return pathToSwap

'''
def randomLocalSearchCouples(randomBestSolution,numEvals):
  bestSol = []
  bestFitness = randomBestSolution[1]
  bestPath = randomBestSolution[0]
  bestTour = randomBestSolution[2]
  bestSteps = randomBestSolution[3]
  stations_list = [x for x in range(len(EVRP.cust_demand) - EVRP.numOfStations, len(EVRP.cust_demand))]
  
  #print(bestFitness)
  #input('go on')
  EVRP.init_evals()
  while not(termination_condition(numEvals)):
    best_sol_temp = Heuristic.init_heuristic()
    pathTemp = couplesList(bestPath.copy(),numEvals)
    best_sol_temp = Heuristic.run_heuristic(pathTemp,stations_list,best_sol_temp)
    if (EVRP.check_solution(best_sol_temp.tour, best_sol_temp.steps)):
      if best_sol_temp.tour_length < bestFitness:
        bestFitness = best_sol_temp.tour_length
        bestPath = pathTemp
  bestTourToList = []
  for i in range(0,bestSteps):
    bestTourToList.append(bestTour[i])
  bestSol.append((bestPath))
  bestSol.append((bestFitness))
  bestSol.append((bestTourToList))
  bestSol.append((bestSteps)) 
  return bestSol
'''

def randomLocalSearch(randomBestSolution,numEvals):
  bestSol = []
  bestFitness = randomBestSolution[1]
  bestPath = randomBestSolution[0]
  bestTour = randomBestSolution[2]
  bestSteps = randomBestSolution[3]
  stations_list = [x for x in range(len(EVRP.cust_demand) - EVRP.numOfStations, len(EVRP.cust_demand))]
  for r in range(Stats.maxTrials):
    EVRP.init_evals()
    while not(termination_condition(numEvals)):
      best_sol_temp = Heuristic.init_heuristic()
      flagSwap = True
      while flagSwap:
        random.seed()
        random1 = random.randint(0, len(bestPath) - 1)
        random2 = random.randint(0, len(bestPath) - 1)
        #print(random1,random2)
        if random1 != random2:
          flagSwap = False
      
      pathTemp = bestPath.copy()
      pathTemp = swapPositions(pathTemp,random1,random2)
      best_sol_temp = Heuristic.run_heuristic(pathTemp,stations_list,best_sol_temp)
      if (EVRP.check_solution(best_sol_temp.tour, best_sol_temp.steps)):
        if best_sol_temp.tour_length < bestFitness:
          bestFitness = best_sol_temp.tour_length
          bestPath = pathTemp
          bestSteps = best_sol_temp.steps
          bestTour = best_sol_temp.tour
  EVRP.check_solution(bestTour, bestSteps)
  bestTourToList = []
  for i in range(0,bestSteps):
    bestTourToList.append(bestTour[i])
  bestSol.append((bestPath))
  bestSol.append((bestFitness))
  bestSol.append((bestTourToList))
  bestSol.append((bestSteps)) 
  return bestSol


def definitiveIteratedLocalSearch(numEvals):
  bestSolutionRandomizedArray = list(prepare_and_launch(numEvals))
  bestSol = bestSolutionRandomizedArray
  bestSolTemp = []
  for run in range(Stats.maxTrials):
    start_run(run+1)
    bestSolTemp = randomLocalSearch(bestSol,numEvals)
    if bestSolTemp[1] < bestSol[1]:
      bestSol = bestSolTemp
    end_run(run,bestSol[1])
  return bestSol


def plotSolution(solToPlot,problem_instance):
  activeArcs = []
  plt.plot(int(EVRP.node_list[0].x), int(EVRP.node_list[0].y), c='r', marker='s')
  for i in range(EVRP.numOfCustomers + 1):
    plt.scatter(int(EVRP.node_list[i].x), int(EVRP.node_list[i].y), c='b', s = 20)
  for i in range(EVRP.numOfCustomers + 1, EVRP.actualProblemSize):
    plt.scatter(int(EVRP.node_list[i].x), int(EVRP.node_list[i].y), c='g', marker='p', s = 80) 
  #plt.scatter(int(EVRP.node_list[EVRP.numOfCustomers:].x), int(EVRP.node_list[EVRP.numOfCustomers:].y), c='g') 
  plt.title(problem_instance.name)
  plt.xlabel("Fitness:" + str(solToPlot[1])) 
  ct = datetime.datetime.now()
  ts = ct.timestamp()
  plt.savefig('Benchmarks/plots/' + os.path.basename(problem_instance.name) + '/' + os.path.basename(problem_instance.name) + str(ts) + 'plotwithoutroute.png')
  for i in range(len(solToPlot[2]) - 1):
    activeArcs.append((solToPlot[2][i],solToPlot[2][i+1]))
  for i,j in activeArcs:
    plt.plot([int(EVRP.node_list[i].x),int(EVRP.node_list[j].x)],[int(EVRP.node_list[i].y),int(EVRP.node_list[j].y)],c='b',zorder = 0)
  plt.savefig('Benchmarks/plots/' + os.path.basename(problem_instance.name) + '/' + os.path.basename(problem_instance.name) + str(ts) + 'plotwithroute.png')

def execute(problem_instance):
  #problem_instance = open('Benchmarks/bench1.evrp', 'r')
  parser = argparse.ArgumentParser()
  parser.add_argument('--maxTrials',type = int, required=True)
  parser.add_argument('--benchNo',type = str, required=True)
  args = parser.parse_args()
  EVRP.read_problem(problem_instance)
  numEvalsInt = int(re.search(r'\d+', problem_instance.name).group()) * 10
  numEvals = numEvalsInt * EVRP.actualProblemSize
  Stats.open_stats(problem_instance,args.maxTrials)
  iLSSol = definitiveIteratedLocalSearch(numEvals)
  #plotSolution(iLSSol,problem_instance)
  #print(EVRP.node_list)
  if EVRP.exceedVehicles:
    print('The final solution exceeds the number of vehicles')
  else:
    print('The solution fits the number of vehicles')      
  #Stats.close_stats()
  print(iLSSol)
  return iLSSol   

'''
/****************************************************************/
/*                Main Function                                 */
/****************************************************************/
'''

def main():
  parser = argparse.ArgumentParser()
  parser.add_argument('--maxTrials',type = int, required=True)
  parser.add_argument('--benchNo',type = str, required=True)
  args = parser.parse_args()
  problem_instance = open(args.benchNo, 'r')
  Stats.open_stats(problem_instance,args.maxTrials)
  number_of_cpu = int(args.maxTrials)
  delayed_funcs = [delayed(execute)(problem_instance) for i in range(number_of_cpu)]
  parallel_pool = Parallel(n_jobs=number_of_cpu)
  final = parallel_pool(delayed_funcs)
  final_sorted_list = sorted(final, key=lambda x:x[1])
  final = [final_sorted_list[0], final_sorted_list[-1]]
  EVRP.read_problem(problem_instance)
  plotSolution(final[0],problem_instance)
  EVRP.check_solution(final[0][2], final[0][3])
  numEvalsInt = int(re.search(r'\d+', problem_instance.name).group()) 
  numEvals = numEvalsInt * 1000
  Stats.close_stats(final_sorted_list,numEvals)
  

if __name__ == "__main__":
  main()