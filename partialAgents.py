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
        self.visited = []
        self.food = []
        self.last = Directions.STOP
        self.prevBuffer = [(-1,-1),(-1,-2),(-1,-3),(-1,-4),
                           (-1,-5),(-1,-6),(-1,-7),(-1,-8)]
        self.deStuckCtr = 0
        self.deGhostCtr = 0

        self.deStuckValue = 3 # number of steps pacman will run when stuck
        self.deGhostValue = 2 # number of steps pacman will run after seeing a ghost

    def final(self, state):
        self.visited = []
        self.food = []
        self.last = Directions.STOP
        self.prevBuffer = [(-1,-1),(-1,-2),(-1,-3),(-1,-4),
                           (-1,-5),(-1,-6),(-1,-7),(-1,-8)]
        self.deStuckCtr = 0
        self.deGhostCtr = 0
        print " __________________"
        print "|                  |"
        print "|    Game Over!    |"
        print "|                  |"
        print " ------------------"


##############################################################################

    ## Decide which direction to go

    def getAction(self, state):
        self.update(state)
        self.updateBuffer(state)

        ## Run from ghosts
        #
        # If pacman can see ghost, never go towards ghost
        # Effectively makes pacman run from ghosts
        if self.ghostWithinRange(state):
            return self.runFromGhost(state)

        ## Avoid ghosts
        #
        # If previous move was running from a ghost;
        # Keep running, do not backtrack for 2 additional steps
        # Prevents backtracking towards a ghost after turning a
        # corner and no longer being able to see ghost
        if self.deGhosting(state):
            return self.deGhost(state);

        ## Get unstuck
        #
        # goTowardsClosestFood/SmallestFood methods may cause pacman
        # to get stuck, unable to manoeuvre around a wall, going back
        # and forth repeatedly.
        # If pacman gets stuck, get unstuck by going in one direction
        # for certain number of steps never backtracking, until pacman
        # is no longer in position that causes him to get stuck
        if self.isStuck(state) or self.deStucking(state):
            return self.deStuck(state)

        ## Follow adjacent food
        #
        # If pacman can see food/ is right next to food, eat
        # that food, and follow that trail of food until
        # pacman can see no more in sight
        if self.foodWithinRange(state):
            return self.followFood(state)

        ## Go to closest food || smallest food
        #
        # Smallest food : food with smallest x then y coordinate
        # (westmost then southmost)
        #
        # Go to closest food that has been previously seen
        # If wall, then go to smallest food to avoid getting stuck
        if self.foodSeen(state):
            return self.goTowardsClosestFood(state)

        ## Randomly traverse
        #
        # If no food detected, randomly traverse map
        return self.randomlyTraverse(state)


