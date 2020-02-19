
"""
Created on Tue Feb 18 00:38:33 2020
@author: Pieter Cawood
@description:   Asyncronous-Backtracking-Algorithm for a distributed constraint satisfaction problem.
                This example is reffered to as the N-Queen problem and the solution is found recursively,
                which limits the size to 4x4 chess board.
                Future work is to implement threads to reduce recursion and improve agent initialization.
"""

import numpy as np

class Coordinate(object):
    #returns true if diagonal        
    def __init__(self, Row,Col):
        self.Row = Row
        self.Col = Col
    
    def GetCoordinates(self):
        return [self.Row,self.Col]
    
    def SetCoordinates(self,Row,Col):
        self.Row = Row
        self.Col = Col
              
class Nogood(object):
     def __init__(self, Agent, Assignments):
        self.Agent = Agent
        self.Assignments = Assignments
   
Environment = np.zeros((4,4)) 

def InitialiseEnvironment(Agents):
    for _agent in Agents:
        Environment.itemset((_agent.Assignments.Row,_agent.Assignments.Col),_agent.Priority)     
    print(Environment)
    
def UpdateEnvironment(Agent,Assignments):
    Pos = np.where(Environment == Agent.Priority)
    if ((Pos[0].size > 0) and (Pos[1].size > 0)):
        Environment.itemset((Pos[0][0],Pos[1][0]),0) 
    Environment.itemset((Assignments.Row,Assignments.Col),Agent.Priority)
    print(Environment)
    print()   
    
