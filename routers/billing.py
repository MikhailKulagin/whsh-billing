import logging
from typing import List

import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime

from models import billing
from database.db import get_session
from database import db_models

from config import config

router = APIRouter()
log = logging.getLogger(__name__)


@router.get("/top_10_invoices",
            response_model=List[billing.Invoice])
async def show_random_invoices(db: Session = Depends(get_session)):
    """
    Бстрая проверка, что таблица создалась и в ней что-то есть
    :param db:
    :return:
    """
    random_invoices = db.query(db_models.Invoice).limit(10).all()
    if random_invoices:
        return random_invoices
    else:
        raise HTTPException(204, "No Content")


@router.post("/create_invoice",
             response_model=dict)
async def add_invoice(body: billing.Invoice, db: Session = Depends(get_session)):
    """
    Создать инвойс в БД.
    :param body:
    :param db:
    :return:
    """
    body.tstamp = datetime.utcnow()
    new_invoices = db_models.Invoice(**body.dict())
    db.add(new_invoices)
    db.flush()
    db.commit()
    db.refresh(new_invoices)
    if new_invoices.id:
        return {'inserted_id': new_invoices.id}
    else:
        raise HTTPException(500, "Invoice insert error")


@router.post("/send_invoices/",
             response_model=dict)
async def add_record(id_account: int = None,
                     id_invoice: int = None,
                     db: Session = Depends(get_session)):
    """
    Отправка инвойсов в Accounting.
    При вызове должен быть заполнен id_invoice или id_account, чтобы не отправить всю таблицу.
    Пока решил сделать так, если запрос вернет много инвойсов, то каждый отправляется отдельным post.
    POST http://localhost:8008/send_invoices/?id_invoice=1
    :param id_invoice:
    :param id_account:
    :param db:
    :return:
    """
    if not id_account and not id_invoice:
        raise HTTPException(400, "Bad Request")
    invoice_search_stmt = billing.Invoice(id=id_invoice, id_account=id_account).dict(exclude_none=True)
    found_invoices = db.query(db_models.Invoice).filter_by(**invoice_search_stmt).all()
    sent_to_accounts = await send_to_accounting(found_invoices)
    if sent_to_accounts:
        return {'sent_invoice_ids': sent_to_accounts}
    else:
        raise HTTPException(204, "No Content")


async def send_to_accounting(found_invoices: list) -> list:
    sent_to_accounts = []
    async with httpx.AsyncClient() as client:
        for invoice in found_invoices:
            invoice = billing.Invoice(**invoice.dict())
            await client.post(f'{config.accounting_url}/update_balance',
                              content=invoice.json(),
                              timeout=15)
            sent_to_accounts.append(invoice.id)
    return sent_to_accounts
