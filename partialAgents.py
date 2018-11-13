# partialAgent.py
# parsons/15-oct-2017
#
# Version 1
#
# The starting point for CW1.
#
# Intended to work with the PacMan AI projects from:
#
# http://ai.berkeley.edu/
#
# These use a simple API that allow us to control Pacman's interaction with
# the environment adding a layer on top of the AI Berkeley code.
#
# As required by the licensing agreement for the PacMan AI we have:
#
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

# The agent here is was written by Simon Parsons, based on the code in
# pacmanAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util

class PartialAgent(Agent):

    # Constructor
    def __init__(self):
        # print "Starting up!"
        name = "Pacman"
        self.moveCounter = 0
        self.gridWidth = None
        self.gridHeight = None
        self.map = []
        self.cur = None

    def final(self, state):

        print " __________________"
        print "|                  |"
        print "|    Game Over!    |"
        print "|                  |"
        print " ------------------"


##############################################################################

    ## Decide which direction to go

    def getAction(self, state):
        if self.moveCounter == 0: self.start(state)
        self.update(state)
        print "\n"

        self.printMap(state)


        return self.decideMove(state)






##############################################################################

    def start(self, state):
        self.getGridSize(state)
        print "width : ", self.gridWidth, " height : ", self.gridHeight
        self.setEmptyMap(state)
        self.setFoodLocations(state)
        self.setWallLocations(state)


    def update(self, state):
        self.moveCounter+=1
        self.cur = api.whereAmI(state)
        cur = self.cur
        if self.map[cur[0]][cur[1]] == 2: self.map[cur[0]][cur[1]] -= 1


    def getGridSize(self, state):
        corners = api.corners(state)
        width = corners[1][0] - corners[0][0] + 1
        height = corners[2][1] -corners[0][1] + 1
        self.gridWidth = width
        self.gridHeight = height

    def setEmptyMap(self, state):
        for x in range(0, self.gridWidth):
            tempx = []
            for y in range(0, self.gridHeight):
                tempx.append(1)
            self.map.append(tempx)

    def printMap(self, state):
        for y in range(self.gridHeight-1, -1 , -1):
            for x in self.map:
                print x[y], " ",
            print "\n"


    ## Wall value = 0
    ## Food value = 2
    ## Empty space = 1
    def setFoodLocations(self, state):
        for x in api.food(state):
            self.map[x[0]][x[1]] = 2

    ## Wall value = 0
    ## Food value = 2
    ## Empty space = 1
    def setWallLocations(self, state):
        for x in api.walls(state):
            self.map[x[0]][x[1]] = 0

    def possibleMoves(self, state):
        ## returns list of (direction, coord) pairs that are in legal moves)

        cur = self.cur
        moves = api.legalActions(state)
        possibleMoves = []

        #north
        if Directions.NORTH in moves:
            possibleMoves.append((Directions.NORTH, (cur[0], cur[1]+1)))
        #east
        if Directions.EAST in moves:
            possibleMoves.append((Directions.EAST, (cur[0]+1, cur[1])))
        #south
        if Directions.SOUTH in moves:
            possibleMoves.append((Directions.SOUTH, (cur[0], cur[1]-1)))
        #west
        if Directions.WEST in moves:
            possibleMoves.append((Directions.WEST, (cur[0]-1, cur[1])))

        return possibleMoves

    def decideMove(self, state):
        ## look at each possible move
        # for each possible move look at its outcomes
        # calculate the value of that move based on outcomes
        # value of move = sum of all outcomes (value * probability)

        # [[(dir, coord), value]]
        moves = []
        # for each possible move
        for x in self.possibleMoves(state):
            if x[0] == Directions.NORTH:
                # [dir, coord, value, prob]
                forward = [x[0], x[1], self.getValue(state, (x[1])), 0.8]
                left = [Directions.WEST, (x[1][0]-1, x[1][1]), self.getValue(state, (x[1][0]-1, x[1][1])), 0.1]
                right = [Directions.EAST, (x[1][0]+1, x[1][1]), self.getValue(state, (x[1][0]+1, x[1][1])), 0.1]
                value = forward[2]*forward[3] + left[2]*left[3] + right[2]*right[3]
                # [move, value]
                moves.append([x, value])
            if x[0] == Directions.EAST:
                # [dir, coord, value, prob]
                forward = [x[0], x[1], self.getValue(state, (x[1])), 0.8]
                left = [Directions.SOUTH, (x[1][0], x[1][1]+1), self.getValue(state, (x[1][0], x[1][1]+1)), 0.1]
                right = [Directions.NORTH, (x[1][0], x[1][1]-1), self.getValue(state, (x[1][0], x[1][1]-1)), 0.1]
                value = forward[2]*forward[3] + left[2]*left[3] + right[2]*right[3]
                # [move, value]
                moves.append([x, value])
            if x[0] == Directions.SOUTH:
                # [dir, coord, value, prob]
                forward = [x[0], x[1], self.getValue(state, (x[1])), 0.8]
                left = [Directions.EAST, (x[1][0]+1, x[1][1]), self.getValue(state, (x[1][0]+1, x[1][1])), 0.1]
                right = [Directions.WEST, (x[1][0]-1, x[1][1]), self.getValue(state, (x[1][0]-1, x[1][1])), 0.1]
                value = forward[2]*forward[3] + left[2]*left[3] + right[2]*right[3]
                # [move, value]
                moves.append([x, value])
            if x[0] == Directions.WEST:
                # [dir, coord, value, prob]
                forward = [x[0], x[1], self.getValue(state, (x[1])), 0.8]
                left = [Directions.SOUTH, (x[1][0], x[1][1]-1), self.getValue(state, (x[1][0], x[1][1]-1)), 0.1]
                right = [Directions.NORTH, (x[1][0], x[1][1]+1), self.getValue(state, (x[1][0], x[1][1]+1)), 0.1]
                value = forward[2]*forward[3] + left[2]*left[3] + right[2]*right[3]
                # [move, value]
                moves.append([x, value])

        highest = -1000
        bestMove = None
        for x in moves:
            if x[1] > highest:
                highest = x[1]
                bestMove = x[0]

        print "Values of moves : ", moves
        print "Best move : ", bestMove, "\n"
        print "########################################", "\n"
        return bestMove[0]



    def adjacentCoords(self, state, cur):
        ## returns list of the 4 surrounding coords
        coords = []
        coords.append((cur[0], cur[1]+1))
        coords.append((cur[0]+1, cur[1]))
        coords.append((cur[0], cur[1]-1))
        coords.append((cur[0]-1, cur[1]))
        return coords


    # def outcomes(self, state, moves):
    #     ## returns the list of outcomes of a move
    #     # (intended square, right square, left square)
    #     moves.remove(self.cur)
    #     return moves

    def outcomes(self, state, cur, dir):
        ## cur is current coord
        ## coord is the coord we are looking at the outcomes of

        ## returns the list of outcomes of moving to a coord from cur
        adj = self.adjacentCoords(state, cur)

        #north : remove backwards
        if dir == Directions.NORTH : adj.remove((cur[0], cur[1]-1))
        #east : remove backwards
        if dir == Directions.NORTH : adj.remove((cur[0]-1, cur[1]))
        #south : remove backwards
        if dir == Directions.NORTH : adj.remove((cur[0], cur[1]+1))
        #west : remove backwards
        if dir == Directions.NORTH : adj.remove((cur[0]+1, cur[1]))

        return adj

    def getValue(self, state, coord):
        x = coord[0]
        y = coord[1]
        return self.map[x][y]

















    ###
