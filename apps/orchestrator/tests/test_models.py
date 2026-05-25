from datetime import datetime

from src.db.models import (
    Artifact,
    CostLog,
    Page,
    PipelineTask,
    Review,
    SpecGenSession,
    StepExecution,
)


def test_create_page(db_session):
    page = Page(
        id="bbs.alert_close",
        module="bbs",
        title="관리자 경고/확인 팝업 후 창 닫기",
        spec_status="complete",
        spec_score=0.950,
        complexity="low",
    )
    db_session.add(page)
    db_session.commit()

    loaded = db_session.get(Page,"bbs.alert_close")
    assert loaded is not None
    assert loaded.module == "bbs"
    assert loaded.title == "관리자 경고/확인 팝업 후 창 닫기"
    assert loaded.spec_score == 0.950
    assert loaded.complexity == "low"
    assert loaded.migration_status == "queued"
    assert loaded.current_step == 0


def test_page_default_values(db_session):
    page = Page(id="test.page", module="test")
    db_session.add(page)
    db_session.commit()

    loaded = db_session.get(Page,"test.page")
    assert loaded.migration_status == "queued"
    assert loaded.current_step == 0
    assert loaded.total_cost == 0.0
    assert loaded.total_input_tokens == 0
    assert loaded.total_output_tokens == 0


def test_step_execution_linked_to_page(db_session):
    page = Page(id="bbs.alert_close", module="bbs")
    db_session.add(page)
    db_session.flush()

    step = StepExecution(
        page_id="bbs.alert_close",
        step_number=1,
        step_name="spec_load",
        status="running",
        attempt_number=1,
        model_used="haiku",
    )
    db_session.add(step)
    db_session.commit()

    loaded = db_session.get(Page, "bbs.alert_close")
    assert len(loaded.step_executions) == 1
    assert loaded.step_executions[0].step_name == "spec_load"
    assert loaded.step_executions[0].status == "running"


def test_artifact_linked_to_page(db_session):
    page = Page(id="bbs.alert_close", module="bbs")
    db_session.add(page)
    db_session.flush()

    artifact = Artifact(
        page_id="bbs.alert_close",
        step_number=3,
        artifact_type="api_contract",
        file_path="apps/backend/openapi/bbs_alert_close.yaml",
        version=1,
        content_hash="abc123",
    )
    db_session.add(artifact)
    db_session.commit()

    loaded = db_session.get(Page, "bbs.alert_close")
    assert len(loaded.artifacts) == 1
    assert loaded.artifacts[0].artifact_type == "api_contract"


def test_cost_log(db_session):
    page = Page(id="bbs.alert_close", module="bbs")
    db_session.add(page)
    db_session.flush()

    cost = CostLog(
        page_id="bbs.alert_close",
        step_number=3,
        model="claude-sonnet-4-6",
        input_tokens=5000,
        output_tokens=1500,
        cache_read_tokens=3000,
        cost=0.035,
    )
    db_session.add(cost)
    db_session.commit()

    logs = db_session.query(CostLog).filter_by(page_id="bbs.alert_close").all()
    assert len(logs) == 1
    assert logs[0].model == "claude-sonnet-4-6"
    assert logs[0].cost == 0.035


def test_review(db_session):
    page = Page(id="bbs.alert_close", module="bbs")
    db_session.add(page)
    db_session.flush()

    review = Review(
        page_id="bbs.alert_close",
        step_number=4,
        status="pending",
        review_type="blocking",
        summary="React 컴포넌트 확인 필요",
    )
    db_session.add(review)
    db_session.commit()

    loaded = db_session.get(Page, "bbs.alert_close")
    assert len(loaded.reviews) == 1
    assert loaded.reviews[0].status == "pending"
    assert loaded.reviews[0].review_type == "blocking"


def test_pipeline_task_persistence(db_session):
    task = PipelineTask(
        id="run-abc123",
        task_type="pipeline_run",
        page_id="bbs.alert_close",
        status="queued",
    )
    db_session.add(task)
    db_session.commit()

    loaded = db_session.get(PipelineTask, "run-abc123")
    assert loaded is not None
    assert loaded.task_type == "pipeline_run"
    assert loaded.status == "queued"


def test_spec_gen_session_persistence(db_session):
    session = SpecGenSession(
        id="sg-abc123",
        url="https://example.com/shop/mp_question.php",
        php_path="shop/mp_question.php",
        page_id="shop.mp_question",
        status="ready",
        step=0,
    )
    db_session.add(session)
    db_session.commit()

    loaded = db_session.get(SpecGenSession, "sg-abc123")
    assert loaded is not None
    assert loaded.page_id == "shop.mp_question"
    assert loaded.status == "ready"
