from pydantic import BaseModel, Field
from typing import Optional
from ..models.graph_data_models import DAGNode,DAG
from ..models.context_data_models import Context

class ContextBuilder:
    def __init__(self) -> None:
        self.dag = None
        self.root_cause = None
        self.causal_chain = []
    
    def build_context(self,dag:DAG) -> Context:
        if not dag:
            raise RuntimeError("DAG is required to build context")
        self.dag = dag
        
        try:
            self.root_cause = self.dag.root_cause
            self._find_causal_chain(self.dag.root_id)
            return Context(root_cause=self.root_cause,causal_chain=self.causal_chain)
        
        except Exception as e:
            raise RuntimeError(f"Failed to build context: {str(e)}")
        
    def _find_causal_chain(self,node_id:str) -> None:
        """Find the causal chain of the issue"""
        try:
            if not node_id:
                return
            
            node = next((node for node in self.dag.nodes if node.id == node_id),None)
            if not node:
                return
            
            # Add current node's message to the causal chain
            self.causal_chain.append(node.log_entry.message)
            
            # Iterate through the children of the node
            for child_id in node.children:
                child_node = next((child_node for child_node in self.dag.nodes if child_node.id == child_id),None)
                if child_node:
                    self._find_causal_chain(child_node.id)
            
        except Exception as e:
            raise RuntimeError(f"Failed to find causal chain: {str(e)}")
        
        