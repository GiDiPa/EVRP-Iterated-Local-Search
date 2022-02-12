import argparse
import sys
import EVRP
import Heuristic
import Stats
import random
import argparse
import copy

'''
/*initialiazes a run for your heuristic*/
'''
def start_run(r):
  random.seed(r)
  rs = random.random()
  EVRP.init_evals()
  EVRP.init_current_best()
  print("Run: " + str(r) + " with random seed " + str(rs))

'''
/*gets an observation of the run for your heuristic*/
'''

def end_run(r):
  if EVRP.get_current_best == sys.maxsize:
    print("End of run " + str(r+1) + " with no solution.  Total evaluations: " + str(EVRP.get_evals()))
  else:
    Stats.get_mean(r,EVRP.get_current_best())
    print("End of run " + str(r+1) + " with best solution quality " + str(EVRP.get_current_best()) + " total evaluations: " + str(EVRP.get_evals()))

'''
/*sets the termination conidition for your heuristic*/
'''
def termination_condition(numEvals):
  if EVRP.get_evals() >= 2000:
    flag = True
  else:
    flag = False
  return flag


'''
/* prepare data and launch run heuristic
'''

def prepare_and_launch(numEvals):
  customers_list = []
  bestPaths = set()
  for i in range(EVRP.numOfCustomers + 1):
    customers_list.append(i)
  #remove Depot
  customers_list.remove(0)
  #array of Stations to pass
  stations_list = [x for x in range(len(EVRP.cust_demand) - EVRP.numOfStations, len(EVRP.cust_demand))]
  #stations_list.append(0)
  print(stations_list)
  print(EVRP.cust_demand)
  firstRun = True
  for run in range(Stats.maxTrials):
    start_run(run+1)
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
    end_run(run)
  best_path = best_path_temp.copy()
  best_tourlength = []
  bestTourPath = []
  best_tourlength.append(best_solution.tour_length)
  for i in range(0,best_solution.steps):
    bestTourPath.append(best_solution.tour[i])
  bestPaths.add(tuple(best_path))
  bestPaths.add(tuple(bestTourPath))
  bestPaths.add(tuple(best_tourlength))
  return bestPaths
    
'''
/****************************************************************/
/*                Main Function                                 */
/****************************************************************/
'''
def main():
  problem_instance = open('Benchmarks/bench3.evrp', 'r')
  parser = argparse.ArgumentParser()
  parser.add_argument('--numEvals', type=int, required=True)
  parser.add_argument('--maxTrials',type = int, required=True)
  args = parser.parse_args()
  EVRP.read_problem(problem_instance)

  Stats.open_stats(problem_instance,args.maxTrials)
  #initialize the array of customers including depotp
  bestSolutionFromMaxTrial = prepare_and_launch(args.numEvals)
  print (bestSolutionFromMaxTrial)
  
  Stats.close_stats()

if __name__ == "__main__":
  main()

