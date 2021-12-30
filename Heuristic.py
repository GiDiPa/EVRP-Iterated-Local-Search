
import random
from dataclasses import dataclass
import EVRP
import sys
import gc

@dataclass
class Solution:
    tour: list
    id: int
    tour_length: float
    steps: int

best_sol = None

'''
/*initialize the structure of your heuristic in this function*/
'''

def init_heuristic():
  global best_sol
  best_sol = Solution(tour=[None for x in range(EVRP.numOfCustomers + 1000)],id = 1, steps = 0, tour_length = sys.maxsize)


'''
Pseudo-codice della Greedy Randomized Search

BestSol := Null
Best := Infinity
For i:=1 to MaxTentativi
    sol:=genera soluzione a caso
    cost:=calcola il costo di sol
    if cost<best then
        BestSol:=sol
        best:=cost
        print(best, tempo trascorso dall'inizio)
    endif
endfor
return BestSol,Best
'''

def run_heuristic():
  hhelp, oobject, tot_assigned, ffrom, to, charging_station = 0, 0, 0, 0, 0, 0
  r = []
  energy_temp = 0.0
  capacity_temp = 0.0
  for i in range(EVRP.numOfCustomers + 1):
    r.append(i)
    

  for i in range(EVRP.numOfCustomers + 1):
    oobject = int(random.random() * (EVRP.numOfCustomers - tot_assigned))
    hhelp = r[i]
    r[i] = r[i+oobject]
    r[i+oobject] = hhelp
    tot_assigned += 1
  best_sol.steps = 0
  best_sol.tour_length = sys.maxsize
  best_sol.tour[0] = EVRP.Depot
  best_sol.steps += 1

  i = 0
  while i < EVRP.numOfCustomers:
    ffrom = best_sol.tour[best_sol.steps - 1]
    to = r[i]
    if capacity_temp + float(EVRP.get_customer_demand(to)[1]) <= EVRP.maxCapacity and energy_temp + EVRP.get_energy_consumption(ffrom,to) <= EVRP.batteryCapacity:
      capacity_temp += float(EVRP.get_customer_demand(to)[1])
      energy_temp += EVRP.get_energy_consumption(ffrom,to)
      best_sol.tour[best_sol.steps] = to
      best_sol.steps += 1
      i += 1
    elif capacity_temp + float(EVRP.get_customer_demand(to)[1]) > EVRP.maxCapacity:
      capacity_temp = 0.0
      energy_temp = 0.0
      best_sol.tour[best_sol.steps] = EVRP.Depot
      best_sol.steps += 1
    elif energy_temp + float(EVRP.get_energy_consumption(ffrom,to)) > EVRP.batteryCapacity:
      charging_station = random.randint(0, float(EVRP.actualProblemSize - (EVRP.numOfCustomers-1)) + float(EVRP.numOfCustomers - 1)-1)  
      if EVRP.is_charging_station(charging_station) == True:
        energy_temp = 0.0
        best_sol.tour[best_sol.steps] = charging_station
        best_sol.steps += 1
    else:
      capacity_temp = 0.0
      energy_temp = 0.0
      best_sol.tour[best_sol.steps] = EVRP.Depot
      best_sol.steps += 1
    
    if best_sol.tour[best_sol.steps - 1] != EVRP.Depot:
      best_sol.tour[best_sol.steps] = EVRP.Depot
      best_sol.steps += 1
  best_sol.tour_length = EVRP.fitness_evaluation(best_sol.tour, best_sol.steps)

  del r
  
  gc.collect()

def free_heuristic():
  del best_sol.tour
  gc.collect()


