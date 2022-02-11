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


def checkStationsTour(stations_list,ffrom,to,energy_temp):
  minBestDistanceToStation, minBestDistanceFromStationTo, minBestDistanceFromStation = sys.maxsize, sys.maxsize, sys.maxsize
  bestFromStation = None
  bestFromToStation = None
  minPathCommonStation = None
  stationComputedPathList = []
  for station in stations_list:
    if station == ffrom:
      continue
    elif energy_temp + float(EVRP.get_energy_consumption(ffrom,station)) <= EVRP.batteryCapacity:
      if float(EVRP.get_energy_consumption(ffrom,station)) < minBestDistanceFromStation:
        minBestDistanceFromStation = float(EVRP.get_energy_consumption(ffrom,station))
        bestFromStation = station

      if energy_temp + float(EVRP.get_energy_consumption(ffrom,to)) + float(EVRP.get_energy_consumption(to,station)) <= EVRP.batteryCapacity:
        if float(EVRP.get_energy_consumption(to,station)) < minBestDistanceToStation:
          minBestDistanceToStation = float(EVRP.get_energy_consumption(to,station))
          bestFromToStation = station
         
      from_station = float(EVRP.get_energy_consumption(ffrom,station))
      station_to = float(EVRP.get_energy_consumption(station,to))
      if from_station + station_to < minBestDistanceFromStationTo:
        minBestDistanceFromStationTo = from_station + station_to
        minPathCommonStation = station

  stationComputedPathList.append(bestFromStation)
  stationComputedPathList.append(bestFromToStation)
  stationComputedPathList.append(minPathCommonStation)
  return stationComputedPathList
  
    

