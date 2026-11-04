import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_db
from app.api.main import app
from app.db.session import Base
from app.db.models.attendance import Attendance  # noqa: F401 - register model metadata
from app.db.models.contact import Contact  # noqa: F401 - register model metadata
from app.db.models.employee import Employee  # noqa: F401 - register model metadata
from app.db.models.leave import Leave  # noqa: F401 - register model metadata


@pytest.fixture
def db_session():
    """为每个测试创建独立 SQLite 内存数据库，测试数据不会碰到真实 MySQL。"""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    test_session_factory = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = test_session_factory()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def client(db_session):
    """创建 FastAPI 测试客户端，并将数据库依赖替换成测试数据库。"""
    app.dependency_overrides[get_db] = lambda: db_session
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.pop(get_db, None)