class Agent(object): 
    def __init__(self, Priority, Assignments, Domain, Constraints):
        self.Priority = Priority
        self.LocalDomain = Domain
        self.AgentView = {}
        self.Assignments = Assignments
        self.Constraints = Constraints
        self.NogoodList = []
        self.Terminate = False
        self.NeighbourAgents = []
     
    def AddNeighbourLink(self,Neighbour):
        self.NeighbourAgents.append(Neighbour)
    
    #Received OK from higher priority agent
    def RecOK(self,Neighbour,Assignments):
        self.AgentView[Neighbour] = Assignments
        if not self.Terminate:
            self.CheckAgentView()
    
    #Received Nogood from lower priority agent
    def RecNogood(self,Neighbour,Nogoods):
        if not self.Terminate:
            if not Neighbour in self.NeighbourAgents:
                self.AddNeighbourLink(Neighbour)
            self.NogoodList += Nogoods
            self.CheckAgentView()
        
    def RecNoSolution(self):
        self.Terminate = True
        
    def PubOK(self,All):
        UpdateEnvironment(self,self.Assignments)
        for _agent in self.NeighbourAgents:
            if (_agent.Priority > self.Priority) or All:
                _agent.RecOK(self, self.Assignments)
                   
    def PublishNogoods(self,NeighbourAgent,Nogoods):
        NeighbourAgent.RecNogood(self,Nogoods)
        
    def PublishNoSolution(self):
        for _neighbour in self.NeighbourAgents:
            _neighbour.RecNoSolution()
        self.Terminate = True
     
    #Check Assignments to constraints and Nogoods    
    def IsInconsistent(self, LocalAssignments, NeighbourAssignments):    
        _inconsistent = False
        for _consistent in self.Constraints:
           if not _consistent(LocalAssignments.Row,LocalAssignments.Col,NeighbourAssignments.Row,NeighbourAssignments.Col):
               _inconsistent =  True
        for _nogood in self.NogoodList:
            if ((_nogood.Agent == self) and ((_nogood.Assignments.Row == LocalAssignments.Row) and (_nogood.Assignments.Col == LocalAssignments.Col))):
                _inconsistent = True
        return _inconsistent

    #Check if local agent assignment is consistent with agent view
    #after a neighbour sent new assignment
    def CheckAgentView(self):
        _inconsistent = False
        for _agent in self.AgentView:
            if self.IsInconsistent(self.Assignments,self.AgentView.get(_agent)):
                _inconsistent = True
        #Agent asggignments inconsistent with one of the agents in view      
        if (_inconsistent):
            NewValue = False
            #Search local domain for new consistent value
            for _value in self.LocalDomain:
                if not _value == self.Assignments:
                    _allconsistent = True
                    for _agent in self.AgentView:
                        AgentView = self.AgentView.get(_agent) 
                        if self.IsInconsistent(_value,AgentView):
                            _allconsistent = False
                            break
                    if _allconsistent:
                        self.Assignments = _value
                        NewValue = True
                        break
            if NewValue:
                #Send assignments to all lower-priority agents 
                self.PubOK(True)
            else:
                #If no assignment consistent with agent view perform backtracking
                self.BackTrack()
        
        #First agent has no agentview, check if it's assignments are conistsent
        if((len(self.AgentView) == 0)):
            _assignment = False
            _continue = False
            for _nogood in self.NogoodList:
                if  ((_nogood.Agent == self) and ((_nogood.Assignments.Row == self.Assignments.Row) and (_nogood.Assignments.Col == self.Assignments.Col))):
                    _continue = True
            if _continue:
                for _value in self.LocalDomain:
                    for _nogood in self.NogoodList:
                        if not ((_nogood.Agent == self) and ((_nogood.Assignments.Row == _value.Row) and (_nogood.Assignments.Col == _value.Col))):
                            self.Assignments = _value 
                            _assignment = True
                            break
                    if _assignment:
                        break
            self.PubOK(True)                       
                         
    #Get Nogood assingments for lower prioneighbour agents based on this agent's agent view       
    def GetNogoods(self):
       # self.NogoodList.clear()
        Nogoods = []
        for _value in self.LocalDomain:
            #Create nogoods for local agent's assignment
            for _neighbour in self.AgentView:
                for _consistent in self.Constraints:
                    if not _consistent(_value.Row,_value.Col,_neighbour.Assignments.Row,_neighbour.Assignments.Col):
                        Nogoods.append(Nogood(_neighbour,_neighbour.Assignments))
        return Nogoods
                
    #If there is no value from local domain that this agent can take consistently
    #Then notify the agent with the lowest priority the Nogood set        
    def BackTrack(self):
        if not self.Terminate:
            Nogoods = self.GetNogoods()
            if len(Nogoods) == 0:
                self.PublishNoSolution()
            else: 
                LowPrioNeighbour = Nogoods[0].Agent
                for _nogood in Nogoods:
                    if (_nogood.Agent.Priority > LowPrioNeighbour.Priority):
                        LowPrioNeighbour = _nogood.Agent
                self.NogoodList = Nogoods
                self.PublishNogoods(LowPrioNeighbour,Nogoods)
                #lowPrioNeighbour will change his assignments, so remove from agent view
                if LowPrioNeighbour in self.AgentView:
                    del self.AgentView[LowPrioNeighbour]
                self.CheckAgentView()   

    
Constraints = []
#Add positioning constraints: vertical, horizontal and diagonal
Constraints.append(lambda RowI,ColI,RowJ,ColJ: ((ColI != ColJ) and (RowI != RowJ)))
Constraints.append(lambda RowI,ColI,RowJ,ColJ: ((RowI + ColJ) != (RowJ + ColI)) and ((RowI - ColJ) != (RowJ - ColI)))    

#Create agents. Future: Make a method(N) to create N numbers of agents & matrix
Agents = [Agent(1,Coordinate(0,0),[Coordinate(0,0),Coordinate(0,1),Coordinate(0,2),Coordinate(0,3)],Constraints),
          Agent(2,Coordinate(1,0),[Coordinate(1,0),Coordinate(1,1),Coordinate(1,2),Coordinate(1,3)],Constraints),
          Agent(3,Coordinate(2,0),[Coordinate(2,0),Coordinate(2,1),Coordinate(2,2),Coordinate(2,3)],Constraints),
          Agent(4,Coordinate(3,0),[Coordinate(3,0),Coordinate(3,1),Coordinate(3,2),Coordinate(3,3)],Constraints)]
          
InitialiseEnvironment(Agents)

#Subscribe neighbour agents
for _agent in Agents:
    for _neighbour in Agents:
        if _neighbour.Priority > _agent.Priority:
            _agent.AddNeighbourLink(_neighbour)      
            
#Publish assignments          
for _agent in Agents:
    _agent.PubOK(False)