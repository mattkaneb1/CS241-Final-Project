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
               first = 'OffensiveMinimaxAgent', second = 'DefensiveMinimaxAgent'):




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




class ExpectimaxAgent(CaptureAgent):

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
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.depth = 2

  def evaluationFunction(self, currentGameState, ID):
    if currentGameState.getAgentState(ID).isPacman:
      return self.evaluateOffense(currentGameState,ID)
    else:
      return self.evaluateDefense(currentGameState,ID)

  def isTerminal(self, agent, state, depth):
    if agent == self.index:
      return (state.data._win or state.data._lose) or self.depth == depth
    else:
      return state.data._win or state.data._lose

  def pacMove(self, state, depth):
    opps = CaptureAgent.getOpponents(self, state)
    if self.isTerminal(self.index, state, depth + 1):
        return self.evaluationFunction(state,self.index)
    currMax = float('-inf')
    for action in state.getLegalActions(self.index):
        successorState = state.generateSuccessor(self.index, action)
        currMax = max(currMax, self.ghostMove(opps[0], successorState, depth + 1))  # first ghost has next move
    return currMax

  def ghostMove(self, ghostNum, state, depth):
    if self.isTerminal(ghostNum, state, depth):
        return self.evaluationFunction(state,ghostNum)
    expected = 0
    opps = CaptureAgent.getOpponents(self, state)

    # If ghost isnt visible, skip it
    if state.getAgentState(ghostNum).configuration == None:
      if ghostNum == opps[0]:  # if not last ghost, the next ghost moves next
          expected = self.ghostMove(opps[1], state, depth)
      else:  # if last ghost, pacman has next move
          expected = self.pacMove(state, depth)

    else:
      numActions = len(state.getLegalActions(ghostNum))
      for action in state.getLegalActions(ghostNum):
          successorState = state.generateSuccessor(ghostNum, action)
          
          # ASSUMES THEY CHOOSE RANDOMLY WHICH COULD BE IMPROVED

          if ghostNum == opps[0]:  # if not last ghost, the next ghost moves next
              expected += (1.0 / numActions) * self.ghostMove(opps[1], successorState, depth)
          else:  # if last ghost, pacman has next move
              expected += (1.0 / numActions) * self.pacMove(successorState, depth)
    return expected

  def chooseExpectiMaxAction(self, gameState):
    """
      Returns the expectimax action using self.depth and self.evaluationFunction

      All ghosts should be modeled as choosing uniformly at random from their
      legal moves.
    """
    maximum = float('-inf')
    bestAction = None
    opps = CaptureAgent.getOpponents(self, gameState)
    for action in gameState.getLegalActions(self.index):
        successorState = gameState.generateSuccessor(self.index, action)
        expectedVal = self.ghostMove(opps[0], successorState, 0)
        if expectedVal > maximum:
            maximum = expectedVal
            bestAction = action
    return bestAction

  def chooseAction(self, gameState):
    opps = CaptureAgent.getOpponents(self, gameState)
    return self.chooseExpectiMaxAction(gameState)

  def evaluateOffense(self, gameState, ID):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getOFeatures(gameState,ID)
    weights = self.getOWeights(gameState)
    return features * weights

  def evaluateDefense(self, gameState, ID):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getDFeatures(gameState,ID)
    weights = self.getDWeights(gameState)
    return features * weights

  def getOFeatures(self, gameState, ID):
    """
    Features to implement:
    1. Number of dots currently carrying
    2. Closest Ghost
    3. Score
    4. Min Distance to Food
    5. Distance back to our side
    """
    features = util.Counter()
    redTeam = gameState.isOnRedTeam(ID)
    opponent = ID in self.getOpponents(gameState)
    blueFood = gameState.getBlueFood().asList()
    redFood = gameState.getRedFood().asList()

    # Add Score to Features
    #================================================================================
    # if redTeam:
    #   features['score'] = len(redFood) - len(blueFood)
    # else:
    #   features['score'] = len(blueFood) - len(redFood)

    # Re-Visit using actual score here @@@@@
    #================================================================================


    # Discourage Standing Still
    #================================================================================
    c_pos = gameState.getAgentState(ID).getPosition()
    if self.getPreviousObservation() == None:
      features["no_move"] = 0
    else:
      l_pos = self.getPreviousObservation().getAgentState(ID).getPosition()

      if l_pos == None:
        features["no_move"] = 0
      elif c_pos == l_pos:
        features["no_move"] = 1
      else:
        features["no_move"] = 0
    #================================================================================


    # Add Number of Dots being Carried to Features
    #================================================================================
    features["dots"] = gameState.getAgentState(ID).numCarrying
    #================================================================================


    # Distance from Boundary Line
    #================================================================================
    if not gameState.getAgentState(ID).isPacman:
      features["to_boundary"] = 0
    else:
      b_line = []
      if redTeam:
        m_line = (gameState.data.layout.width - 2) / 2 - 1
      else:
        m_line = (gameState.data.layout.width - 2) / 2 + 1
      
      for i in range(1, gameState.data.layout.height - 1):
        if not gameState.hasWall(m_line, i):
          b_line.append((m_line, i))

      features["to_boundary"] = min([self.getMazeDistance(c_pos, b_pos) for b_pos in b_line])

      features["to_boundary"]*= features["dots"]/5
    #================================================================================


    # Distance from Closest Ghost
    #================================================================================
    closest_ghost = 6
    if opponent:
      for opp in self.getTeam(gameState):
        if not gameState.getAgentState(opp).isPacman:
          g_pos = gameState.getAgentState(opp).getPosition()
          closest_ghost = min(self.getMazeDistance(c_pos, g_pos),closest_ghost)

    else:
      for opp in self.getOpponents(gameState):
        g_pos = gameState.getAgentState(opp).getPosition()
        if g_pos != None:
          if not gameState.getAgentState(opp).isPacman:
            closest_ghost = min(self.getMazeDistance(c_pos, g_pos),closest_ghost)

    features["close_ghost"] = closest_ghost
    #================================================================================


    # Number of Food Left
    #================================================================================
    features["num_food"] = len(redFood) if redTeam else len(blueFood)
    #================================================================================
    

    # Closest & Furthest Food
    #================================================================================
    if closest_ghost < 3:
      features["close_food"] = 20
    else:
      if redTeam:
        features["close_food"] = min([self.getMazeDistance(c_pos, f_pos) for f_pos in blueFood])
      else:
        features["close_food"] = min([self.getMazeDistance(c_pos, f_pos) for f_pos in redFood])
    #================================================================================


    # Closest Capsule
    #================================================================================
    caps = gameState.getCapsules()
    if len(caps) != 0:
      features["capsule"] = min([self.getMazeDistance(c_pos, cap_pos) for cap_pos in caps])
    else:
      features["capsule"] = -1
    #================================================================================

    return features

  def getOWeights(self, gameState):
    """
    Just need to assign weights to the features
    """
    # return {'score': 10, 'no_move' : -100000000,
    #         'dots' : 10, 'to_boundary' : -20,
    #         'close_ghost' : 10, 'num_food': -10,
    #         'close_food' : -50,'capsule':-25}

    return {'score': -100, 'no_move' : -10000000,
            'dots' : -1, 'to_boundary' : -5,
            'close_ghost' : 10, 'close_food' : -1}



  def getDFeatures(self, gameState,ID):
    features = util.Counter()

    myPos = gameState.getAgentState(ID).getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if gameState.getAgentState(ID).isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    boundary_line = []
    if gameState.isOnRedTeam(ID):
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

    if gameState.isOnRedTeam(ID):
      our_food = gameState.getRedFood().asList()
    else:
      our_food = gameState.getBlueFood().asList()

    summed = 0
    for food in our_food:
      summed += self.getMazeDistance(myPos, food)

    features["dist_food"] = summed / len(our_food)

    if(features["invaderDistance"] < 5):
      features["dist_food"] = 0
    if(features["numInvaders"] > 0):
      features["dist_food"] = 0

    return features

  def getDWeights(self, gameState):
    return {'numInvaders': -100000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2, "dist_food": -100}



