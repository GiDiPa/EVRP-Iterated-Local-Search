import math
import sys
import gc
from dataclasses import dataclass
import numpy as np


node_list = []
distances = []
cust_demand = []
charging_station = []
problem_size = 0
energy_consumption = 0.0

Depot = 0
numOfCustomers = 0
actualProblemSize = 0
optimum = 0
numOfStations = 0
batteryCapacity = 0
maxCapacity = 0
vehicles = 0

evals = 0.0
current_best = 0.0

@dataclass
class Node:
    id: int
    x: float
    y: int


'''
/****************************************************************/
/*Compute and return the euclidean distance of two objects      */
/****************************************************************/
'''

def euclidean_distance(i,j):
  xd, yd, r = 0.0, 0.0, 0.0
  xd = int(node_list[i].x) - int(node_list[j].x)
  yd = int(node_list[i].y) - int(node_list[j].y)
  r = math.sqrt(xd*xd + yd*yd)
  return r



'''
/****************************************************************/
/*Compute the distance matrix of the problem instance           */
/****************************************************************/
'''

def compute_distances():
  for i in range(actualProblemSize):
    for j in range(actualProblemSize):
      distances[i][j] = euclidean_distance(i,j)

'''
/****************************************************************/
/*Generate and return a two-dimension array of type double      */
/****************************************************************/
'''

def generate_2D_matrix(n,m):
  matrix = np.zeros((n,m))
  return matrix




'''
/****************************************************************/
/* Read the problem instance and generate the initial object    */
/* vector.                                                      */
/****************************************************************/

'''
def read_problem(bench):
  global problem_size
  global maxCapacity
  global vehicles
  global batteryCapacity
  global energy_consumption
  global numOfStations
  global optimum
  global numOfCustomers
  global actualProblemSize
  global node_list
  global distances

  lines = bench.readlines()
  for line in lines:
    if "DIMENSION" in line:
      if line.split(':')[1].strip() == 0 or line.split(':')[1].strip() is None:
        print('Error on Dimension')
      else:
        problem_size = int(line.split(':')[1].strip())
    elif "EDGE_WEIGHT_TYPE" in line:
      if line.split(':')[1].strip() is None:
        print('EDGE_WEIGHT_TYPE Error')
        exit()
      elif line.split(':')[1].strip() != 'EUC_2D':
        print('Not EUC_2D')
        exit()
    elif "CAPACITY" in line:
      if line.split(':')[0].strip() == 'CAPACITY':
        if line.split(':')[1].strip() == 0 or line.split(':')[1].strip() is None:
          print('Error on Capacity')
        else:
          maxCapacity = int(line.split(':')[1].strip())
      elif line.split(':')[0].strip() == 'ENERGY_CAPACITY':
        if line.split(':')[1].strip() == 0 or line.split(':')[1].strip() is None:
          print('Error on ENERGY_CAPACITY')
          exit()
        else:
          batteryCapacity = int(line.split(':')[1].strip())
    elif "VEHICLES" in line:
      if line.split(':')[1].strip() == 0 or line.split(':')[1].strip() is None:
        print('Error on Vehicles')
        exit()
      else:
        vehicles = int(line.split(':')[1].strip())
    elif "ENERGY_CONSUMPTION" in line:
      if line.split(':')[1].strip() == 0 or line.split(':')[1].strip() is None:
        print('Error on ENERGY_CONSUMPTION')
        exit()
      else:
        energy_consumption = float(line.split(':')[1].strip())
    elif "STATIONS" in line:
      if line.split(':')[0].strip() == 'STATIONS':
        if line.split(':')[1].strip() == 0 or line.split(':')[1].strip() is None:
          print('Error on Stations')
        else:
          numOfStations = int(line.split(':')[1].strip())
    elif "OPTIMAL_VALUE" in line:
      if line.split(':')[1].strip().split('(')[0].strip() == 0 or line.split(':')[1].strip() is None:
        print('Error on Optimal_Value')
        exit()
      else:
        optimum = float(line.split(':')[1].strip().split('(')[0].strip())
    elif "NODE_COORD_SECTION" in line:
      if problem_size != 0:
        numOfCustomers = problem_size - 1
        actualProblemSize = problem_size + numOfStations
        flag = False
        indexNodeCoordInFile = 0
        for line1 in lines:
          if flag == False:
            if "NODE_COORD_SECTION" in line1:
              flag = True
          elif flag == True:
            if indexNodeCoordInFile < actualProblemSize:
              tempId = line1.split(" ")[0].strip()
              tempX  = line1.split(" ")[1].strip()
              tempY  = line1.split(" ")[2].strip()
              node_list.append(Node(tempId,tempX,tempY)) 
            indexNodeCoordInFile +=1
        distances = generate_2D_matrix(actualProblemSize,actualProblemSize)
      else:
        print("wrong problem istance file")
        exit()
    elif "DEMAND_SECTION" in line:
      if problem_size != 0:
        flag = False
        indexDemandSecInFile = 0
        for linetemp in lines:
          if flag == False:
            if "DEMAND_SECTION" in linetemp:
              flag = True
          elif flag == True:
            if indexDemandSecInFile < actualProblemSize:
              if indexDemandSecInFile < actualProblemSize - numOfStations:
                tempId  = linetemp.split(" ")[0].strip()
                tempDem = linetemp.split(" ")[1].strip()
                cust_demand.append([tempId,tempDem])
                charging_station.append(False)
              else:
                 cust_demand.append([indexDemandSecInFile + 1,0])
                 charging_station.append(True)
              indexDemandSecInFile +=1
        charging_station[0] = True
  if actualProblemSize == 0:
    print("wrong problem istance file") 
    exit()
  else:
    compute_distances()     

