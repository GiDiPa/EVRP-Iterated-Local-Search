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
energy_temp = 0.0
capacity_temp = 0.0
'''
/*initialize the structure of your heuristic in this function*/
'''

def init_heuristic():
  #global best_sol
  best_sol = Solution(tour=[None for x in range(EVRP.numOfCustomers + 1000)],id = 1, steps = 0, tour_length = sys.maxsize)
  return best_sol

def run_array_permutated(r):
  r_copy = r
  random.seed()
  random.shuffle(r_copy)
  return r_copy


############################################################################################
#                                                                                          #
#                                                                                          #
#                                                                                          #
#                                   HEURISTIC SOLUTION                                     #
#                                                                                          #
#                                                                                          #
#                                                                                          #
############################################################################################


def checkStationsTour(stations_list,ffrom,to,energy_temp): #minimum path compute for charging stations in my zone
  minBestDistanceFromStationTo, minBestDistanceFromStation = sys.maxsize, sys.maxsize
  bestFromStation = None
  minPathCommonStation = None
  stationComputedPathList = []
  for station in stations_list:
    if station == ffrom:
      continue
    elif energy_temp + float(EVRP.get_energy_consumption(ffrom,station)) <= EVRP.batteryCapacity:
      if float(EVRP.get_energy_consumption(ffrom,station)) < minBestDistanceFromStation:
        minBestDistanceFromStation = float(EVRP.get_energy_consumption(ffrom,station))
        bestFromStation = station
         
      from_station = float(EVRP.get_energy_consumption(ffrom,station))
      station_to = float(EVRP.get_energy_consumption(station,to))
      if from_station + station_to < minBestDistanceFromStationTo:
        minBestDistanceFromStationTo = from_station + station_to
        minPathCommonStation = station

  stationComputedPathList.append(bestFromStation)
  stationComputedPathList.append(minPathCommonStation)
  return stationComputedPathList
  

def revertBack(i,customer_shuffle_list,stations_list,best_sol):#function to go back if got stuck and force vehicles to stop at charging station before continue
  global energy_temp 
  global capacity_temp

  wflag = True
  best_sol.steps -= 1
  ffrom = best_sol.tour[best_sol.steps - 1]
  to = customer_shuffle_list[i]
  capacity_temp -= float(EVRP.get_customer_demand(to)[1])
  energy_temp -= EVRP.get_energy_consumption(ffrom,to)
  minToStation = checkStationsTour(stations_list,ffrom,to,energy_temp)
  if minToStation[0] != None:
    if energy_temp + float(EVRP.get_energy_consumption(ffrom,minToStation[1])) <= EVRP.batteryCapacity:
      energy_temp = 0.0
      best_sol.tour[best_sol.steps] = minToStation[1]
      best_sol.steps += 1
      wflag = False
      return wflag
      #attemptFlag = True
            
    else:
      energy_temp = 0.0
      best_sol.tour[best_sol.steps] = minToStation[0]
      best_sol.steps += 1    
      wflag = False
      return wflag
      #attemptFlag = True
  '''
  elif energy_temp + float(EVRP.get_energy_consumption(ffrom,0)) <= EVRP.batteryCapacity:
    capacity_temp = 0.0
    energy_temp = 0.0
    best_sol.tour[best_sol.steps] = EVRP.Depot
    best_sol.steps += 1
    wflag = False
    return wflag
    #attemptFlag = True
  '''  
  return wflag
    

