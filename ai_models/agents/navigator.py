from __future__ import annotations
import json
from typing import Any, Callable
from ai_models.agents.base import BaseAgent
from ai_models.llm.provider import LLMProvider
from ai_models.llm.prompts import NAVIGATOR_SYSTEM_PROMPT, NAVIGATOR_USER_TEMPLATE
from ai_models.models import TriageState, AgentStatus, NavigatorResult

class NavigatorAgent(BaseAgent):
    def __init__(self, llm: LLMProvider, top_k: int = 5, status_callback: Callable | None = None) -> None:
        super().__init__("navigator", llm, status_callback)
        self.top_k = top_k

    async def execute(self, state: TriageState) -> TriageState:
        await self._emit_status(AgentStatus.RUNNING)
        try:
            topology_nodes = state.get("topology_nodes", [])
            topology_edges = state.get("topology_edges", [])
            
            fault_scores = {
                node.get("node_id", node.get("id", "")): node.get("anomaly_score", 0.0)
                for node in topology_nodes
            }

            rejection_feedback = state.get("rejection_feedback", "")

            user_prompt = NAVIGATOR_USER_TEMPLATE.format(
                topology_nodes=json.dumps(topology_nodes),
                topology_edges=json.dumps(topology_edges),
                fault_scores=json.dumps(fault_scores),
                rejection_feedback=rejection_feedback,
            )

            response = await self.llm.generate(NAVIGATOR_SYSTEM_PROMPT, user_prompt)

            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1] if "\n" in cleaned else cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
            parsed_data = json.loads(cleaned)

            suspicious_nodes = parsed_data.get("suspicious_nodes", [])[:self.top_k]
            suspicious_ids = set(suspicious_nodes)

            localized_nodes = [
                n for n in topology_nodes
                if n.get("node_id", n.get("id", "")) in suspicious_ids
            ]
            localized_edges = [
                e for e in topology_edges
                if e.get("source") in suspicious_ids or e.get("target") in suspicious_ids
            ]

            from ai_models.models import SubgraphData, NodeData, EdgeData
            subgraph = SubgraphData(
                nodes=[NodeData(**n) if isinstance(n, dict) else n for n in localized_nodes],
                edges=[EdgeData(**e) if isinstance(e, dict) else e for e in localized_edges],
                center_node=suspicious_nodes[0] if suspicious_nodes else "",
            )

            result = NavigatorResult(
                suspicious_nodes=suspicious_nodes,
                fault_scores=parsed_data.get("fault_scores", fault_scores),
                traversal_path=parsed_data.get("traversal_path", suspicious_nodes),
                localized_subgraph=subgraph,
                reasoning=parsed_data.get("reasoning", ""),
            )

            state["navigator_result"] = result.model_dump()

            if "agent_updates" not in state:
                state["agent_updates"] = []
            state["agent_updates"].append({"agent": self.name, "status": "COMPLETED"})

            await self._emit_status(AgentStatus.COMPLETED)
        except Exception as e:
            await self._emit_status(AgentStatus.FAILED, detail=str(e))
            from ai_models.models import SubgraphData
            state["navigator_result"] = NavigatorResult(
                suspicious_nodes=[],
                fault_scores={},
                traversal_path=[],
                localized_subgraph=SubgraphData(nodes=[], edges=[], center_node=""),
                reasoning=f"Failed to execute: {e}",
            ).model_dump()
            
        return state
