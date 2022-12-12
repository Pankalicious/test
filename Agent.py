import random

import numpy as np
import math

class Agent:
    def __init__(self, map, learningRate, gamma):
        self.map = map
        self.location = map.startPoint

        self.moveCount = 0
        self.totalReward = 0

        self.gridSize = 5

        self.learningRate = learningRate
        self.gamma = gamma

        self.goalReward = 10
        self.reward = -0.04

        self.trailType = ''
        self.elevationDifficulty = ''

        #transition model if no user inputs given
        self.probOn = 0.5
        self.probOff = 0.5

        self.prob2m = 0.45
        self.prob5m = 0.45
        self.prob10m = 0.1


    def findPossibleMoves(self, location):
        moves = []
        x = location[0]
        y = location[1]

        #left
        if (y > 0 and self.map.trailMap[x][y-1] != 'X'):
            moves.append([x, y-1, 0])
        #rigth
        if (y < (self.map.columns - 1) and self.map.trailMap[x][y+1] != 'X'):
            moves.append([x, y+1, 1])

        # up
        if (x > 0 and self.map.trailMap[x - 1][y] != 'X'):
            moves.append([x - 1, y, 2])
        # down
        if (x < (self.map.rows - 1) and self.map.trailMap[x + 1][y] != 'X'):
            moves.append([x + 1, y, 3])

        return moves

    def setTransitionModel(self, trailType, elevationDifficulty):
        self.trailType = trailType
        self.elevationDifficulty = elevationDifficulty

        #trail type
        if trailType == 'On':
            self.probOn = 0.7
            self.probOff = 0.3
        elif trailType == 'Off':
            self.probOn = 0.3
            self.probOff = 0.7
        elif trailType == "Hybrid":
            self.probOn = 0.55
            self.probOff = 0.45

        #elevation difficulty
        if elevationDifficulty == 'Low':
            self.prob2m = 0.6
            self.prob5m = 0.25
            self.prob10m = 0.15
        elif elevationDifficulty == 'Medium':
            self.prob2m = 0.5
            self.prob5m = 0.35
            self.prob10m = 0.15
        elif elevationDifficulty == 'High':
            self.prob2m = 0.30
            self.prob5m = 0.35
            self.prob10m = 0.35
        return

    def findNextLocation(self,location):
        moves = self.findPossibleMoves(location)

        # if random.uniform(0, 1) < epsilon:
        #     index = np.random.choice(len(moves))
        #     return moves[index]

        probabilities = []
        currentElevation = self.map.elevationMap[location[0]][location[1]]
        for row in moves:
            if self.map.trailMap[row[0]][row[1]] == 0:
                prob1 = self.probOff
            elif self.map.trailMap[row[0]][row[1]] == 1:
                prob1 = self.probOn
            elif self.map.trailMap[row[0]][row[1]] == 'G':
                prob1 = 0.9


            if abs(self.map.elevationMap[row[0]][row[1]] - currentElevation) <= 2:
                prob2 = self.prob2m
            elif abs(self.map.elevationMap[row[0]][row[1]] - currentElevation) <= 5:
                prob2 = self.prob5m
            else:
                prob2 = self.prob10m

            probabilities.append(prob1*prob2)

        norm = [float(i) / sum(probabilities) for i in probabilities]
        index = np.random.choice(len(moves),p=norm)

        return moves[index]

    def takeMove(self, nextLocation):
        self.location = nextLocation[:2]
        self.moveCount+=1

    def updateQTable(self, previousLocation, currentLocation, nextLocation):
        prev = previousLocation[:2]
        current = currentLocation[:2]

        nextIndex = nextLocation[2]
        if self.map.qTable[current[0]][current[1]] == 'G':
            nextQ = self.goalReward
        else:
            #Qlearning
            moves = self.findPossibleMoves(currentLocation)
            maximum = -100
            for move in moves:
                qValue = self.map.qTable[current[0]][current[1]][move[2]]
                if qValue > maximum:
                    maximum = qValue
            nextQ = maximum
            #SARSA
            #nextQ = self.map.qTable[current[0]][current[1]][nextIndex]

        index = currentLocation[2]
        prevQ = self.map.qTable[prev[0]][prev[1]][index]

        self.map.qTable[prev[0]][prev[1]][index] = round(
            prevQ + self.learningRate * (self.calculateRewardFull(prev, current) + self.gamma * nextQ - prevQ),
            2)

        self.totalReward += self.calculateRewardFull(prev, current)



    def calculateReward(self, location1, location2):
        reward = 0
        if self.trail_steepness(location1, location2) > 0.385:
            reward = -0.04
        else:
            reward = -0.02
        return reward


    def goalReached(self):
        return self.map.trailMap[self.location[0]][self.location[1]] == 'G'

    def trail_steepness(self, location1, location2):
        elevation1 = self.map.elevationMap[location2[0]][location2[1]]
        elevation2 = self.map.elevationMap[location1[0]][location1[1]]
        return math.atan((elevation2 - elevation1) / self.gridSize)

    def calculateRewardFull(self, location1, location2):
        trail = self.map.trailMap[location2[0]][location2[1]]

        elevation2 = self.map.elevationMap[location2[0]][location2[1]]
        elevation1 = self.map.elevationMap[location1[0]][location1[1]]

        distanceToGoal1 = (location1[0] - self.map.goal[0]) + (location1[1] - self.map.goal[1])
        distanceToGoal2 =(location2[0] - self.map.goal[0]) +(location2[1] - self.map.goal[1])


        if distanceToGoal2 <= distanceToGoal1:
            goalFactor = 0.7
        else:
            goalFactor = 1

        rewardFactorTrail = 1
        if trail == 1:
            if self.trailType == 'On':
                rewardFactorTrail = 1
            elif self.trailType == 'Off':
                rewardFactorTrail = 5
            elif self.trailType == 'Hybrid':
                rewardFactorTrail == 1
        elif trail == 0:
            if self.trailType == 'On':
                rewardFactorTrail = 10
            elif self.trailType == 'Off':
                rewardFactorTrail = 1
            elif self.trailType == 'Hybrid':
                rewardFactorTrail == 4

        elevationChange = elevation2 -elevation1
        rewardFactorElevation = 1
        if elevationChange <= 2:
            if self.elevationDifficulty == 'Low':
                rewardFactorElevation = 1
            elif self.elevationDifficulty == 'Medium':
                rewardFactorElevation = 1
            elif self.elevationDifficulty == 'High':
                rewardFactorElevation = 3

        elif elevationChange <= 5:
            if self.elevationDifficulty == 'Low':
                rewardFactorElevation = 5
            elif self.elevationDifficulty == 'Medium':
                rewardFactorElevation = 3
            elif self.elevationDifficulty == 'High':
                rewardFactorElevation = 2
        else:
            if self.elevationDifficulty == 'Low':
                rewardFactorElevation = 10
            elif self.elevationDifficulty == 'Medium':
                rewardFactorElevation = 5
            elif self.elevationDifficulty == 'High':
                rewardFactorElevation = 1

        reward = self.reward * goalFactor * (rewardFactorTrail + rewardFactorElevation)
        return reward