def run_heuristic(customer_shuffle_list,stations_list, best_sol):
  global energy_temp 
  global capacity_temp

  energy_temp = 0.0
  capacity_temp = 0.0
  best_sol.steps = 0
  best_sol.tour_length = sys.maxsize
  best_sol.tour[0] = EVRP.Depot
  best_sol.steps += 1
  i = 0
  #attemptFlag = True
  
  while i <= EVRP.numOfCustomers:
    #first if: final step when every customer is iterated
    if i == EVRP.numOfCustomers:
      if best_sol.tour[best_sol.steps - 1] != EVRP.Depot:
        if energy_temp + float(EVRP.get_energy_consumption(to,0)) <= EVRP.batteryCapacity:#enough energy then back to depot
          best_sol.tour[best_sol.steps] = EVRP.Depot
          best_sol.steps += 1
          i += 1
          
        else:
          finalCheckStationRoute = checkStationsTour(stations_list,to,0,energy_temp)#function to compute minimum route from ffrom and stations
          #not enough energy for depot
          if finalCheckStationRoute[0] != None:
            if energy_temp + float(EVRP.get_energy_consumption(to,finalCheckStationRoute[1])) <= EVRP.batteryCapacity:
              #i go through the best charging station with minimum path between ffrom and depot 
              energy_temp = 0.0
              best_sol.tour[best_sol.steps] = finalCheckStationRoute[1]
              best_sol.steps += 1
              
            else:
              #if not, go to the nearest charging station, this step is probably useless because the value above can be the same as this in worst cases
              energy_temp = 0.0
              best_sol.tour[best_sol.steps] = finalCheckStationRoute[0]
              best_sol.steps += 1
              

          else:
            wflag = True
            while wflag:
              i -= 1
              #revertBack is the function that let me go back if I get stuck on route because of the lack of energy
              wflag = revertBack(i,customer_shuffle_list,stations_list,best_sol)
               
    
    else:
      #not the final step and takes all the actual value
      ffrom = best_sol.tour[best_sol.steps - 1]
      to = customer_shuffle_list[i]
      stationTourSolutions = []
      

      if capacity_temp + float(EVRP.get_customer_demand(to)[1]) > EVRP.maxCapacity:#if vehicle capacity gets more than his max Capacity we need to go to depot
        if energy_temp + float(EVRP.get_energy_consumption(ffrom,0)) <= EVRP.batteryCapacity:
          #this condition if charge is ok to go directly to depot
          capacity_temp = 0.0
          energy_temp = 0.0
          best_sol.tour[best_sol.steps] = EVRP.Depot
          best_sol.steps += 1
        else:
          stationTourSolutions = checkStationsTour(stations_list,ffrom,to,energy_temp)
          #this if vehicles can't go back directly and needs to stop at charging station 
          if stationTourSolutions[0] != None:
            if energy_temp + float(EVRP.get_energy_consumption(to,stationTourSolutions[1])) <= EVRP.batteryCapacity:
              #i go through the best charging station with minimum path between ffrom and depot 
              energy_temp = 0.0
              best_sol.tour[best_sol.steps] = stationTourSolutions[1]
              best_sol.steps += 1
            else:
              energy_temp = 0.0
              best_sol.tour[best_sol.steps] = stationTourSolutions[0]
              best_sol.steps += 1

          else:
            #revert if vehicles get stuck
            wflag = True
            while wflag:
              i -= 1
              wflag = revertBack(i,customer_shuffle_list,stations_list,best_sol)
            

      else:
        #if capacity is good enough i check the battery between customers
        if energy_temp + EVRP.get_energy_consumption(ffrom,to) <= EVRP.batteryCapacity:
          capacity_temp += float(EVRP.get_customer_demand(to)[1])
          energy_temp += EVRP.get_energy_consumption(ffrom,to)
          best_sol.tour[best_sol.steps] = to
          best_sol.steps += 1
          i += 1

        #if not enough battery I search the minimum path between two nodes with charging station in the middle
        elif energy_temp + float(EVRP.get_energy_consumption(ffrom,to)) > EVRP.batteryCapacity:
          stationTourSolutions = checkStationsTour(stations_list,ffrom,to,energy_temp)
          if stationTourSolutions[0] != None:
            if energy_temp + float(EVRP.get_energy_consumption(ffrom,stationTourSolutions[1])) <= EVRP.batteryCapacity:  
              energy_temp = 0.0
              best_sol.tour[best_sol.steps] = stationTourSolutions[1]
              best_sol.steps += 1
          
            else:
              energy_temp = 0.0
              best_sol.tour[best_sol.steps] = stationTourSolutions[0]
              best_sol.steps += 1
      
          else:
            #revert if i got stuck.
            wflag = True
            while wflag:
              i -= 1
              wflag = revertBack(i,customer_shuffle_list,stations_list,best_sol)
  
  best_sol.tour_length = EVRP.fitness_evaluation(best_sol.tour, best_sol.steps)
  return best_sol



'''
if attemptFlag == True:
  best = float(EVRP.get_energy_consumption(ffrom,to))              
  for attempt in range(i+1,len(customer_shuffle_list)):
    if float(EVRP.get_energy_consumption(ffrom,customer_shuffle_list[attempt])) < best and capacity_temp + float(EVRP.get_customer_demand(customer_shuffle_list[attempt])[1]) <= EVRP.maxCapacity:
      best = float(EVRP.get_energy_consumption(ffrom,customer_shuffle_list[attempt]))
      customer_shuffle_list[i], customer_shuffle_list[attempt] = customer_shuffle_list[attempt], customer_shuffle_list[i]
  attemptFlag = False      
to = customer_shuffle_list[i]
minToStation = checkStationsTour(stations_list,ffrom,to,energy_temp)


if energy_temp + float(EVRP.get_energy_consumption(ffrom,to)) <= EVRP.batteryCapacity: #and attemptFlag == True:
  capacity_temp += float(EVRP.get_customer_demand(to)[1])
  energy_temp += EVRP.get_energy_consumption(ffrom,to)
  best_sol.tour[best_sol.steps] = to
  best_sol.steps += 1
  i += 1
  wflag = False
  #attemptFlag = False
'''



'''
else:
if i < len(customer_shuffle_list):
  randomCustomer = random.randrange(i, len(customer_shuffle_list))
  customer_shuffle_list[i], customer_shuffle_list[randomCustomer] = customer_shuffle_list[randomCustomer], customer_shuffle_list[i] #implement swap random of remaining
  best_sol.tour[best_sol.steps] = None
'''  


'''
if best_sol.tour[best_sol.steps - 1] == best_sol.tour[best_sol.steps - 2] and EVRP.is_charging_station(best_sol.tour[best_sol.steps - 2]):
  if i < len(customer_shuffle_list):
    randomCustomer = random.randrange(i, len(customer_shuffle_list))
    customer_shuffle_list[i], customer_shuffle_list[randomCustomer] = customer_shuffle_list[randomCustomer], customer_shuffle_list[i] #implement swap random of remaining
    best_sol.steps -= 1
    best_sol.tour[best_sol.steps] = None
    energy_temp = 0.0
  else:
    best_sol.steps -= 1
    best_sol.tour[best_sol.steps] = None
    energy_temp = 0.0
    stationTourSolutions = checkStationsTour(stations_list,ffrom,0,energy_temp)
    if stationTourSolutions[0] != None:
      if energy_temp + float(EVRP.get_energy_consumption(ffrom,stationTourSolutions[2])) <= EVRP.batteryCapacity:
        energy_temp = 0.0
        best_sol.tour[best_sol.steps] = stationTourSolutions[2]
        best_sol.steps += 1
      else:
        energy_temp = 0.0
        best_sol.tour[best_sol.steps] = stationTourSolutions[0]
        best_sol.steps += 1
'''