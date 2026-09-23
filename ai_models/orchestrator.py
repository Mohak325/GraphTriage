from __future__ import annotations

import asyncio
import uuid
from typing import Any, Callable

from langgraph.graph import StateGraph, END

from ai_models.models import (
    TriageState,
    RCAOutput,
    IncidentData,
    AgentStatus,
)
from ai_models.llm.provider import LLMProvider, LLMProviderFactory
from ai_models.agents.navigator import NavigatorAgent
from ai_models.agents.diagnoser import DiagnoserAgent
from ai_models.agents.verifier import VerifierAgent


class GraphTriageOrchestrator:

    def __init__(
        self,
        llm: LLMProvider | None = None,
        max_iterations: int = 3,
        navigator_top_k: int = 5,
        status_callback: Callable | None = None,
    ):
        self.llm = llm or LLMProviderFactory.create()
        self.max_iterations = max_iterations
        self.status_callback = status_callback

        self.navigator = NavigatorAgent(
            llm=self.llm,
            top_k=navigator_top_k,
            status_callback=status_callback,
        )
        self.diagnoser = DiagnoserAgent(
            llm=self.llm,
            status_callback=status_callback,
        )
        self.verifier = VerifierAgent(
            llm=self.llm,
            status_callback=status_callback,
        )

        self.graph = self._build_graph()

    def _build_graph(self) -> StateGraph:
        workflow = StateGraph(TriageState)

        workflow.add_node("navigate", self._navigate_node)
        workflow.add_node("diagnose", self._diagnose_node)
        workflow.add_node("verify", self._verify_node)
        workflow.add_node("finalize", self._finalize_node)

        workflow.set_entry_point("navigate")

        workflow.add_edge("navigate", "diagnose")
        workflow.add_edge("diagnose", "verify")

        workflow.add_conditional_edges(
            "verify",
            self._should_continue,
            {
                "continue": "navigate",
                "finalize": "finalize",
            },
        )

        workflow.add_edge("finalize", END)

        return workflow.compile()

    async def _navigate_node(self, state: TriageState) -> TriageState:
        return await self.navigator.execute(state)

    async def _diagnose_node(self, state: TriageState) -> TriageState:
        return await self.diagnoser.execute(state)

    async def _verify_node(self, state: TriageState) -> TriageState:
        updated_state = await self.verifier.execute(state)
        updated_state["iteration"] = updated_state.get("iteration", 0) + 1
        return updated_state

    def _should_continue(self, state: TriageState) -> str:
        verification = state.get("verification_result")
        iteration = state.get("iteration", 0)
        max_iter = state.get("max_iterations", self.max_iterations)

        if verification and verification.get("verdict") == "ACCEPT":
            return "finalize"

        if iteration >= max_iter:
            return "finalize"

        return "continue"

    async def _finalize_node(self, state: TriageState) -> TriageState:
        verification = state.get("verification_result", {})
        diagnosis = state.get("diagnosis_result", {})
        incident = state.get("incident", {})

        verdict = verification.get("verdict", "REJECT")

        if verdict == "ACCEPT":
            status = "confirmed"
        elif diagnosis.get("root_cause_node"):
            status = "best_effort"
        else:
            status = "failed"

        final_output = RCAOutput(
            rca_id=str(uuid.uuid4()),
            incident_id=incident.get("incident_id", "unknown"),
            root_cause_node=diagnosis.get("root_cause_node", "unknown"),
            confidence=diagnosis.get("confidence", 0.0),
            evidence_chain=diagnosis.get("evidence_chain", []),
            counterfactual_results=[],
            remediation=diagnosis.get("remediation", []),
            iterations=state.get("iteration", 0),
            status=status,
        )

        if verification.get("counterfactual_results"):
            from ai_models.models import CounterfactualResult
            final_output.counterfactual_results = [
                CounterfactualResult(**cf)
                for cf in verification["counterfactual_results"]
            ]

        state["final_output"] = final_output.model_dump()
        state["status"] = status

        if self.status_callback:
            await self.status_callback({
                "agent": "orchestrator",
                "status": "completed",
                "detail": f"RCA completed with status: {status}",
            })

        return state

    async def run(
        self,
        incident: IncidentData,
        topology_nodes: list[dict],
        topology_edges: list[dict],
        metrics: list[dict] | None = None,
        traces: list[dict] | None = None,
        logs: list[str] | None = None,
    ) -> RCAOutput:
        initial_state: TriageState = {
            "incident": incident.model_dump(),
            "topology_nodes": topology_nodes,
            "topology_edges": topology_edges,
            "metrics": metrics or [],
            "traces": traces or [],
            "logs": logs or [],
            "navigator_result": None,
            "diagnosis_result": None,
            "verification_result": None,
            "rejection_feedback": "",
            "iteration": 0,
            "max_iterations": self.max_iterations,
            "status": "processing",
            "agent_updates": [],
            "final_output": None,
        }

        final_state = await self.graph.ainvoke(initial_state)

        if final_state.get("final_output"):
            return RCAOutput(**final_state["final_output"])

        return RCAOutput(
            rca_id=str(uuid.uuid4()),
            incident_id=incident.incident_id,
            root_cause_node="unknown",
            confidence=0.0,
            evidence_chain=[],
            counterfactual_results=[],
            remediation=[],
            iterations=final_state.get("iteration", 0),
            status="failed",
        )

    def run_sync(
        self,
        incident: IncidentData,
        topology_nodes: list[dict],
        topology_edges: list[dict],
        metrics: list[dict] | None = None,
        traces: list[dict] | None = None,
        logs: list[str] | None = None,
    ) -> RCAOutput:
        return asyncio.run(
            self.run(incident, topology_nodes, topology_edges, metrics, traces, logs)
        )
