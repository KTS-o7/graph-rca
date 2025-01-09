# this will generate a directed acyclic graph in json format
# input is a number of dictionaries, each dictionary is a node
# each dictionary has following params at least
# {
#     "id": "node1",
#     "time_stamp": "2021-01-01 00:00:00",
#     "log_level": "INFO",
#     "log_message": "This is an info message",
#     "log_source": "source1",
# }

# Think of adding some more params. Also be sure to add any changes made to keys in parser.py file as well.

class GraphGenerator:
    def add_node(self, node: dict) -> None:
        # this will add a node to the graph
        pass
    
    def add_edge(self, from_node: str, to_node: str) -> None:
        # this will add an edge between two nodes
        pass
    def generate_graph(self,) -> dict:
        # this will generate the graph in json format
        # Feel free to change the return type
        pass