'''
/****************************************************************/
/* Returns the solution quality of the solution. Taken as input */
/* an array of node indeces and its length                      */
/****************************************************************/
'''

def fitness_evaluation(routes, size):
  global current_best,evals
  tour_length = 0.0
  for i in range(size-1):
    tour_length += distances[routes[i]][routes[i+1]]
  if tour_length < current_best:
    current_best = tour_length
  evals += 1
  return tour_length  


'''
/****************************************************************/
/* Outputs the routes of the solution. Taken as input           */
/* an array of node indeces and its length                      */
/****************************************************************/
'''

def print_solution(routes, size):
  for i in size:
    print(routes[i])


'''
/****************************************************************/
/* Validates the routes of the solution. Taken as input         */
/* an array of node indeces and its length                      */
/****************************************************************/
'''

def check_solution(t, size):
  checkDepotReturn = 0
  energy_temp = batteryCapacity
  capacity_temp = maxCapacity
  distance_temp = 0.0
  for i in range(size-1):
    if t[i+1] == 0:
      checkDepotReturn += 1
    ffrom = t[i]
    to = t[i+1]
    capacity_temp = capacity_temp - int(get_customer_demand(to)[1])
    energy_temp -= get_energy_consumption(ffrom,to)
    distance_temp += get_distance(ffrom,to)

    if capacity_temp < 0.0:
      #print("error: capacity below 0 at customer " + str(to))
      #print_solution(t,size)
      return False
    if energy_temp < 0.0:
      #print("error: energy below 0 from " + str(ffrom) + " to " + str(to))
      #print_solution(t,size)
      return False
    if is_charging_station(to) == True:
      if to == Depot:
        capacity_temp = maxCapacity
        energy_temp = batteryCapacity
      else:
        energy_temp = batteryCapacity
  if distance_temp != fitness_evaluation(t,size):
    print("error: check fitness evaluation")
    return False
  elif checkDepotReturn > vehicles + 1:
    #print("error: too many travel to depot")
    return False
  return True


'''
/****************************************************************/
/* Returns the distance between two points: from and to. Can be */
/* used to evaluate a part of the solution. The fitness         */
/* evaluation count will be proportional to the problem size    */
/****************************************************************/
'''

def get_distance(ffrom, to):
  global evals
  evals += (1.0/actualProblemSize)
  return distances[ffrom][to]

'''
/****************************************************************/
/* Returns the energy consumed when travelling between two      */
/* points: from and to.                                         */
/****************************************************************/
''' 

def get_energy_consumption(ffrom, to):
  '''/*DO NOT USE THIS FUNCTION MAKE ANY CALCULATIONS TO THE ROUTE COST*/'''
  return energy_consumption*distances[ffrom][to]

'''
/****************************************************************/
/* Returns the demand for a specific customer                   */
/* points: from and to.                                         */
/****************************************************************/
'''

def get_customer_demand(customer):
  return cust_demand[customer]

'''
/****************************************************************/
/* Returns true when a specific node is a charging station;     */
/* and false otherwise                                          */
/****************************************************************/
'''

def is_charging_station(node):
  if charging_station[node]:
    return True
  else:
    return False

'''
/****************************************************************/
/* Returns the best solution quality so far                     */
/****************************************************************/
'''

def get_current_best():
  return current_best

'''
/*******************************************************************/
/* Reset the best solution quality so far for a new indepedent run */
/*******************************************************************/
'''

def init_current_best():
  global current_best
  current_best = sys.maxsize

'''
/****************************************************************/
/* Returns the current count of fitness evaluations             */
/****************************************************************/
''' 

def get_evals():
  return evals

'''
/****************************************************************/
/* Reset the evaluation counter for a new indepedent run        */
/****************************************************************/
''' 

def init_evals():
  global evals
  evals = 0

'''
/****************************************************************/
/* Clear the allocated memory                                   */
/****************************************************************/
'''

def free_EVRP():
  global node_list,cust_demand,charging_station,distances
  del node_list,cust_demand,charging_station
  for i in actualProblemSize:
    del distances[i]
  del distances

  gc.collect()

'''
bench = open('Benchmarks/bench1.evrp', 'r')
read_problem(bench)
print(problem_size)
print(maxCapacity)
print(vehicles)
print(batteryCapacity)
print(energy_consumption)
print(numOfStations)
print(optimum)
print(node_list)
print(cust_demand)
print(charging_station)
'''