def run_heuristic(customer_shuffle_list,stations_list, best_sol):
  energy_temp = 0.0
  capacity_temp = 0.0

  best_sol.steps = 0
  best_sol.tour_length = sys.maxsize
  best_sol.tour[0] = EVRP.Depot
  best_sol.steps += 1
  i = 0
  #attemptFlag = True
  
  while i <= EVRP.numOfCustomers:
    if i == EVRP.numOfCustomers:
      if best_sol.tour[best_sol.steps - 1] != EVRP.Depot:
        finalCheckStationRoute = checkStationsTour(stations_list,to,0,energy_temp)
        if energy_temp + float(EVRP.get_energy_consumption(to,0)) <= EVRP.batteryCapacity:
          best_sol.tour[best_sol.steps] = EVRP.Depot
          best_sol.steps += 1
          i += 1
          
        elif finalCheckStationRoute[0] != None:
          if energy_temp + float(EVRP.get_energy_consumption(to,finalCheckStationRoute[2])) <= EVRP.batteryCapacity:
            energy_temp = 0.0
            best_sol.tour[best_sol.steps] = finalCheckStationRoute[2]
            best_sol.steps += 1
            if energy_temp + float(EVRP.get_energy_consumption(finalCheckStationRoute[2],0)) <= EVRP.batteryCapacity:
              best_sol.tour[best_sol.steps] = EVRP.Depot
              best_sol.steps += 1
              i += 1
          else:
            energy_temp = 0.0
            best_sol.tour[best_sol.steps] = finalCheckStationRoute[0]
            best_sol.steps += 1
            if energy_temp + float(EVRP.get_energy_consumption(finalCheckStationRoute[0]),0) <= EVRP.batteryCapacity:
              best_sol.tour[best_sol.steps] = EVRP.Depot
              best_sol.steps += 1
              i += 1

        else:
          wflag = True
          while wflag:
            i -= 1
            best_sol.steps -= 1
            ffrom = best_sol.tour[best_sol.steps - 1]
            to = customer_shuffle_list[i]
            capacity_temp -= float(EVRP.get_customer_demand(to)[1])
            energy_temp -= EVRP.get_energy_consumption(ffrom,to)
            minToStation = checkStationsTour(stations_list,ffrom,to,energy_temp)

            if minToStation[0] != None:
              if energy_temp + float(EVRP.get_energy_consumption(ffrom,minToStation[2])) <= EVRP.batteryCapacity:
                energy_temp = 0.0
                best_sol.tour[best_sol.steps] = minToStation[2]
                best_sol.steps += 1
                wflag = False
            
              else:
                energy_temp = 0.0
                best_sol.tour[best_sol.steps] = minToStation[0]
                best_sol.steps += 1    
                wflag = False    
    
    else:
      ffrom = best_sol.tour[best_sol.steps - 1]
      to = customer_shuffle_list[i]
      minToStation = sys.maxsize
      stationTourSolutions = []
      stationTourSolutions = checkStationsTour(stations_list,ffrom,to,energy_temp)
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
      if capacity_temp + float(EVRP.get_customer_demand(to)[1]) > EVRP.maxCapacity:
        if energy_temp + float(EVRP.get_energy_consumption(ffrom,0)) <= EVRP.batteryCapacity:
          capacity_temp = 0.0
          energy_temp = 0.0
          best_sol.tour[best_sol.steps] = EVRP.Depot
          best_sol.steps += 1

        elif stationTourSolutions[0] != None:
          energy_temp = 0.0
          best_sol.tour[best_sol.steps] = stationTourSolutions[0]
          best_sol.steps += 1

        else:
          wflag = True
          while wflag:
            i -= 1
            best_sol.steps -= 1
            ffrom = best_sol.tour[best_sol.steps - 1]
            to = customer_shuffle_list[i]
            capacity_temp -= float(EVRP.get_customer_demand(to)[1])
            energy_temp -= EVRP.get_energy_consumption(ffrom,to)
            minToStation = checkStationsTour(stations_list,ffrom,to,energy_temp)
            
            if energy_temp + float(EVRP.get_energy_consumption(ffrom,0)) <= EVRP.batteryCapacity:
              capacity_temp = 0.0
              energy_temp = 0.0
              best_sol.tour[best_sol.steps] = EVRP.Depot
              best_sol.steps += 1
              wflag = False
            
            elif minToStation[0] != None:
              energy_temp = 0.0
              best_sol.tour[best_sol.steps] = minToStation[0]
              best_sol.steps += 1  
              wflag = False        
      else:
        if energy_temp + EVRP.get_energy_consumption(ffrom,to) <= EVRP.batteryCapacity:
          capacity_temp += float(EVRP.get_customer_demand(to)[1])
          energy_temp += EVRP.get_energy_consumption(ffrom,to)
          best_sol.tour[best_sol.steps] = to
          best_sol.steps += 1
          i += 1

        elif energy_temp + float(EVRP.get_energy_consumption(ffrom,to)) > EVRP.batteryCapacity:
          if stationTourSolutions[0] != None:
            if energy_temp + float(EVRP.get_energy_consumption(ffrom,stationTourSolutions[2])) <= EVRP.batteryCapacity:  
              energy_temp = 0.0
              best_sol.tour[best_sol.steps] = stationTourSolutions[2]
              best_sol.steps += 1
          
            else:
              energy_temp = 0.0
              best_sol.tour[best_sol.steps] = stationTourSolutions[0]
              best_sol.steps += 1

          elif energy_temp + float(EVRP.get_energy_consumption(ffrom,0)) <= EVRP.batteryCapacity:
            energy_temp = 0.0
            capacity_temp = 0.0
            best_sol.tour[best_sol.steps] = EVRP.Depot
            best_sol.steps += 1
      
          else:
            wflag = True
            
            while wflag:
              i -= 1
              best_sol.steps -= 1
              ffrom = best_sol.tour[best_sol.steps - 1]
              to = customer_shuffle_list[i]
              capacity_temp -= float(EVRP.get_customer_demand(to)[1])
              energy_temp -= EVRP.get_energy_consumption(ffrom,to)
              minToStation = checkStationsTour(stations_list,ffrom,to,energy_temp)

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

              if minToStation[0] != None:
                if energy_temp + float(EVRP.get_energy_consumption(ffrom,minToStation[2])) <= EVRP.batteryCapacity:
                  energy_temp = 0.0
                  best_sol.tour[best_sol.steps] = minToStation[2]
                  best_sol.steps += 1
                  wflag = False
                  #attemptFlag = True
            
                else:
                  energy_temp = 0.0
                  best_sol.tour[best_sol.steps] = minToStation[0]
                  best_sol.steps += 1    
                  wflag = False
                  #attemptFlag = True
              
              elif energy_temp + float(EVRP.get_energy_consumption(ffrom,0)) <= EVRP.batteryCapacity:
                capacity_temp = 0.0
                energy_temp = 0.0
                best_sol.tour[best_sol.steps] = EVRP.Depot
                best_sol.steps += 1
                wflag = False
                #attemptFlag = True
            
            '''
            else:
              if i < len(customer_shuffle_list):
                randomCustomer = random.randrange(i, len(customer_shuffle_list))
                customer_shuffle_list[i], customer_shuffle_list[randomCustomer] = customer_shuffle_list[randomCustomer], customer_shuffle_list[i] #implement swap random of remaining
                best_sol.tour[best_sol.steps] = None
            '''    

  best_sol.tour_length = EVRP.fitness_evaluation(best_sol.tour, best_sol.steps)
  return best_sol



