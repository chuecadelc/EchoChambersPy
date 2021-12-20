"""
Server element for the EC model.
"""

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import NetworkModule
from .model import EchoChambers, State, Type


def network_portrayal(G):
    # The model ensures there is always 1 agent per node
    """Network."""

    def node_color(agent):
        return {Type.REGULAR: "Purple", Type.LURKER: "Blue"}.get(
            agent.type, "Orange"
        )

    def edge_color(agent1, agent2):
        if State.SHARING in (agent1.state, agent2.state):
            return "#000000"
        return "#e8e8e8"

    def edge_width(agent1, agent2):
        if State.SHARING in (agent1.state, agent2.state):
            return 3
        return 2

    def get_agents(source, target):
        return G.nodes[source]["agent"][0], G.nodes[target]["agent"][0]

# you have to create a dictionary to give nodes and edges properties

    portrayal = dict()
    portrayal["nodes"] = [
        {
            "size": 6,
            "shape": "circle" if State.QUIET else "",
            "color": node_color(agents[0]),
            "tooltip": "id: {}<br>state: {}".format(
                agents[0].unique_id, agents[0].type.name
            ),
        }
        for (_, agents) in G.nodes.data("agent")
    ]

    portrayal["edges"] = [
        {
            "source": source,
            "target": target,
            "color": edge_color(*get_agents(source, target)),
            "width": edge_width(*get_agents(source, target)),
        }
        for (source, target) in G.edges
    ]

    return portrayal


network = NetworkModule(network_portrayal, 500, 500, library='d3')

chart1 = ChartModule([{"Label": "Sharing", "Color": "Green"},
                      {"Label": "Quiet", "Color": "Red"}])

model_params = dict(num_nodes=100, avg_node_degree=3)

server = ModularServer(EchoChambers, [network, chart1],
                       'Echo Chambers Basic Model', model_params)

#created for Chrome
server.port = 8521