class OffensiveExpectimaxAgent(ExpectimaxAgent):
  def evaluationFunction(self, currentGameState, i):
    if i == self.index:
      return self.evaluateOffense(currentGameState,i)
    elif currentGameState.getAgentState(i).isPacman:
      return self.evaluateOffense(currentGameState,i)
    else:
      return self.evaluateDefense(currentGameState,i)

class DefensiveExpectimaxAgent(ExpectimaxAgent):
  def evaluationFunction(self, currentGameState, i):
    if i == self.index:
      return self.evaluateDefense(currentGameState,i)
    elif currentGameState.getAgentState(i).isPacman:
      return self.evaluateOffense(currentGameState,i)
    else:
      return self.evaluateDefense(currentGameState,i)








class MinimaxAgent(CaptureAgent):

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
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.depth = 2

  def evaluationFunction(self, currentGameState, ID):
    if currentGameState.getAgentState(ID).isPacman:
      return self.evaluateOffense(currentGameState,ID)
    else:
      return self.evaluateDefense(currentGameState,ID)

  def isTerminal(self, agent, state, depth):
    if agent == self.index:
      return (state.data._win or state.data._lose) or self.depth == depth
    else:
      return state.data._win or state.data._lose

  def minValue(self,state,alpha,beta,agent,depth):
    if self.isTerminal(agent,state,depth):
      return self.evaluationFunction(state,agent)

    v = float('inf')

    opps = CaptureAgent.getOpponents(self, state)


    # If ghost isnt visible, skip it
    if state.getAgentState(agent).configuration == None:
      if agent == opps[0]:
          v = min(v,self.minValue(state,alpha,beta,opps[1],depth))
      else:  
          v = min(v,self.maxValue(state,alpha,beta,self.index,depth+1))
    else:
      for action in state.getLegalActions(agent):
        successorState = state.generateSuccessor(agent, action)

        if agent == opps[1]:
          v = min(v,self.maxValue(successorState,alpha,beta,self.index,depth+1))
        else:
          v = min(v,self.minValue(successorState,alpha,beta,opps[1],depth))

        if v < alpha:
          return v

        beta = min(beta,v)

    return v

  def maxValue(self,state,alpha,beta,agent,depth):

    if self.isTerminal(agent,state,depth):
      return self.evaluationFunction(state,agent)

    v = float('-inf')

    opps = CaptureAgent.getOpponents(self, state)
    for action in state.getLegalActions(agent):
      successorState = state.generateSuccessor(agent, action)

      v = max(v,self.minValue(successorState,alpha,beta,opps[0],depth))

      if v > beta:
        return v

      alpha = max(alpha,v)

    return v

  def chooseMiniMaxAction(self, gameState):
    """
      Returns the expectimax action using self.depth and self.evaluationFunction

      All ghosts should be modeled as choosing uniformly at random from their
      legal moves.
    """
    maximum = float('-inf')
    alpha = float('-inf')
    beta = float('inf')
    bestAction = None
    opps = CaptureAgent.getOpponents(self, gameState)
    for action in gameState.getLegalActions(self.index):
        successorState = gameState.generateSuccessor(self.index, action)
        currVal = self.minValue(successorState,alpha,beta,opps[0],0)
        if currVal > maximum:
            maximum = currVal
            bestAction = action
        if currVal > alpha:
            alpha = currVal #update alpha at the root
    return bestAction

  def chooseAction(self, gameState):
    return self.chooseMiniMaxAction(gameState)

  def evaluateOffense(self, gameState, ID):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getOFeatures(gameState,ID)
    weights = self.getOWeights(gameState)
    return features * weights

  def evaluateDefense(self, gameState, ID):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getDFeatures(gameState,ID)
    weights = self.getDWeights(gameState)
    return features * weights

  def getOFeatures(self, gameState, ID):
    """
    Features to implement:
    1. Number of dots currently carrying
    2. Closest Ghost
    3. Score
    4. Min Distance to Food
    5. Distance back to our side
    """
    features = util.Counter()
    redTeam = gameState.isOnRedTeam(ID)
    opponent = ID in self.getOpponents(gameState)
    blueFood = gameState.getBlueFood().asList()
    redFood = gameState.getRedFood().asList()

    # Add Score to Features
    #================================================================================
    if redTeam:
      features['score'] = len(blueFood)
    else:
      features['score'] = len(redFood)
    #================================================================================


    # Discourage Standing Still
    #================================================================================
    c_pos = gameState.getAgentState(ID).getPosition()
    if self.getPreviousObservation() == None:
      features["no_move"] = 0
    else:
      l_pos = self.getPreviousObservation().getAgentState(ID).getPosition()

      if l_pos == None:
        features["no_move"] = 0
      elif c_pos == l_pos:
        features["no_move"] = 1
      else:
        features["no_move"] = 0
    #================================================================================


    # Add Number of Dots being Carried to Features
    #================================================================================
    features["dots"] = gameState.getAgentState(ID).numCarrying
    #================================================================================


    # Distance from Boundary Line
    #================================================================================
    if not gameState.getAgentState(ID).isPacman:
      features["to_boundary"] = 0
    else:
      b_line = []
      if redTeam:
        m_line = (gameState.data.layout.width - 2) / 2 - 1
      else:
        m_line = (gameState.data.layout.width - 2) / 2 + 1
      
      for i in range(1, gameState.data.layout.height - 1):
        if not gameState.hasWall(m_line, i):
          b_line.append((m_line, i))

      features["to_boundary"] = min([self.getMazeDistance(c_pos, b_pos) for b_pos in b_line])

      features["to_boundary"]*= features["dots"]
    #================================================================================


    # Distance from Closest Ghost
    #================================================================================
    closest_ghost = 6
    if opponent:
      for opp in self.getTeam(gameState):
        if not gameState.getAgentState(opp).isPacman:
          g_pos = gameState.getAgentState(opp).getPosition()
          closest_ghost = min(self.getMazeDistance(c_pos, g_pos),closest_ghost)

    else:
      for opp in self.getOpponents(gameState):
        g_pos = gameState.getAgentState(opp).getPosition()
        if g_pos != None:
          if not gameState.getAgentState(opp).isPacman:
            closest_ghost = min(self.getMazeDistance(c_pos, g_pos),closest_ghost)

    features["close_ghost"] = closest_ghost
    #================================================================================


    # Closest & Furthest Food
    #================================================================================
    #if closest_ghost < 3:
    #  features["close_food"] = 20
    #else:
    if redTeam:
      features["close_food"] = min([self.getMazeDistance(c_pos, f_pos) for f_pos in blueFood])
    else:
      features["close_food"] = min([self.getMazeDistance(c_pos, f_pos) for f_pos in redFood])
    #================================================================================


    # Closest Capsule
    #================================================================================
    # caps = gameState.getCapsules()
    # if len(caps) != 0:
    #   features["capsule"] = min([self.getMazeDistance(c_pos, cap_pos) for cap_pos in caps])
    # else:
    #   features["capsule"] = -1
    #================================================================================

    return features

  def getOWeights(self, gameState):
    """
    Just need to assign weights to the features
    """
    return {'score': -100, 'no_move' : -10000000,
            'dots' : -1, 'to_boundary' : -5,
            'close_ghost' : 10, 'close_food' : -1}
            # 'capsule':-1}

            # {'successorScore': 100, 
            # 'distanceToFood': -1, 
            # 'ghost_distance' : 10, 
            # 'carrying_dots' : -1, 
            # "to_boundary" : -5, 
            # "maxDistance": 0, 
            # "no_move": -10000000, 
            # "num_food": -100}



  def getDFeatures(self, gameState,ID):
    
    features = util.Counter()
    myPos = gameState.getAgentState(ID).getPosition()
    features = util.Counter()
    redTeam = gameState.isOnRedTeam(ID)
    opponent = ID in self.getOpponents(gameState)
    blueFood = gameState.getBlueFood().asList()
    redFood = gameState.getRedFood().asList()
    c_pos = gameState.getAgentState(ID).getPosition()

    # Determine if on Defense
    #================================================================================
    features['onDefense'] = 1
    if gameState.getAgentState(ID).isPacman: features['onDefense'] = 0
    #================================================================================


    # Computes distance to invaders we can see
    # Count Invaders
    #================================================================================
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    #================================================================================


    #================================================================================
    features['invaderDistance'] = 6
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)
    #================================================================================


    # Distance from Boundary Line
    #================================================================================
    b_line = []
    if redTeam:
      m_line = (gameState.data.layout.width - 2) / 2 - 1
    else:
      m_line = (gameState.data.layout.width - 2) / 2 + 1
    
    for i in range(1, gameState.data.layout.height - 1):
      if not gameState.hasWall(m_line, i):
        b_line.append((m_line, i))

    features["to_boundary"] = min([self.getMazeDistance(c_pos, b_pos) for b_pos in b_line])
    #================================================================================


    # Find Average Distance from Food
    #================================================================================
    if gameState.isOnRedTeam(ID):
      our_food = redFood
    else:
      our_food = blueFood

    summed = 0
    for food in our_food:
      summed += self.getMazeDistance(myPos, food)
    features["dist_food"] = summed / len(our_food)
    #================================================================================


    # Patrol Variable
    #================================================================================
    # y = util.sample([.125,.125,.125,.125,.125,.125,.125,.125,.125],[2,3,4,5,6,7,8,9,10])
    # features['patrol'] = abs(c_pos[1] - y)
    #================================================================================
  


    # # Don't patrol until near border
    # #================================================================================
    # if features["to_boundary"] > 4:
    #   features["patrol"] = 0
    #   features["dist_food"] = 0
    # #================================================================================

    # if features["to_boundary"] < 4:
    #   features["to_boundary"] = 0

    # Ignore guarding food when invaders
    #================================================================================
    if(features["invaderDistance"] < 5):
      features["dist_food"] = 0
      features["patrol"] = 0
    if(features["numInvaders"] > 0):
      features["dist_food"] = 0
      features["patrol"] = 0
    #================================================================================
    return features

  def getDWeights(self, gameState):
    return {'numInvaders': -1000, 'onDefense': 5, 
            'invaderDistance': -25, 'dist_food': -5,
            'to_boundary' : -20}
            # , 'patrol' : -2}


class OffensiveMinimaxAgent(MinimaxAgent):
  def evaluationFunction(self, currentGameState, i):
    if i == self.index:
      return self.evaluateOffense(currentGameState,i)
    elif currentGameState.getAgentState(i).isPacman:
      return self.evaluateOffense(currentGameState,i)
    else:
      return self.evaluateDefense(currentGameState,i)

class DefensiveMinimaxAgent(MinimaxAgent):
  def evaluationFunction(self, currentGameState, i):
    if i == self.index:
      return self.evaluateDefense(currentGameState,i)
    elif currentGameState.getAgentState(i).isPacman:
      return self.evaluateOffense(currentGameState,i)
    else:
      return self.evaluateDefense(currentGameState,i)




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
    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)
    self.depth = 1




