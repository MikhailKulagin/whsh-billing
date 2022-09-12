# https://towardsdatascience.com/fastapi-cloud-database-loading-with-python-1f531f1d438a
import sqlalchemy
from sqlalchemy import BigInteger, String, Integer, Column, DateTime
from sqlalchemy.orm import relationship, class_mapper
from database.db import Base

metadata = sqlalchemy.MetaData()


class DictBase:
    def dict(self):
        columns = [column.key for column in class_mapper(self.__class__).columns]
        return dict(map(lambda c: (c, getattr(self, c)), columns))


class Invoice(Base, DictBase):
    def __init__(self, **kwargs):
        Base.__init__(self, **kwargs)
        DictBase.__init__(self)

    __tablename__ = "t_invoices"
    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True)
    id_account = Column(BigInteger, index=True)
    operation = Column(Integer)
    tstamp = Column(DateTime)
