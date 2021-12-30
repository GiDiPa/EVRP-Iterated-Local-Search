from sys import flags
import EVRP
import Heuristic
import Stats
import random


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
  Stats.get_mean(r,EVRP.get_current_best())
  print("End of run " + str(r) + " with best solution quality " + str(EVRP.get_current_best()) + " total evaluations: " + str(EVRP.get_evals()))

'''
/*sets the termination conidition for your heuristic*/
'''
def termination_condition():
  if EVRP.get_evals() >= 2000:
    flag = True
  else:
    flag = False
  return flag


'''
/****************************************************************/
/*                Main Function                                 */
/****************************************************************/
'''
def main():
  problem_instance = open('Benchmarks/bench1.evrp', 'r')
  EVRP.read_problem(problem_instance)

  Stats.open_stats(problem_instance)

  for run in range(Stats.maxTrials):
    start_run(run+1)
    Heuristic.init_heuristic()

    while not(termination_condition()):
      Heuristic.run_heuristic()
    '''implement print_solution or/and check_solution'''
    end_run(run)
  
  Stats.close_stats()

if __name__ == "__main__":
  main()

