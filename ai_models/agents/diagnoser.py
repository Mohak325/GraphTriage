from __future__ import annotations
import json
from typing import Any, Callable
from ai_models.agents.base import BaseAgent
from ai_models.llm.provider import LLMProvider
from ai_models.llm.prompts import DIAGNOSER_SYSTEM_PROMPT, DIAGNOSER_USER_TEMPLATE
from ai_models.models import TriageState, AgentStatus, DiagnosisResult

class DiagnoserAgent(BaseAgent):
    def __init__(self, llm: LLMProvider, status_callback: Callable | None = None) -> None:
        super().__init__("diagnoser", llm, status_callback)

    async def execute(self, state: TriageState) -> TriageState:
        await self._emit_status(AgentStatus.RUNNING)
        try:
            navigator_result = state.get("navigator_result", {})
            subgraph = navigator_result.get("localized_subgraph", {})
            subgraph_nodes = subgraph.get("nodes", [])
            subgraph_edges = subgraph.get("edges", [])
            
            metrics = state.get("metrics", [])[-100:]
            traces = state.get("traces", [])[-50:]
            logs = state.get("logs", [])[-100:]
            
            user_prompt = DIAGNOSER_USER_TEMPLATE.format(
                subgraph_nodes=json.dumps(subgraph_nodes),
                subgraph_edges=json.dumps(subgraph_edges),
                metrics=json.dumps(metrics),
                traces=json.dumps(traces),
                logs=json.dumps(logs),
            )

            response = await self.llm.generate(DIAGNOSER_SYSTEM_PROMPT, user_prompt)

            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
            parsed_data = json.loads(cleaned)

            result = DiagnosisResult(**parsed_data)

            state["diagnosis_result"] = result.model_dump()

            if "agent_updates" not in state:
                state["agent_updates"] = []
            state["agent_updates"].append({"agent": self.name, "status": "COMPLETED"})

            await self._emit_status(AgentStatus.COMPLETED)
        except Exception as e:
            await self._emit_status(AgentStatus.FAILED, detail=str(e))
            state["diagnosis_result"] = DiagnosisResult(
                root_cause_node="unknown",
                confidence=0.0,
                evidence_chain=[],
                remediation=[],
                reasoning=f"Failed to execute: {e}",
            ).model_dump()
            
        return state
