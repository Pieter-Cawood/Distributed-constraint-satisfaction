"""
Created on Mon Feb 17 15:54:33 2020
@author: Nicolaas Pieter Cawood
@description:   Arc consistency/ Filtering algorithm that allows the reduction of agent domains
                for a CSP (Constrain Solution problem)
"""

class Agent(object): 

    def __init__(self,Id, LocalDomain):
        self.Id = Id
        self.LocalDomain = LocalDomain  
        self.NeighbourAgents = []
    
    def SubscribeNeighbour(self,NeighbourAgent):
        self.NeighbourAgents.append(NeighbourAgent)
        
    def RcvNewDomain(self,NeighbourAgent):
        self.Revise(NeighbourAgent)
        
#Publish domain to others        
    def PublishNewDomain(self,CallingNeighbour=None):
        for Neighbour in self.NeighbourAgents:
           if ((Neighbour == CallingNeighbour) or (CallingNeighbour == None)) : 
               Neighbour.RcvNewDomain(self)
               
#Arc consistency method
    def Revise(self,Neighbour):   
        LocalDomainChanged = False
        for value in self.LocalDomain:
            if value in Neighbour.LocalDomain:
                self.LocalDomain.remove(value)
                LocalDomainChanged = True
        if (LocalDomainChanged):     
            self.PublishNewDomain(Neighbour)

# The agents. In format Agent('Name',[d1,d2,d..])      
NeighbourAgents = [Agent('A',[1,2,3,4]),
                   Agent('B',[1,2,3,4]),
                   Agent('C',[1,2,3,5]),
                   Agent('D',[2,3,5,7])]

#Subscribe neighbour agents
for Agent in NeighbourAgents:
    for Neighbour in NeighbourAgents:
        if Neighbour != Agent:
            Agent.SubscribeNeighbour(Neighbour)
            
#Have all agents communicate their domain            
for Agent in NeighbourAgents:   
    Agent.PublishNewDomain()

for Agent in NeighbourAgents:
   print("Agent "+ str(Agent.Id) + " Domain : "+ str(Agent.LocalDomain))

