"""Model of Echo Chambers."""

from mesa import Model, Agent
from mesa.time import RandomActivation
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
from enum import Enum
import networkx as nx
import numpy as np
import random


class Type(Enum):
    """To identify the different agents."""

    REGULAR = 1
    LURKER = 2
    OVAUSER = 3

class State(Enum):
    """Agent state."""
    
    QUIET = 1
    SHARING = 2


def number_state(model, state):
    """Count all agents."""
    return sum([1 for a in model.grid.get_all_cell_contents() if a.state is state])


def number_shares(model):
    """Count all agents."""
    return number_state(model, State.SHARING)
    

def number_quiet(model):
    """Count all agents."""
    return number_state(model, State.QUIET)


class EchoChambers(Model):
    """
    Parameters for the model.
        num_nodes: number of agents in the model
        avg_node_degree: how many frens it should have
        schedule = agent activation schedule
        G = type of network
        grid= grid display of the network
        layout= type of layout for the network
    """
    
    def __init__(self, num_nodes, avg_node_degree):
    
        self.num_nodes = num_nodes
        self.counter = 0
        # self.state= initial_state
        # self.ova_chance= ova_chance
        # self.engagement = 0
        self.G = nx.barabasi_albert_graph(self.num_nodes, avg_node_degree)
        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)
        self.layout = nx.spring_layout(self.G)
        nx.draw(self.G, pos=nx.spring_layout(self.G))
        
        self.datacollector = DataCollector({
            # "Regulars": compute_regulars,
            # "Lurkers": compute_lurkers,
            # "Resistant": compute_ovauser,
            "Sharing": number_shares,
            "Quiet": number_quiet
            })
        
        for i, node in enumerate(self.G.nodes()):
            a = Citizens(
            i,
            self,
            Type.REGULAR,
            State.QUIET
            )
            
        self.schedule.add(a)
        # Add the agent to the node
        self.grid.place_agent(a, node)
        
        lurker_nodes = self.random.sample(self.G.nodes(), 50)
        for a in self.grid.get_cell_list_contents(lurker_nodes):
        
            a.type = Type.LURKER
            
        ova_nodes = self.random.sample(self.G.nodes(), 5)
        for a in self.grid.get_cell_list_contents(ova_nodes):
            
            a.type = Type.OVAUSER
            
        self.running = True
        self.datacollector.collect(self)
        
        # generating the info, once per simulation
        # info should have political id [0], credibility[1] and emotion [2]
        self.information = []
        
        
        for each in range(0, 100):
            self.information.append([None, None, None])
        
        for each in range(0, 100):
        
            self.information[each][0] = np.random.uniform(-1, 1)
            self.information[each][1] = np.random.uniform(0, 1)
            self.information[each][2] = random.randint(0, 1)
        
        # giving nodes the info_received
        information = []
        nx.set_node_attributes(self.G, information, "info_received")
        
        # Agents can be normal, influential or news orgs. Diff. influence
        self.influence = random.randint(0, 1)
        nx.set_node_attributes(self.G, self.influence, "Influence_type")
        
    def step(self):
        """Step."""
        self.information_difuss()
        self.schedule.step()
        # collect data
        self.datacollector.collect(self)
        
        # self.agents()   
    def run_model(self, n):
        """Run."""
        for i in range(n):
            self.step()
            
    # Random selection of info and agent to send it to so the difussion begins 
    def information_difuss(self):
        """Info."""
        info = self.random.sample(self.information, 1)
        chosen_one = random.choice(list(self.G.nodes()))
        
        self.G.nodes[chosen_one]["info_received"] = info
        self.G.nodes[chosen_one]["Influence_type"] = self.influence
        return self.G.nodes(data=True)
        # it's working so no need to verify
        print(self.G.nodes[chosen_one]['Influence_type'],
        self.G.nodes[52]['Influence_type'])
        
        # chosen_one.info_received.append(info)
        # print(info, "appended")
        
    
