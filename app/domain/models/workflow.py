from __future__ import annotations
from dataclasses import dataclass
from enum import IntEnum, StrEnum

class AppMode(StrEnum):
    AUTO = "auto"
    PROFESSIONAL = "professional"

class WorkflowStep(IntEnum):
    IMPORT = 0
    SEPARATE = 1
    LYRICS = 2
    REVIEW = 3
    STYLE = 4
    RENDER = 5
    EXPORT = 6

@dataclass(frozen=True, slots=True)
class WorkflowState:
    current: WorkflowStep = WorkflowStep.IMPORT
    completed: frozenset[WorkflowStep] = frozenset()
    running: bool = False
    operation: str = "Choose a song or video"
    progress: int = 0
    error: str | None = None

    def start(self, step: WorkflowStep, operation: str) -> "WorkflowState":
        return WorkflowState(step, self.completed, True, operation, 0, None)

    def update(self, progress: int, operation: str) -> "WorkflowState":
        return WorkflowState(self.current, self.completed, self.running, operation, max(0,min(100,progress)), self.error)

    def complete(self, step: WorkflowStep, next_step: WorkflowStep, operation: str) -> "WorkflowState":
        return WorkflowState(next_step, self.completed | {step}, False, operation, 100, None)

    def fail(self, message: str) -> "WorkflowState":
        return WorkflowState(self.current, self.completed, False, "Action required", self.progress, message)
