"""Fixture-backed implementations of external client interfaces.

Enables full offline execution, unit/contract testing, local dashboard demos,
and carrier benchmark evaluations without requiring Person A/B active infrastructure.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from contracts.pydantic.contract_1_telemetry import (
    NormalizedTelemetryEvent,
    SourceDomain,
    EventType,
    Severity,
    EventMetadata,
)
from contracts.pydantic.contract_2_rca_analysis import RCARequest, RCAResponse
from .client_interfaces import (
    MCPTelemetryClientInterface,
    MCPToolDefinition,
    RCAClientInterface,
    VectorStoreRAGClientInterface,
    RAGDocumentCitation,
)

FIXTURES_DIR = Path(__file__).resolve().parent.parent.parent / "tests" / "fixtures"


class FixtureMCPTelemetryClient(MCPTelemetryClientInterface):
    """Fixture-backed MCP client providing discovered tools and reading static Contract 1 telemetry."""

    def __init__(self, fixtures_path: Optional[Path] = None):
        self.fixtures_path = fixtures_path or (FIXTURES_DIR / "sample_contract_1_events.json")
        self._events: List[Dict[str, Any]] = []
        if self.fixtures_path.exists():
            with open(self.fixtures_path, "r") as f:
                self._events = json.load(f)

    async def list_tools(self) -> List[MCPToolDefinition]:
        """Dynamically list tools exposed by Person A's MCP server."""
        return [
            MCPToolDefinition(
                name="query_prometheus",
                description="Query live Prometheus metrics for 5GC NFs, Pods, or Transport nodes.",
                input_schema={
                    "type": "object",
                    "required": ["component_id", "metric_name"],
                    "properties": {
                        "component_id": {"type": "string", "description": "e.g. amf-01, smf-02"},
                        "metric_name": {"type": "string", "description": "e.g. amf_active_ngap_contexts"},
                    },
                },
            ),
            MCPToolDefinition(
                name="query_nwdaf",
                description="Query 3GPP Network Data Analytics Function (NWDAF) network performance analytics.",
                input_schema={
                    "type": "object",
                    "required": ["analytics_id", "target_nf"],
                    "properties": {
                        "analytics_id": {"type": "string", "description": "e.g. NF_LOAD, SERVICE_EXPERIENCE"},
                        "target_nf": {"type": "string", "description": "e.g. amf-01"},
                    },
                },
            ),
            MCPToolDefinition(
                name="inspect_k8s_pod",
                description="Query Kubernetes API for CNF pod lifecycle status, restarts, and resource usage.",
                input_schema={
                    "type": "object",
                    "required": ["pod_name"],
                    "properties": {
                        "pod_name": {"type": "string", "description": "e.g. pod-db-redis, amf-01-c89b"},
                    },
                },
            ),
            MCPToolDefinition(
                name="get_pcap_frames",
                description="Retrieve parsed 5GC SBI signaling frames for a specific procedure or trace ID.",
                input_schema={
                    "type": "object",
                    "required": ["procedure"],
                    "properties": {
                        "procedure": {"type": "string", "description": "e.g. Registration, PDU_Session_Establishment"},
                    },
                },
            ),
        ]

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute tool call against static telemetry fixtures."""
        if tool_name == "query_prometheus":
            comp = arguments.get("component_id", "")
            metric = arguments.get("metric_name", "")
            for ev in self._events:
                if ev.get("source_component") == comp and ev.get("metric_name") == metric:
                    return {
                        "status": "success",
                        "component": comp,
                        "metric": metric,
                        "value_raw": ev.get("metric_value_raw"),
                        "value_somp_delta": ev.get("metric_value_somp_delta"),
                        "timestamp": ev.get("timestamp"),
                    }
            # Fallback realistic metric response
            return {
                "status": "success",
                "component": comp,
                "metric": metric,
                "value_raw": 89.5,
                "value_somp_delta": 14.2,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }

        elif tool_name == "query_nwdaf":
            return {
                "status": "success",
                "analytics_id": arguments.get("analytics_id"),
                "target_nf": arguments.get("target_nf"),
                "load_level": "CRITICAL_CONGESTION",
                "confidence": 0.94,
            }

        elif tool_name == "inspect_k8s_pod":
            pod = arguments.get("pod_name", "")
            return {
                "status": "success",
                "pod_name": pod,
                "phase": "Running" if "redis" not in pod else "CrashLoopBackOff",
                "restart_count": 0 if "redis" not in pod else 8,
                "memory_usage_mb": 4096 if "redis" not in pod else 8192,
            }

        elif tool_name == "get_pcap_frames":
            return {
                "status": "success",
                "procedure": arguments.get("procedure"),
                "violating_frames": [
                    {"frame": 23, "type": "RegistrationReject", "cause": "5GS_Congestion"}
                ],
            }

        raise ValueError(f"Unknown MCP tool: {tool_name}")

    async def query_live_metric(self, component: str, metric_name: str) -> Optional[NormalizedTelemetryEvent]:
        """Query live metric to satisfy AGORA state-before-act verification."""
        for ev in self._events:
            if ev.get("source_component") == component and ev.get("metric_name") == metric_name:
                return NormalizedTelemetryEvent(**ev)

        # Return synthesized live event with current timestamp for AGORA verification
        return NormalizedTelemetryEvent(
            timestamp=datetime.now(timezone.utc),
            source_domain=SourceDomain.FIVE_G_CORE_SBA if "amf" in component or "smf" in component else SourceDomain.KUBERNETES_CNF,
            source_component=component,
            event_type=EventType.METRIC,
            severity=Severity.CRITICAL,
            metric_name=metric_name,
            metric_value_raw=92.4,
            metric_value_somp_delta=12.8,
            counter_reset_flag=False,
            log_message=None,
            trace_id="live-agora-trace-01",
            pcap_metadata=None,
            metadata=EventMetadata(
                tenant_id="tenant-carrier-noc",
                cluster_id="cluster-eu-west-1",
                kpi_filter_passed=True,
            ),
        )


class FixtureRCAClient(RCAClientInterface):
    """Fixture-backed implementation of Contract 2 RCA Analysis API."""

    def __init__(self, fixtures_dir: Optional[Path] = None):
        self.fixtures_dir = fixtures_dir or FIXTURES_DIR
        self._cache: Dict[str, RCAResponse] = {}
        self._load_fixtures()

    def _load_fixtures(self):
        # Index all scenario JSONs in fixtures
        for file in self.fixtures_dir.glob("*.json"):
            if file.name.startswith("contract_2_") or file.name.startswith("scenario_"):
                try:
                    with open(file, "r") as f:
                        data = json.load(f)
                        if "incident_id" in data and "ranked_causes" in data:
                            resp = RCAResponse(**data)
                            self._cache[resp.incident_id] = resp
                except Exception:
                    pass

    async def analyze_incident(self, request: RCARequest) -> RCAResponse:
        if request.incident_id in self._cache:
            return self._cache[request.incident_id]

        # Default fallback to INC-2026-0042 reference scenario
        ref_file = self.fixtures_dir / "contract_2_inc_2026_0042.json"
        with open(ref_file, "r") as f:
            data = json.load(f)
            data["incident_id"] = request.incident_id
            return RCAResponse(**data)


class FixtureVectorStoreRAGClient(VectorStoreRAGClientInterface):
    """Fixture-backed RAG client over ETSI NFV-MANO guidelines and SOPs."""

    def __init__(self):
        self._corpus: List[Dict[str, Any]] = [
            {
                "doc_id": "ETSI-NFV-IFA-005-SOP-42",
                "title": "AMF SBI Client Pool Saturation Recovery Workflow",
                "section": "Clause 7.4.2: Overload Control and Queue Remediation",
                "standard": "ETSI GS NFV-IFA 005 v4.3.1",
                "content": "When AMF Service-Based Interface (SBI) encounters thread pool or client pool exhaustion triggering RegistrationReject (Frame 23 congestion), the NFVO/VNFM shall invoke horizontal scale-out of the AMF microservice instances (minimum +2 replicas) and dynamically reconfigure SBI client_pool_size to 2048 to prevent HTTP/2 queue starvation across the AMF-SMF link.",
                "keywords": ["amf", "sbi", "client_pool_size", "registration", "horizontal_scale", "thread pool"],
            },
            {
                "doc_id": "ETSI-NFV-IFA-007-SOP-19",
                "title": "Transport BGP Route Flap & Optical Degradation Remediation",
                "section": "Clause 6.2.1: Optical Carrier Protection Switching",
                "standard": "ETSI GS NFV-IFA 007 v3.1.1",
                "content": "Upon detecting persistent Forward Error Correction (FEC) uncorrectable frame errors exceeding link thresholds on core optical router interfaces, initiate protection switching to secondary redundant DWDM lambda and dampen BGP advertisement flaps via route-dampening policy.",
                "keywords": ["router", "bgp", "optical", "transport", "flapping", "fec"],
            },
            {
                "doc_id": "ETSI-NFV-SOL-003-SOP-88",
                "title": "Cloud-Native CNF Pod OOMKilled Emergency Evacuation",
                "section": "Clause 8.3: Memory Pressure and Cgroup Quarantine",
                "standard": "ETSI GS NFV-SOL 003 v4.2.1",
                "content": "When stateful caching CNF pods (e.g. Redis subscriber session cache) experience repeated OOMKilled restarts due to cgroup limits, patch memory request/limit to 8Gi and trigger graceful state sync before restarting terminating container.",
                "keywords": ["oomkilled", "memory", "redis", "cgroup", "crashloop"],
            },
            {
                "doc_id": "3GPP-TS-29.518-SOP-03",
                "title": "3GPP 5G Core AMF Service-Based Interface Specification",
                "section": "Clause 5.2.2: Namf_Communication Service Overload Handling",
                "standard": "3GPP TS 29.518 v18.2.0",
                "content": "AMF SBI client pool size must be tuned proportionally to the peak concurrent NGAP signaling contexts. If HTTP/2 stream multiplexing exceeds queue capacity, 5GS_Congestion cause code is returned in RegistrationReject.",
                "keywords": ["3gpp", "amf", "ngap", "registrationreject", "congestion", "namf"],
            },
        ]

    async def search_sop(self, query: str, top_k: int = 3) -> List[RAGDocumentCitation]:
        query_lower = query.lower()
        scored: List[tuple[float, Dict[str, Any]]] = []

        for doc in self._corpus:
            score = 0.1
            for kw in doc["keywords"]:
                if kw in query_lower:
                    score += 0.25
            scored.append((score, doc))

        scored.sort(key=lambda x: x[0], reverse=True)
        results: List[RAGDocumentCitation] = []
        for score, doc in scored[:top_k]:
            results.append(
                RAGDocumentCitation(
                    doc_id=doc["doc_id"],
                    title=doc["title"],
                    section=doc["section"],
                    standard=doc["standard"],
                    content=doc["content"],
                    score=round(min(score, 0.99), 3),
                )
            )
        return results
