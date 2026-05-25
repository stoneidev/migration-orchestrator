import pytest
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from src.db import deps
from src.db.models import Base, SpecGenHistory


@pytest.fixture
def temp_factory():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)
    deps.set_session_factory(factory)
    yield factory
    deps.reset_session_factory()


def test_get_session_factory_returns_set_factory(temp_factory):
    assert deps.get_session_factory() is temp_factory


def test_get_session_factory_configures_default_when_unset():
    # Ensure no factory is set first.
    deps.reset_session_factory()
    factory = deps.get_session_factory()
    assert factory is not None
    deps.reset_session_factory()


def test_spec_gen_history_round_trip_via_helper(temp_factory):
    """C1 regression: the import-time capture bug used to silently drop writes."""
    factory = deps.get_session_factory()
    with factory() as db:
        db.add(SpecGenHistory(
            session_id="sg-test",
            page_id="shop.products",
            url="http://example.com/shop",
            php_path="shop/products.php",
            status="complete",
            operations_count=3,
            business_rules_count=10,
            test_scenarios_count=15,
            cost=0.05,
        ))
        db.commit()

    with factory() as db:
        rows = db.query(SpecGenHistory).filter_by(session_id="sg-test").all()
        assert len(rows) == 1
        assert rows[0].operations_count == 3
        assert rows[0].cost == 0.05
