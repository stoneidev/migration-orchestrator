import pytest

from src.pipeline.state_machine import StepState, transition, InvalidTransitionError


def test_queued_to_running():
    assert transition(StepState.QUEUED, StepState.RUNNING) == StepState.RUNNING


def test_running_to_passed():
    assert transition(StepState.RUNNING, StepState.PASSED) == StepState.PASSED


def test_running_to_retrying():
    assert transition(StepState.RUNNING, StepState.RETRYING) == StepState.RETRYING


def test_running_to_review():
    assert transition(StepState.RUNNING, StepState.REVIEW) == StepState.REVIEW


def test_retrying_to_passed():
    assert transition(StepState.RETRYING, StepState.PASSED) == StepState.PASSED


def test_retrying_to_blocked():
    assert transition(StepState.RETRYING, StepState.BLOCKED) == StepState.BLOCKED


def test_review_to_approved():
    assert transition(StepState.REVIEW, StepState.APPROVED) == StepState.APPROVED


def test_review_to_refined():
    assert transition(StepState.REVIEW, StepState.REFINED) == StepState.REFINED


def test_review_to_skipped():
    assert transition(StepState.REVIEW, StepState.SKIPPED) == StepState.SKIPPED


def test_invalid_transition_raises():
    with pytest.raises(InvalidTransitionError):
        transition(StepState.QUEUED, StepState.PASSED)


def test_invalid_transition_blocked_to_running():
    with pytest.raises(InvalidTransitionError):
        transition(StepState.BLOCKED, StepState.RUNNING)


def test_passed_is_terminal():
    with pytest.raises(InvalidTransitionError):
        transition(StepState.PASSED, StepState.RUNNING)