##############################################################################


    def foodSeen(self, state):
        # Determines whether any food has been seen

        if len(self.food) > 0: return True
        else: return False

    def update(self, state):
        # Updates coords that pacman has visited
        # Takes note of locations of any food pacman can see
        # Disregards food that has been eaten

        cur = api.whereAmI(state)
        food = api.food(state)
        if cur not in self.visited:
            self.visited.append(cur)
        for x in food:
            if x not in self.food:
                self.food.append(x)
        if cur in self.food:
            self.food.remove(cur)

    def updateBuffer(self, state):
        # Keeps track of pacmans last 8 moves
        # Used for determining whether pacman is
        # stuck or in endless loop back and forth

        cur = api.whereAmI(state)
        self.prevBuffer.insert(0,cur)
        temp = self.prevBuffer[:8]
        self.prevBuffer = temp

    def isStuck(self, state):
        # Determines whether pacman is stuck
        # in endless loop going back and forth
        # by looking at last 8 coords

        cur = api.whereAmI(state)
        buf = set()
        for x in self.prevBuffer:
            buf.add(x)
        # If stuck then previous coords repeated
        # => less unique coords in buffer
        if len(buf) <= 4:
            self.deStuckCtr = self.deStuckValue
            return True
        return False


    def smallestFood(self, state):
        # Return coord of food with lowest x then
        # y coord (westmost then southmost)

        temp = self.food[0]
        for x in self.food:
            if x[0] < temp[0]:
                temp = x
            elif x[0] == temp[0]:
                if x[1] < temp[1]:
                    temp = x
        return temp

    def foodWithinRange(self, state):
        # Determines whether pacman can currently see food

        cur = api.whereAmI(state)
        foodAndCapsules = api.union(api.food(state), api.capsules(state))

        for x in range(1,6):
            #Food seen south of pacman
            if (cur[0], cur[1]-x) in foodAndCapsules:
                return True
            #Food seen west of pacman
            if (cur[0]-x, cur[1]) in foodAndCapsules:
                return True
            #Food seen north of pacman
            if (cur[0], cur[1]+x) in foodAndCapsules:
                return True
            #Food seen east of pacman
            if (cur[0]+x, cur[1]) in foodAndCapsules:
                return True
        #No food seen
        return False

    def deStucking(self, state):
        # Determines whether pacman is in the process
        # of getting unstuck

        if self.deStuckCtr > 0:
            self.deStuckCtr-=1
            return True
        return False

    def deGhosting(self, state):
        # Determines whether pacman is avoiding previously
        # seen ghost by running away from it

        if self.deGhostCtr > 0:
            self.deGhostCtr-=1
            return True
        return False

    def ghostWithinRange(self, state):
        # Determines whether pacman can currently see ghost

        cur = api.whereAmI(state)
        ghosts = api.ghosts(state)

        for x in range(1,6):
            #Ghost seen south of pacman
            if (cur[0], cur[1]-x) in ghosts:
                self.deGhostCtr = self.deGhostValue
                return True
            #Ghost seen west of pacman
            if (cur[0]-x, cur[1]) in ghosts:
                self.deGhostCtr = self.deGhostValue
                return True
            #Ghost seen north of pacman
            if (cur[0], cur[1]+x) in ghosts:
                self.deGhostCtr = self.deGhostValue
                return True
            #Ghost seen east of pacman
            if (cur[0]+x, cur[1]) in ghosts:
                self.deGhostCtr = self.deGhostValue
                return True
        return False

    def runFromGhost(self, state):
        # Runs away from ghosts
        #
        # Returns any direction that moves pacman away from ghost
        # Removes option of going towards ghost
        # Makes random choice of remaining options

        self.update(state)

        # print "Running from ghosts"

        cur = api.whereAmI(state)
        ghosts = api.ghosts(state)
        legal = api.legalActions(state)
        legal.remove(Directions.STOP)

        for x in range(1,4):

            #Ghost seen south of pacman
            if (cur[0], cur[1]-x) in ghosts:
                if Directions.SOUTH in legal:
                    #Stop pacman from going south towards ghost
                    if len(legal) > 1: legal.remove(Directions.SOUTH)
                    #Let pacman go in any direction except south
                    self.last = random.choice(legal)
                    return self.last

            #Ghost seen west of pacman
            if (cur[0]-x, cur[1]) in ghosts:
                if Directions.WEST in legal:
                    #Stop pacman from going west towards ghost
                    if len(legal) > 1: legal.remove(Directions.WEST)
                    #Let pacman go in any direction except west
                    self.last = random.choice(legal)
                    return self.last

            #Ghost seen north of pacman
            if (cur[0], cur[1]+x) in ghosts:
                if Directions.NORTH in legal:
                    #Stop pacman going north towards ghost
                    if len(legal) > 1: legal.remove(Directions.NORTH)
                    #Let pacman go in any direction except south
                    self.last = random.choice(legal)
                    return self.last

            #Ghost seen east of pacman
            if (cur[0]+x, cur[1]) in ghosts:
                if Directions.EAST in legal:
                    #Stop pacman going east towards ghost
                    if len(legal) > 1: legal.remove(Directions.EAST)
                    #Let pacman go in any direction except east
                    self.last = random.choice(legal)
                    return self.last

        self.last = random.choice(legal)
        return self.last


    def deStuck(self, state):
        # Gets pacman unstuck
        #
        # Follows path in one direction,
        # while never backtracking

        self.update(state)

        # print "Getting unstuck"

        cur = api.whereAmI(state)
        legal = api.legalActions(state)
        legal.remove(Directions.STOP)
        if len(legal) > 1:
            #Remove option to backtrack
            if self.oppositeDirection(state, self.last) in legal:
                legal.remove(self.oppositeDirection(state, self.last))
        #Go straight if possible
        if self.last in legal:
            return self.last

        self.last = random.choice(legal)
        return self.last


    def deGhost(self, state):
        # Avoid ghosts
        #
        # When running from a ghost, if pacman turns a corner,
        # pacman can no longer see ghost, and thus may backtrack
        # towards the ghost, causing him to get caught.
        # Avoid this by going straight and never backtracking
        # for 2 steps. Allows pacman to turn corners without losing
        # track of ghost and backtracking towards it

        self.update(state)

        # print "Avoiding ghosts"

        cur = api.whereAmI(state)
        legal = api.legalActions(state)
        legal.remove(Directions.STOP)
        if len(legal) > 1:
            #Remove option to backtrack
            legal.remove(self.oppositeDirection(state, self.last))
        #Go straight if possible
        if self.last in legal:
            return self.last
        self.last = random.choice(legal)
        return self.last


    def closestFoodIs(self, state):
        # Finds coord of closest food
        #
        # Performs breadth first search taking into
        # consideration walls, finds coord of food
        # that is smallest number of steps away

        cur = api.whereAmI(state)
        queue = [cur]
        visitedd = [cur]

        while queue:
            if queue[0] in self.food:
                return queue[0]
            else:
                front = queue[0]
                queue.pop(0)
                for x in self.possibleMoves(state, front):
                    if x not in visitedd:
                        visitedd.append(x)
                        queue.append(x)


    def goTowardsClosestFood(self, state):
        # Returns direction that takes pacman towards
        # the location of the food that is closest
        #
        # If pacman might get stuck, then go to smallest food instead
        # If pacman cant go directly towards food, go perpendicular to food
        # If pacman can go directly towards food then do so
        # If pacman cant go directly towards food then go straight if possible
        # Otherwise go random direction, except backwards


        self.update(state)

        # print "Seeking closest food"

        cur = api.whereAmI(state)
        coord = self.closestFoodIs(state)
        legal = api.legalActions(state)

        #------------If pacman might get stuck----------------

        #If closest food is southwest; pacman may get stuck
        if coord[0] < cur[0] and coord[1] < cur[1]:
            #Go to smallest food to avoid getting stuck
            self.last = self.goTowardsSmallestFood(state)
            return self.last

        #If closest food is northwest; pacman may get stuck
        if coord[0] < cur[0] and coord[1] > cur[1]:
            #Go to smallest food to avoid getting stuck
            self.last = self.goTowardsSmallestFood(state)
            return self.last

        #If closest food is northeast; pacman may get stuck
        if coord[0] > cur[0] and coord[1] > cur[1]:
            #Go to smallest food to avoid getting stuck
            self.last = self.goTowardsSmallestFood(state)
            return self.last

        #If closest food is southeast; pacman may get stuck
        if coord[0] > cur[0] and coord[1] < cur[1]:
            #Go to smallest food to avoid getting stuck
            self.last = self.goTowardsSmallestFood(state)
            return self.last

        #----------------------------------------------------

        #If closest food is west
        if coord[0] < cur[0]:
            #If wall inbetween pacman and food
            if (cur[0]-1, cur[1]) in api.walls(state):
                #Go north
                if Directions.NORTH in legal:
                    self.last = Directions.NORTH
                    return self.last
                #If cant go north go south
                if Directions.SOUTH in api.walls(state):
                    self.last = Directions.SOUTH
                    return self.last
            #Go west
            if Directions.WEST in legal:
                self.last = Directions.WEST
                return self.last
            #If cant go west, go straight
            elif self.last in legal:
                return self.last
            #If cant go straight go any possible direction except backwards
            else:
                legal.remove(Directions.STOP)
                if len(legal) > 1: legal.remove(self.oppositeDirection(state, self.last))
                self.last = random.choice(legal)
                return self.last

        #If closest food is east
        if coord[0] > cur[0]:
            #If wall inbetween pacman and food
            if (cur[0]+1, cur[1]) in api.walls(state):
                #Go north
                if Directions.NORTH in legal:
                    self.last = Directions.NORTH
                    return self.last
                #If cant go north go south
                if Directions.SOUTH in api.walls(state):
                    self.last = Directions.SOUTH
                    return self.last
            #Go east
            if Directions.EAST in legal:
                self.last = Directions.EAST
                return self.last
            #If cant go east, go straight
            elif self.last in legal:
                return self.last
            #If cant go straight go any possible direction except backwards
            else:
                legal.remove(Directions.STOP)
                if len(legal) > 1: legal.remove(self.oppositeDirection(state, self.last))
                self.last = random.choice(legal)
                return self.last

        #If closest food is south
        if coord[1] < cur[1]:
            #If wall inbetween pacman and food
            if (cur[0], cur[1]-1) in api.walls(state):
                #Go west
                if Directions.WEST in legal:
                    self.last = Directions.WEST
                    return self.last
                #If cant go west go east
                if Directions.EAST in api.walls(state):
                    self.last = Directions.EAST
                    return self.last
            #Go south
            if Directions.SOUTH in legal:
                self.last = Directions.SOUTH
                return self.last
            #If cant go south go straight
            elif self.last in legal:
                return self.last
            #If cant go straight go any possible direction except backwards
            else:
                legal.remove(Directions.STOP)
                if len(legal) > 1: legal.remove(self.oppositeDirection(state, self.last))
                self.last = random.choice(legal)
                return self.last

        #If closest food is north
        if coord[1] > cur[1]:
            #If wall inbetween pacman and food
            if (cur[0], cur[1]+1) in api.walls(state):
                #Go west
                if Directions.WEST in legal:
                    self.last = Directions.WEST
                    return self.last
                #If cant go west go east
                if Directions.EAST in api.walls(state):
                    self.last = Directions.EAST
                    return self.last
            #Go north
            if Directions.NORTH in legal:
                self.last = Directions.NORTH
                return self.last
            #If cant go north go straight
            elif self.last in legal:
                return self.last
            #If cant go straight go any possible direction except backwards
            else:
                legal.remove(Directions.STOP)
                if len(legal) > 1: legal.remove(self.oppositeDirection(state, self.last))
                self.last = random.choice(legal)
                return self.last

        legal.remove(Directions.STOP)
        if len(legal) > 1:
            legal.remove(self.oppositeDirection(state, self.last))
        self.last = random.choice(legal)
        return self.last

    def goTowardsSmallestFood(self, state):
        # Returns direction that leads pacman to
        # food with the lowest x then y coord
        #
        # If pacman cant go directly towards food, go perpendicular to food
        # If pacman can go directly towards food then do so
        # If pacman cant go directly towards food then go straight if possible
        # Otherwise go random direction, except backwards

        self.update(state)
        # print "Seeking smallest food"
        cur = api.whereAmI(state)
        coord = self.smallestFood(state)
        legal = api.legalActions(state)

        #If closest food west
        if coord[0] < cur[0]:
            #If wall inbetween pacman and food
            if (cur[0]-1, cur[1]) in api.walls(state):
                #Go north
                if Directions.NORTH in legal:
                    self.last = Directions.NORTH
                    return self.last
                #If cant go north go south
                if Directions.SOUTH in api.walls(state):
                    self.last = Directions.WEST
                    return self.last
            #Go west
            if Directions.WEST in legal:
                self.last = Directions.WEST
                return self.last
            #If cant go west go straight
            elif self.last in legal:
                return self.last
            #If cant go straight go any possible direction except backwards
            else:
                legal.remove(Directions.STOP)
                self.last = random.choice(legal)
                return self.last

        #If closest food east
        if coord[0] > cur[0]:
            #If wall inbetween pacman and food
            if (cur[0]+1, cur[1]) in api.walls(state):
                #Go north
                if Directions.NORTH in legal:
                    self.last = Directions.NORTH
                    return self.last
                #If cant go north go south
                if Directions.SOUTH in api.walls(state):
                    self.last = Directions.SOUTH
                    return self.last
            #Go east
            if Directions.EAST in legal:
                self.last = Directions.EAST
                return self.last
            #If cant go east go straight
            elif self.last in legal:
                return self.last
            #If cant go straight go any possible direction except backwards
            else:
                legal.remove(Directions.STOP)
                self.last = random.choice(legal)
                return self.last

        #If closest food north
        if coord[1] > cur[1]:
            #If wall inbetween pacman and food
            if (cur[0], cur[1]+1) in api.walls(state):
                #Go east
                if Directions.EAST in legal:
                    self.last = Directions.EAST
                    return self.last
                #If cant go east go west
                if Directions.WEST in api.walls(state):
                    self.last = Directions.WEST
                    return self.last
            #Go north
            if Directions.NORTH in legal:
                self.last = Directions.NORTH
                return self.last
            #If cant go north so straight
            elif self.last in legal:
                return self.last
            #If cant go straight go any possible direction except backwards
            else:
                legal.remove(Directions.STOP)
                self.last = random.choice(legal)
                return self.last

        #If closest food south
        if coord[1] < cur[1]:
            #If wall inbetween pacman and food
            if (cur[0], cur[1]-1) in api.walls(state):
                #Go east
                if Directions.EAST in legal:
                    self.last = Directions.EAST
                    return self.last
                #If cant so east go west
                if Directions.WEST in api.walls(state):
                    self.last = Directions.WEST
                    return self.last
            #Go south
            if Directions.SOUTH in legal:
                self.last = Directions.SOUTH
                return self.last
            #If cant go south go straight
            elif self.last in legal:
                return self.last
            #If cant go straight go any possible direction except backwards
            else:
                legal.remove(Directions.STOP)
                self.last = random.choice(legal)
                return self.last


    def leftCoordOf(self, state, coord, dir):
        # Returns the coordinate of the square that
        # is immediately left of the square passed

        if dir == Directions.NORTH:
            return (coord[0]-1, coord[1])
        if dir == Directions.SOUTH:
            return (coord[0]+1, coord[1])
        if dir == Directions.EAST:
            return (coord[0], coord[1]+1)
        if dir == Directions.WEST:
            return (coord[0], coord[1]-1)

    def leftDirOf(self, state, dir):
        # Returns the direction that is left
        # of the direction passed

        if dir == Directions.NORTH:
            return Directions.WEST
        if dir == Directions.SOUTH:
            return Directions.EAST
        if dir == Directions.EAST:
            return Directions.NORTH
        if dir == Directions.WEST:
            return Directions.SOUTH

    def followFood(self, state):
        # Goes to food that is next to pacman
        #
        # If multiple options, favour going left
        # to allow exterior traversal

        self.update(state)
        # print "Following adjacent food"
        cur = api.whereAmI(state)
        foodAndCapsules = api.union(api.food(state), api.capsules(state))

        #If left possible, always go left: allows exteriors traversal
        if self.leftCoordOf(state, cur, self.last) in foodAndCapsules:
            if self.leftDirOf(state, self.last) in api.legalActions(state):
                self.last = self.leftDirOf(state, self.last)
                return self.last

        for x in range(1,6):

            #If food immediately south of pacman
            if (cur[0], cur[1]-x) in foodAndCapsules:
                #Go south
                self.last = Directions.SOUTH
                return self.last
            #If food immediately west of pacman
            if (cur[0]-x, cur[1]) in foodAndCapsules:
                #Go west
                self.last = Directions.WEST
                return self.last
            #If food immediately north of pacman
            if (cur[0], cur[1]+x) in foodAndCapsules:
                #Go north
                self.last = Directions.NORTH
                return self.last
            #If food immediately east of pacman
            if (cur[0]+x, cur[1]) in foodAndCapsules:
                #Go east
                self.last = Directions.EAST
                return self.last

    def possibleMoves(self,state, pos):
        # Returns the list of possible moves from
        # the position passed, taking into account walls

        walls = api.walls(state)
        moves = []

        #South
        if (pos[0], pos[1]-1) not in walls:
            moves.append((pos[0], pos[1]-1))
        #West
        if (pos[0]-1, pos[1]) not in walls:
            moves.append((pos[0]-1, pos[1]))
        #North
        if (pos[0], pos[1]+1) not in walls:
            moves.append((pos[0], pos[1]+1))
        #East
        if (pos[0]+1, pos[1]) not in walls:
            moves.append((pos[0]+1, pos[1]))

        return moves

    def oppositeDirection(self, state, dir):
        # Returns the opposite direction of the one passed

        if dir == Directions.NORTH: return Directions.SOUTH
        if dir == Directions.SOUTH: return Directions.NORTH
        if dir == Directions.EAST: return Directions.WEST
        if dir == Directions.WEST: return Directions.EAST

    def randomlyTraverse(self, state):
        # Returns random direction
        # avoiding backtracking if possible

        self.update(state)
        # print "Randomly traversing"

        legal = api.legalActions(state)
        legal.remove(Directions.STOP)
        if len(legal) > 1:
            #Avoid backtracking
            if self.oppositeDirection(state, self.last) in legal:
                legal.remove(self.oppositeDirection(state, self.last))
        return random.choice(legal)
















    ###
