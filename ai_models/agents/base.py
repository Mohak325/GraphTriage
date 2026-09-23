from __future__ import annotations
import abc
import asyncio
from typing import Any, Callable
from ai_models.llm.provider import LLMProvider
from ai_models.models import TriageState, AgentStatus

class BaseAgent(abc.ABC):
    def __init__(self, name: str, llm: LLMProvider, status_callback: Callable | None = None) -> None:
        self.name = name
        self.llm = llm
        self.status_callback = status_callback

    async def _emit_status(self, status: AgentStatus, detail: str = "") -> None:
        if self.status_callback is not None:
            payload = {"agent": self.name, "status": status.value, "detail": detail}
            if asyncio.iscoroutinefunction(self.status_callback):
                await self.status_callback(payload)
            else:
                self.status_callback(payload)

    @abc.abstractmethod
    async def execute(self, state: TriageState) -> TriageState:
        pass
