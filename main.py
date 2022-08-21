from collections import namedtuple
from fileinput import hook_compressed
import json
from dataclasses import dataclass
from operator import attrgetter


class ShipCostTimeToNextPort:
    def __init__(self, Cost, Time):
        self.Cost = Cost
        self.Time = Time


class ShipSpeedTimeToNextPort:
    def __init__(self, Speed, Time):
        self.Speed = Speed
        self.Time = Time


class Port:
    def __init__(self, THC, TD,  AtracationCost, Demand, Supply, Distance, DeadLine):
        self.THC = THC
        self.TD = TD
        self.AtracationCost = AtracationCost
        self.Demand = Demand
        self.Supply = Supply
        self.Distance = Distance
        self.DeadLine = DeadLine
        self.Speed = 0
        self.TimeOfTraveling = 0


class Ship:
    def __init__(self, OperationCost, LoadCapacity, LOA, A, B, C, D, Min, Max, FuelCostUnit):
        self.OperationCost = OperationCost
        self.LoadCapacity = LoadCapacity
        self.LOA = LOA
        self.A = A
        self.B = B
        self.C = C
        self.D = D
        self.Min = Min
        self.Max = Max
        self.FuelCostUnit = FuelCostUnit


def calcShipSpeedTimeToNextPort(shipData: Ship, portData: Port) -> list[ShipSpeedTimeToNextPort]:
    speedOfShip = shipData.Min

    timeToNextPort = []

    while (speedOfShip <= shipData.Max):
        timeToNextPort.append(ShipSpeedTimeToNextPort(
            speedOfShip, portData.Distance / speedOfShip))
        speedOfShip = speedOfShip + 1

    return timeToNextPort


def portCost(shipData: Ship, portData: Port):
    return (portData.THC * (portData.Demand + portData.Supply)) + (shipData.LOA * portData.TD * portData.AtracationCost)


def getFuelConsumptionRate(speed: float, shipData: Ship) -> float:    
    return (shipData.A*speed*speed*speed) + (shipData.B*speed*speed) + (shipData.C*speed) + (shipData.D)


def getFuelConsumption(timeToNextPort: ShipSpeedTimeToNextPort, shipData: Ship) -> float:
    return timeToNextPort.Time * getFuelConsumptionRate(timeToNextPort.Speed, shipData)


def getFuelConsumptionCost(timeToNextPort: ShipSpeedTimeToNextPort, shipData: Ship) -> float:
    return 1.06 * shipData.FuelCostUnit * getFuelConsumption(timeToNextPort, shipData)


def getBestConsumptionAndTimeOfTraveling(shipData: Ship, portData: Port, timesToNextPort: list[ShipSpeedTimeToNextPort], timeOfPreviousPortTraveling: float) -> ShipCostTimeToNextPort:

    bestTimeToNextPort = 0
    timeToNextPort = 0
    MinValueToTravelingToNextPortIndex = 0

    CostOfTravelingToNextPort = []

    for index in timesToNextPort:
        CostOfTravelingToNextPort.append(round(getFuelConsumptionCost(index, shipData), 2))

    while (1):
        bestCostToNextPort = min(CostOfTravelingToNextPort)
        bestCostToNextPortIndex = CostOfTravelingToNextPort.index(
            bestCostToNextPort)
        bestTimeToNextPort = timesToNextPort[bestCostToNextPortIndex].Time

        timeToNextPort = round(portData.TD + bestTimeToNextPort + timeOfPreviousPortTraveling, 1)
        if (timeToNextPort <= portData.DeadLine):
            break

        timeToNextPort = 0

        del CostOfTravelingToNextPort[bestCostToNextPortIndex]
        del timesToNextPort[bestCostToNextPortIndex]
    print("Time: ", timeToNextPort, "       Cost: : ${:0,.2f}".format(bestCostToNextPort))
    return ShipCostTimeToNextPort(bestCostToNextPort, timeToNextPort)


with open("ShipData.json", 'r') as shipDataFile:
    shipDataJSON = shipDataFile.read()

with open("PortData.json", 'r') as portDataFile:
    portDataJSON = portDataFile.read()

shipDataJSON = json.loads(shipDataJSON)
portDataJSON = json.loads(portDataJSON)
totalTimeTraveling = 0
totalCostTraveling = 0
totalPortCost = 0
numberOfShips = 4
port: Port
flux = 0

shipData = Ship(**shipDataJSON)
portsData = []

for port in portDataJSON['Ports']:
    portsData.append(Port(**port))


for port in portsData:
    timesToNextPort = calcShipSpeedTimeToNextPort(shipData, port)

    consumptionAndTimeOfTraveling = getBestConsumptionAndTimeOfTraveling(
        shipData, port, timesToNextPort, totalTimeTraveling)

    totalTimeTraveling = consumptionAndTimeOfTraveling.Time

  
    totalCostTraveling = totalCostTraveling + consumptionAndTimeOfTraveling.Cost

    totalPortCost = totalPortCost + portCost(shipData, port)

    flux = flux + (port.Demand - port.Supply)

    if (flux > shipData.LoadCapacity):
        print("The Flux's bigger than Load Capacity")

if (totalTimeTraveling == (168 * numberOfShips)):
    print("It Doesn't accept the condition 168N")

print("numberOfShips        : ${:0,.2f}".format(numberOfShips))
print("totalPortCost        : ${:0,.2f}".format(totalPortCost))
print("totalCostTraveling   : ${:0,.2f}".format(totalCostTraveling))
print("OperationCost        : ${:0,.2f}".format(shipData.OperationCost))

minimalValue = ((totalCostTraveling + totalPortCost + shipData.OperationCost) * numberOfShips)
print("Minimal Function is  : ${:0,.2f}".format(minimalValue))
