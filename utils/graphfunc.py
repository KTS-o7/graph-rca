from pydantic import BaseModel, Field
from ..models.graphmodels import GraphNode


class TraceGraph(BaseModel):
    """
    This class defines the structure of the DAG.
    
    Attributes:
    graph: dict[str, GraphNode] - Dictionary of all nodes in the graph
    nodes: dict[str, GraphNode] - Dictionary of all nodes in the graph
    edges: dict[tuple[str, str], bool] - Dictionary of all edges in the graph
    root: str | None - Root node of the graph
    leaf: str | None - Leaf node of the graph
    size: int - Number of nodes in the graph
    
    Methods:
    add_node(node: GraphNode) -> None - Adds a node to the graph
    add_edge(src: str, dst: str) -> None - Adds an edge to the graph
    _will_create_cycle(src: str, dst: str) -> bool - Checks if adding an edge will create a cycle
    has_cycle() -> bool - Checks if the graph has any cycles
    topological_sort() -> list[str] - Returns nodes in topological order
    get_all_paths(src: str, dst: str) -> list[list[str]] - Gets all paths between nodes
    get_node(node_id: str) -> GraphNode - Returns a node from the graph
    get_nodes() -> dict[str, GraphNode] - Returns all nodes in the graph
    get_edges() -> dict[tuple[str, str], bool] - Returns all edges in the graph
    find_root() -> str | None - Finds the root node of the graph
    get_root() -> str | None - Returns the root node of the graph
    generate_dag(logs: list[GraphNode]) -> None - Generates a DAG from a list of logs
    
    """
    def __init__(self) -> None:
        self.graph: dict[str, GraphNode] = {}
        self.nodes: dict[str, GraphNode] = {}
        self.edges: dict[tuple[str, str], bool] = {}
        self.root: str | None = None
        self.leaf: str | None = None
        self.size: int = 0
        
    def __init__(self, logs: list[GraphNode]) -> None:
        self.graph: dict[str, GraphNode] = {}
        self.nodes: dict[str, GraphNode] = {}
        self.edges: dict[tuple[str, str], bool] = {}
        self.root: str | None = None
        self.leaf: str | None = None
        self.size: int = 0
        self.generate_dag(logs)
        
    def add_node(self, node: GraphNode) -> None:
        self.graph[node.id] = node
        self.nodes[node.id] = node
        self.size += 1
        
    def add_edge(self, src: str, dst: str) -> None:
        if src in self.graph and dst in self.graph and not self._will_create_cycle(src, dst):
            self.edges[(src,dst)] = True
            self.graph[dst].parents.append(src)
            
    def _will_create_cycle(self, src: str, dst: str) -> bool:
        if dst == src:
            return True
        visited = set()
        def dfs(node: str) -> bool:
            visited.add(node)
            for edge in self.edges:
                if edge[0] == node and edge[1] == src:
                    return True
                if edge[0] == node and edge[1] not in visited:
                    if dfs(edge[1]):
                        return True
            return False
        return dfs(dst)
    
    def has_cycle(self) -> bool:
        visited = set()
        rec_stack = set()
        
        def dfs_cycle(node: str) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            for edge in self.edges:
                if edge[0] == node:
                    neighbor = edge[1]
                    if neighbor not in visited:
                        if dfs_cycle(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
            
            rec_stack.remove(node)
            return False
        
        for node in self.graph:
            if node not in visited:
                if dfs_cycle(node):
                    return True
        return False
    
    def topological_sort(self) -> list[str]:
        visited = set()
        stack = []
        
        def dfs(node: str):
            visited.add(node)
            for edge in self.edges:
                if edge[0] == node and edge[1] not in visited:
                    dfs(edge[1])
            stack.insert(0, node)
            
        for node in self.graph:
            if node not in visited:
                dfs(node)
        return stack

    # Rest of the methods remain the same
    def get_node(self, node_id: str) -> GraphNode:
        return self.graph[node_id]
    
    def get_nodes(self) -> dict[str, GraphNode]:
        return self.nodes
    
    def get_edges(self) -> dict[tuple[str, str], bool]:
        return self.edges
    
    def find_root(self) -> str | None:
        for node in self.graph:
            if len(self.graph[node].parents) == 0:
                self.root = node
                break
        return self.root
    
    def get_root(self) -> str | None:
        if self.root is not None:
            return self.root
        self.root = self.find_root()
        return self.root
    
    def generate_dag(self, logs: list[GraphNode]) -> None:
        for log in logs:
            self.add_node(log)
        for log in logs:
            for parent in log.parents:
                self.add_edge(parent, log.id)
        self.find_root()
        

    
# add more functions as needed here