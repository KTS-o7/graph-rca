from pydantic import BaseModel, Field
from typing import Optional
from ..models.graph_data_models import DAGNode,DAG
from ..models.parsing_data_models import LogChain

class GraphGenerator:
    def __init__(self,log_chain:LogChain) -> None:
        self.log_chain = log_chain
        self.dag_nodes = []
        self.root_id = None
        self.leaf_ids = []
        
    def generate_dag(self) -> DAG:
        """Generate a Directed Acyclic Graph (DAG) from the log chain"""
        try:
            self.dag_nodes = []
            self.root_id = None
            self.leaf_ids = []
            self.root_cause = None
            
            for log_entry in self.log_chain.log_chain:
                node = DAGNode(id=str(log_entry.timestamp),parent_id=None,children=[],log_entry=log_entry)
                self.dag_nodes.append(node)
                
            self._set_parent_child_relationships()
            self._find_root_and_leaf_nodes()
            self.root_cause = self.find_root_cause()
            
            return DAG(nodes=self.dag_nodes,root_id=self.root_id,leaf_ids=self.leaf_ids,log_chain=self.log_chain,root_cause=self.root_cause)
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate DAG: {str(e)}")
        
    def _set_parent_child_relationships(self) -> None:
        """Set parent-child relationships between nodes"""
        try:
            for i in range(len(self.dag_nodes)):
                for j in range(i+1,len(self.dag_nodes)):
                    if self.dag_nodes[j].log_entry.timestamp > self.dag_nodes[i].log_entry.timestamp:
                        self.dag_nodes[i].children.append(self.dag_nodes[j].id)
                        self.dag_nodes[j].parent_id = self.dag_nodes[i].id
                        
        except Exception as e:
            raise RuntimeError(f"Failed to set parent-child relationships: {str(e)}")
        
    def _find_root_and_leaf_nodes(self) -> None:
        """Find the root and leaf nodes in the graph"""
        try:
            all_node_ids = set(node.id for node in self.dag_nodes)
            child_node_ids = set(child_id for node in self.dag_nodes for child_id in node.children)
            self.root_id = (all_node_ids - child_node_ids).pop()
            self.leaf_ids = list(all_node_ids - set(self.root_id))
            
        except Exception as e:
            raise RuntimeError(f"Failed to find root and leaf nodes: {str(e)}")

    def find_root_cause(self) -> str:
        """Find the root cause of the issue"""
        try:
            root_cause = self._find_root_cause_helper(self.root_id)
            return root_cause
            
        except Exception as e:
            raise RuntimeError(f"Failed to find root cause: {str(e)}")
        
    def _find_root_cause_helper(self, node_id: str) -> str:
        """Helper function to find the root cause recursively"""
        try:
            node = next(node for node in self.dag_nodes if node.id == node_id)
            if not node.parent_id:
                return node.log_entry.message
            return self._find_root_cause_helper(node.parent_id)
            
        except Exception as e:
            raise RuntimeError(f"Failed to find root cause helper: {str(e)}")
        
    