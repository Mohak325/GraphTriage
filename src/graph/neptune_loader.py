"""
Topology Graph Loader & Traversal Engine.
Grounding: Paper 2 (DTFL, Guo et al., IEEE TCC 2023) & Paper 7 (TN-AutoRCA, ICLR 2026).
Supports dual execution modes:
  1. Local In-Memory Graph (NetworkX) for fast offline testing and zero-cloud dependency.
  2. Amazon Neptune Property Graph (Gremlin) for live carrier deployment.
"""

from typing import List, Dict, Any, Optional
import networkx as nx
from structlog import get_logger

from src.contracts.schema import TopologySubgraph, GraphNode, GraphEdge

logger = get_logger()


class TopologyGraphEngine:
    """
    Manages multi-layer telecom cloud topologies:
    - Physical layer (BBU, RRU, Compute Servers, Edge Routers)
    - Virtualization layer (Kubernetes worker nodes, hypervisors)
    - Service layer (5GC NFs: AMF, SMF, UPF, NRF, and Service Function Chains)
    """

    def __init__(self, neptune_endpoint: Optional[str] = None):
        self.neptune_endpoint = neptune_endpoint
        # In-memory graph engine
        self.nx_graph = nx.DiGraph()
        self._gremlin_client = None

        if neptune_endpoint:
            self._init_neptune(neptune_endpoint)

    def _init_neptune(self, endpoint: str):
        """Initializes Gremlin client if live Neptune endpoint is provided."""
        try:
            from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
            from gremlin_python.structure.graph import Graph
            self._g = Graph().traversal().withRemote(DriverRemoteConnection(endpoint, 'g'))
            logger.info("Connected to live Amazon Neptune endpoint", endpoint=endpoint)
        except Exception as e:
            logger.warning("Neptune connection deferred or unavailable; falling back to NetworkX", error=str(e))
            self._g = None

    # ----------------------------------------------------
    # Vertex and Edge Operations (Dual-Mode)
    # ----------------------------------------------------

    def add_network_function(
        self,
        nf_id: str,
        nf_type: str,
        cluster_id: str = "cluster-01",
        status: str = "normal",
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Adds a Network Function vertex."""
        attrs = {
            "label": "NetworkFunction",
            "nf_type": nf_type,
            "cluster_id": cluster_id,
            "status": status,
            **(metadata or {})
        }
        self.nx_graph.add_node(nf_id, **attrs)

    def add_physical_node(
        self,
        node_id: str,
        site_id: str,
        rack: str,
        hw_type: str = "server"
    ):
        """Adds a Physical Node / Base Station vertex."""
        self.nx_graph.add_node(
            node_id,
            label="PhysicalNode",
            site_id=site_id,
            rack=rack,
            hw_type=hw_type,
            status="normal"
        )

    def add_service_chain(
        self,
        sfc_id: str,
        chain_type: str,
        tenant_id: str = "default-tenant"
    ):
        """Adds a Service Function Chain vertex."""
        self.nx_graph.add_node(
            sfc_id,
            label="ServiceChain",
            chain_type=chain_type,
            tenant_id=tenant_id
        )

    def add_call_dependency(
        self,
        source_id: str,
        target_id: str,
        latency_ms: float = 5.0,
        protocol: str = "HTTP2",
        sbi_operation: Optional[str] = None
    ):
        """Adds a directional CALLS invocation edge."""
        self.nx_graph.add_edge(
            source_id,
            target_id,
            label="CALLS",
            latency_ms=latency_ms,
            protocol=protocol,
            sbi_operation=sbi_operation
        )

    def add_hosting_edge(self, nf_id: str, node_id: str, allocation_ratio: float = 1.0):
        """Adds a HOSTED_ON edge from NF to physical or virtual node."""
        self.nx_graph.add_edge(
            nf_id,
            node_id,
            label="HOSTED_ON",
            allocation_ratio=allocation_ratio
        )

    def add_sfc_membership(self, sfc_id: str, nf_id: str, position: int):
        """Adds a PART_OF_SFC edge from ServiceChain to NetworkFunction."""
        self.nx_graph.add_edge(
            sfc_id,
            nf_id,
            label="PART_OF_SFC",
            position=position
        )

    # ----------------------------------------------------
    # Graph Traversal & Subgraph Extraction
    # ----------------------------------------------------

    def get_k_hop_neighbors(self, component_id: str, k: int = 2) -> List[str]:
        """Returns all upstream and downstream neighbors within k hops."""
        if component_id not in self.nx_graph:
            return []

        # Undirected view for multi-hop neighborhood discovery
        undirected = self.nx_graph.to_undirected(as_view=True)
        lengths = nx.single_source_shortest_path_length(undirected, component_id, cutoff=k)
        return list(lengths.keys())

    def extract_incident_subgraph(
        self,
        affected_components: List[str],
        hop_expansion: int = 1
    ) -> TopologySubgraph:
        """
        Extracts a typed TopologySubgraph around affected components,
        matching Contract 2 schema.
        """
        relevant_nodes = set()
        for comp in affected_components:
            neighbors = self.get_k_hop_neighbors(comp, k=hop_expansion)
            relevant_nodes.update(neighbors)

        sub_g = self.nx_graph.subgraph(relevant_nodes)

        nodes_list: List[GraphNode] = []
        for n, data in sub_g.nodes(data=True):
            status = "anomalous" if n in affected_components else data.get("status", "normal")
            nodes_list.append(
                GraphNode(
                    id=n,
                    status=status,
                    component_type=data.get("nf_type") or data.get("label")
                )
            )

        edges_list: List[GraphEdge] = []
        for u, v, data in sub_g.edges(data=True):
            edges_list.append(
                GraphEdge(
                    source=u,
                    target=v,
                    latency_ms=data.get("latency_ms", 10.0),
                    call_count=data.get("call_count", 1)
                )
            )

        return TopologySubgraph(nodes=nodes_list, edges=edges_list)

    def load_from_adjacency_dict(self, topology_spec: Dict[str, Any]):
        """Populates the topology from a structured JSON/dict spec."""
        for service in topology_spec.get("services", []):
            self.add_network_function(
                nf_id=service["name"],
                nf_type=service.get("type", "microservice"),
                cluster_id=topology_spec.get("cluster_id", "cluster-01"),
                status=service.get("status", "normal")
            )

        for dep in topology_spec.get("dependencies", []):
            self.add_call_dependency(
                source_id=dep["source"],
                target_id=dep["target"],
                latency_ms=dep.get("latency_ms", 5.0),
                protocol=dep.get("protocol", "HTTP2")
            )
