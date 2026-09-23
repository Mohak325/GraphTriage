from __future__ import annotations
import json
from typing import Any, Callable
from ai_models.agents.base import BaseAgent
from ai_models.llm.provider import LLMProvider
from ai_models.llm.prompts import VERIFIER_SYSTEM_PROMPT, VERIFIER_USER_TEMPLATE
from ai_models.models import TriageState, AgentStatus, VerificationResult, CounterfactualResult

class VerifierAgent(BaseAgent):
    def __init__(self, llm: LLMProvider, status_callback: Callable | None = None) -> None:
        super().__init__("verifier", llm, status_callback)

    async def execute(self, state: TriageState) -> TriageState:
        await self._emit_status(AgentStatus.RUNNING)
        try:
            diagnosis_result = state.get("diagnosis_result", {})
            navigator_result = state.get("navigator_result", {})
            
            subgraph = navigator_result.get("localized_subgraph", {})
            subgraph_nodes = subgraph.get("nodes", [])
            subgraph_edges = subgraph.get("edges", [])
            
            metrics = state.get("metrics", [])
            traces = state.get("traces", [])
            logs = state.get("logs", [])
            
            user_prompt = VERIFIER_USER_TEMPLATE.format(
                diagnosis=json.dumps(diagnosis_result),
                subgraph_nodes=json.dumps(subgraph_nodes),
                subgraph_edges=json.dumps(subgraph_edges),
                metrics=json.dumps(metrics),
                traces=json.dumps(traces),
                logs=json.dumps(logs)
            )
            
            response = await self.llm.generate(VERIFIER_SYSTEM_PROMPT, user_prompt)

            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
            parsed_data = json.loads(cleaned)
            
            counterfactuals = [
                CounterfactualResult(**cf)
                for cf in parsed_data.get("counterfactual_results", [])
            ]
            
            result = VerificationResult(
                verdict=parsed_data.get("verdict", "REJECT"),
                confidence=parsed_data.get("confidence", 0.0),
                counterfactual_results=counterfactuals,
                rejection_reason=parsed_data.get("rejection_reason", ""),
                rejection_feedback=parsed_data.get("rejection_feedback", "")
            )
            
            state["verification_result"] = result.model_dump()
            
            if result.verdict == "REJECT":
                state["rejection_feedback"] = result.rejection_feedback
                
            if "agent_updates" not in state:
                state["agent_updates"] = []
            state["agent_updates"].append({"agent": self.name, "status": "COMPLETED"})
            
            await self._emit_status(AgentStatus.COMPLETED)
        except Exception as e:
            await self._emit_status(AgentStatus.FAILED, detail=str(e))
            state["verification_result"] = VerificationResult(
                verdict="REJECT",
                confidence=0.0,
                counterfactual_results=[],
                rejection_reason=str(e),
                rejection_feedback="Execution failed"
            ).model_dump()
            
        return state
