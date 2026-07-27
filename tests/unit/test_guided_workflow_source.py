from app.domain.models.workflow import WorkflowStep, WorkflowState


def test_studio_has_current_seven_step_guided_workflow():
    assert [step.name for step in WorkflowStep] == [
        "IMPORT", "SEPARATE", "LYRICS", "REVIEW", "STYLE", "RENDER", "EXPORT"
    ]
    state = WorkflowState().complete(WorkflowStep.IMPORT, WorkflowStep.SEPARATE, "Ready")
    assert WorkflowStep.IMPORT in state.completed
    assert state.current == WorkflowStep.SEPARATE
