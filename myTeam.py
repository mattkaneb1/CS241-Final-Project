# myTeam.py
# ---------
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


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
from util import nearestPoint
import game

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """




  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########


class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """

  def registerInitialState(self, gameState):
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """
    actions = gameState.getLegalActions(self.index)

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())

    if foodLeft <= 2:
      bestDist = 9999
      for action in actions:
        successor = self.getSuccessor(gameState, action)
        pos2 = successor.getAgentPosition(self.index)
        dist = self.getMazeDistance(self.start, pos2)
        if dist < bestDist:
          bestAction = action
          bestDist = dist
      return bestAction

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights

  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}


class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """


  def getFeatures(self, gameState, action):
    """
    Features to implement:
    1. Number of dots currently carrying
    2. Closest Ghost
    3. Score
    4. Min Distance to Food
    5. Distance back to our side
    """

    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    foodList = self.getFood(successor).asList()
    ourState = gameState.getAgentState(self.index).isPacman
    features['successorScore'] = -len(foodList)#self.getScore(successor)

    #sets up the boundary so pacman knows to go back at a point
    boundary_line = []
    if gameState.isOnRedTeam(self.index):
      middle_line = (gameState.data.layout.width - 2) / 2 - 1
    else:
      middle_line = (gameState.data.layout.width - 2) / 2 + 1
    for i in range(1, gameState.data.layout.height - 1): #l.b. of 1 u.b. of height - 1 (just how layout works)
      if not gameState.hasWall(middle_line, i):
        boundary_line.append((middle_line, i))

    """
    First figure out where the other team is + decide if pacman/ghost
    """
    evil_pacman = [] #keeps track of the other pacman
    evil_ghost = [] #keeps track of the other ghost
    for opponent in self.getOpponents(gameState):
      agentState = gameState.getAgentState(opponent)
      opponent_type = agentState.isPacman
      if(opponent_type):
        evil_pacman.append(agentState)
      else:
        evil_ghost.append(agentState)



    print("Evil Pacman: ", evil_pacman)
    print("Evil Ghost: ", evil_ghost)
    #now features to work with these two
    current_position = successor.getAgentState(self.index).getPosition()
    last_pos = gameState.getAgentState(self.index).getPosition()
    features["no_move"] = 0
    if(current_position == last_pos):
      features["no_move"] = 1



    print(current_position)

    features["ghost_distance"] = 10 #just assume kinda far away all the time

    #get closest ghost
    for ghost in evil_ghost:
      if ghost.getPosition() != None:
        distance = self.getMazeDistance(current_position, ghost.getPosition())
        if(distance <= 5):
          features["ghost_distance"] = distance
        if(distance <= 2 and ghost.scaredTimer > 1):
          features["ghost_distance"] *= -1
          features["ghost_distance"] += 1/(1+distance)
        if ghost.scaredTimer > 0:
          features["ghost_distance"] = 10

    features["carrying_dots"] = successor.getAgentState(self.index).numCarrying
    features["to_boundary"] = 0

    min_distance_to_boundary = 1000000
    for boundary_point in boundary_line:
        temp = self.getMazeDistance(current_position, boundary_point)
        if(temp < min_distance_to_boundary):
          features["to_boundary"] = temp
          min_distance_to_boundary = temp

    if(features["ghost_distance"] != 10 and features["ghost_distance"] > 0):
      features["to_boundary"]*=100

    #if we're carrying dots get  back over to the line

    features["to_boundary"]*= features["carrying_dots"]/5


    print(features)

    if ghost.scaredTimer > 0:
      features["ghost_distance"] = 10

    myPos = successor.getAgentState(self.index).getPosition()


    features["num_food"] = len(foodList)

    # Compute distance to the nearest food
    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
      features['distanceToFood'] = minDistance

    if not ourState:
      friendPos = successor.getAgentState(self.index + 2).getPosition()
      maxDistance = util.manhattanDistance(myPos, friendPos)
      #maxDistance = self.getMazeDistance(myPos, friendPos)
      features["maxDistance"] = 1.0/(1+maxDistance)
      #features["distanceToFood"] *= 1000
    else:
      features["maxDistance"] = 0


    print(features)
    return features

  def getWeights(self, gameState, action):
    """
    Just need to assign weights to the features
    """
    return {'successorScore': 100, 'distanceToFood': -1, 'ghost_distance' : 10, 'carrying_dots' : -1, "to_boundary" : -5, "maxDistance": 0, "no_move": -10000000, "num_food": -100}



class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """

  def getFeatures(self, gameState, action):
    print("INFDKLADFJN;LSDKJF;LAKSJDF;LKASJDFL;KASDJF;LKSJF")
    print(self.index)
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)

    myState = successor.getAgentState(self.index)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    boundary_line = []
    if gameState.isOnRedTeam(self.index):
      middle_line = (gameState.data.layout.width - 2) / 2 - 2
    else:
      middle_line = (gameState.data.layout.width - 2) / 2 + 2
    for i in range(1, gameState.data.layout.height - 1):  # l.b. of 1 u.b. of height - 1 (just how layout works)
      if not gameState.hasWall(middle_line, i):
        boundary_line.append((middle_line, i))

    if(len(invaders) == 0):
      min_distance_to_boundary = 1000000
      for boundary_point in boundary_line:
        temp = self.getMazeDistance(myPos, boundary_point)
        if (temp < min_distance_to_boundary):
          features["invaderDistance"] = temp
          min_distance_to_boundary = temp

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    if gameState.isOnRedTeam(self.index):
      our_food = gameState.getRedFood().asList()
    else:
      our_food = gameState.getBlueFood().asList()

    print(our_food)

    summed = 0
    for food in our_food:
      summed += self.getMazeDistance(myPos, food)

    features["dist_food"] = summed

    if(features["invaderDistance"] < 5):
      features["dist_food"] = 0
    if(features["numInvaders"] > 0):
      features["dist_food"] = 0




    print("-------------------")
    print(features)
    print("-------------------")


    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -100000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2, "dist_food": -100}



class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """

    '''
    Make sure you do not delete the following line. If you would like to
    use Manhattan distances instead of maze distances in order to save
    on initialization time, please take a look at
    CaptureAgent.registerInitialState in captureAgents.py.
    '''
    CaptureAgent.registerInitialState(self, gameState)

    '''
    Your initialization code goes here, if you need any.
    '''


  def chooseAction(self, gameState):
    """
    Picks among actions randomly.
    """
    actions = gameState.getLegalActions(self.index)



    '''
    You should change this in your own agent.
    '''

    return random.choice(actions)

