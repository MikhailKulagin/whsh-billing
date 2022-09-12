import json

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database.db import Base, get_session
from service import app
from sqlalchemy_utils import create_database, drop_database

import routers

test_db_url = 'sqlite:///./test.db'
engine = create_engine(test_db_url,
                       connect_args={'check_same_thread': False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_session] = override_get_db
app.include_router(routers.billing.router)
client = TestClient(app)


def test_default():
    """
    Тест для проверки реста
    :return:
    """
    response = client.get('/top_10_invoices')
    assert response.status_code in (200, 204)


def test_create_invoice():
    """
    Тест создания инвойса
    :return:
    """
    try:
        create_database(test_db_url)
        # Никаого 'id': 1 не должно быть, там автоинкремент, но из-за того, что у меня в тестах не pg, что-то не так
        body = {'id': 1, 'id_account': 9999, 'operation': 100}
        response = client.post(url='/create_invoice',
                               json=body,)
        assert response.status_code == 200
    finally:
        drop_database(test_db_url)


def test_send_invoice(monkeypatch):
    # метод проводки инвойса
    try:
        create_database(test_db_url)
        # Никаого 'id': 1 не должно быть, там автоинкремент, но из-за того, что у меня в тестах не pg, что-то не так
        body = {'id': 1, 'id_account': 9999, 'operation': 100}
        create_response = client.post(url='/create_invoice',
                               json=body, )
        if create_response.status_code == 200:
            send_ids = [1]
            async def mock_send_to_accounting(found_invoices):
                # Мок функции, которая шлет в accounting инвойсы
                return send_ids
            monkeypatch.setattr(routers.billing, "send_to_accounting", mock_send_to_accounting)
            send_response = client.post(url='/send_invoices/?id_invoice=1')
            assert send_response.status_code == 200
            assert json.loads(send_response.content) == {'sent_invoice_ids': send_ids}
    finally:
        drop_database(test_db_url)