class Citizens(Agent):
    """Citizen."""
    
    def __init__(self, unique_id, model, init_type, initial_state):
    
        super().__init__(unique_id, model)
        
        self.type = init_type
        self.engagement = 0
        self.social_influence = 0
        self.opinion_changes = 0
        self.threshold = 0.5
        self.emotion = random.randint(0, 1)
        self.certainty = np.random.uniform(0, 1)
        self.susceptibility = np.random.uniform(0, 1)
        self.political_ID = np.random.uniform(-1, 1)
        self.state = initial_state
    
    
    
    def step(self):
        """
        Agent receives & appends info.
        
        depending on origin,
        diff. processess follow
        """
        self.attribute_distrib()
        self.update_condition()
        self.homophily_check()
        self.op_change()
  
    
    def attribute_distrib(self):
        """Agent attributes."""
        for u, v in self.model.G.edges():
            # add random weights between 0 and 10
            self.model.G[u][v]["political_ID"] = np.random.uniform(-1, 1)
            self.model.G[u][v]["tolerance"] = np.random.uniform(0, 1)
            self.model.G[u][v]["emotion"] = random.randint(0, 1)
            self.model.G[u][v]["certainty"] = np.random.uniform(0, 1)
            self.model.G[u][v]["ideology"] = "Left"
            self.model.G[u][v]["info_received"] = {}
            
            # if self.model.G[u][v]["political_ID"] > 0:
            # self.model.G[u][v]["ideology"] == "Right"
            
            return self.model.G.edges(data=True)
        # print ("I made it")
        
    def update_condition(self):
        """
        Change the condition of an agent.
        
        depending on their engagement level.
        This will influence their sharing probs.
        """
        if self.type is Type.REGULAR:
        
            self.engagement = np.random.uniform(0.4, 0.6)
            
            # print(self.engagement)
        
        elif self.type is Type.LURKER:
        
            self.engagement = np.random.uniform(0, 0.4)
        
            # print("I'm a lurker")
        
        else:
        
            self.engagement = np.random.uniform(0.7, 1)
            self.state = State.SHARING
            self.social_influence += 1
            
            # print("something not working")
            # print(self.state)
     
    def homophily_check(self):
        """Homphily."""
        # Finding the agent's ties
        name = self.unique_id
        ties = self.model.G.edges(name, data=True)
        
        count = 0
        
        for u in list(ties):
        
            # ties = list(u)
            
            simil = abs(u[2]['political_ID'] - self.political_ID)
            
            # print(simil)
            
        if simil <= 1:
        
            count += 1
            
            ties_list = list(ties)
            
            print(len(ties_list))
        
        if count >= len(ties_list)//2:
        
            print("homophily")
            homphily = True
            # self.state =  State.SHARING
        
        else:
            print("no homophily")
            homphily = False
            self.state = State.QUIET
     
    def op_change(self):
        """
        Determine agent's op_change rate.
        
        and will affect homophily_check
        
        Agents will change their op based on ALL info received
        """
        
        name = self.unique_id
        
        # print(list(self.model.G.nodes(data=True)))
        
        self.info_received = list(self.model.G.nodes[name]['info_received'])
        self.influence_ag = self.model.G.nodes[name]['Influence_type']
        
        # print(self.info_received)
        
        if len(self.info_received) == 0:
        
            print("No info yet")
        
        else:
        
            print("Habemus info")
            
            # I need to take an average of all the infos, so they evaluate
            ideological_Sim = []
            Source = []
        
        for each in range(len(self.info_received)):
        
            ideological_sim = [abs(self.info_received[each][0]
                              - self.political_ID)]
            
            ideological_Sim.append(ideological_sim)
            
            source = [abs(self.susceptibility - self.info_received[each][1])]
            
            Source.append(source)
            
            # Calculate the formula using the average ideology and source cred
            # print(ideological_Sim)
            avg_ideology = sum(ideological_sim)/len(ideological_sim)
            
            # print(round(avg_ideology, 2))
            
            avg_source = sum(source)/len(source)
            # print(round(avg_source, 2))
        
        if self.influence_ag == 1:
        
            if (abs(avg_ideology - self.political_ID) <= 0.8 and self.emotion == 0
            and self.certainty <=0.5):
            
                self.opinion_changes += 1
                self.political_ID = abs(self.political_ID + 0.1)
                print("changed my mind")
                
            elif  ((abs(avg_ideology - self.political_ID) >= 0.8 and
                abs(avg_ideology - self.political_ID) >= 1)
                and self.emotion == 1 and self.certainty <=0.5 ):
                
                self.opinion_changes += 1
                self.political_ID = abs(self.political_ID + 0.1)
                print("changed my mind")
            
            else:
            
                print("not changing my mind!")
        
        else:
        
            if (abs(avg_ideology - self.political_ID) <= 0.8 and self.emotion == 0
            and self.certainty <=0.5 and abs(avg_source - self.susceptibility) <= 0.5):
            
                self.opinion_changes += 1
                self.political_ID = abs(self.political_ID + 0.1)
                print("changed my mind")
            
            elif  ((abs(avg_ideology - self.political_ID) >= 0.8 and
                abs(avg_ideology - self.political_ID) >= 1)
                and self.emotion == 1 and self.certainty <=0.5
                and abs(avg_source - self.susceptibility) <= 0.5):
            
                self.opinion_changes += 1
                self.political_ID = abs(self.political_ID + 0.1)
                print("changed my mind")
            
            else:
            
                print("not changing my mind!")
        
        
# Deciding to share or not the info.
    def sharing_time(self):
        """
        Share.
        Agents will share info individually, with a max given by ther engag.
        """
        
        if State.SHARING:
        
            name = self.unique_id
            ties = self.model.G.edges(name, data=True)
            
            count = 0
        
        for u in list(ties):
        
            u[2]['info_received'] = self.info_received
            print(u[2]['info_received'])
            # ,list(u))
            count += 1
