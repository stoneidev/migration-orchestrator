from enum import StrEnum


class StepState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    RETRYING = "retrying"
    BLOCKED = "blocked"
    REVIEW = "review"
    APPROVED = "approved"
    REFINED = "refined"
    SKIPPED = "skipped"


class PageState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    REVIEW = "review"
    BLOCKED = "blocked"
    COMPLETE = "complete"
    FAILED = "failed"


class InvalidTransitionError(Exception):
    pass


VALID_STEP_TRANSITIONS: dict[StepState, set[StepState]] = {
    StepState.QUEUED: {StepState.RUNNING},
    StepState.RUNNING: {StepState.PASSED, StepState.RETRYING, StepState.REVIEW},
    StepState.RETRYING: {StepState.PASSED, StepState.BLOCKED, StepState.RETRYING},
    StepState.REVIEW: {StepState.APPROVED, StepState.REFINED, StepState.SKIPPED},
    StepState.APPROVED: set(),
    StepState.REFINED: set(),
    StepState.SKIPPED: set(),
    StepState.PASSED: set(),
    StepState.BLOCKED: set(),
}

VALID_PAGE_TRANSITIONS: dict[PageState, set[PageState]] = {
    PageState.QUEUED: {PageState.RUNNING, PageState.BLOCKED},
    PageState.RUNNING: {PageState.COMPLETE, PageState.BLOCKED, PageState.REVIEW, PageState.FAILED},
    PageState.REVIEW: {PageState.RUNNING},
    PageState.BLOCKED: {PageState.RUNNING},
    PageState.COMPLETE: set(),
    PageState.FAILED: {PageState.RUNNING},
}


def transition(current: StepState, target: StepState) -> StepState:
    allowed = VALID_STEP_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidTransitionError(f"Cannot transition from {current} to {target}")
    return target


def transition_page(current: PageState, target: PageState) -> PageState:
    allowed = VALID_PAGE_TRANSITIONS.get(current, set())
    if target not in allowed:
        raise InvalidTransitionError(f"Page cannot transition from {current} to {target}")
    return target
