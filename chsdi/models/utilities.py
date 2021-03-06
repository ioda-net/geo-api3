# -*- coding: utf-8

from sqlalchemy import Column, String, DateTime
from chsdi.models import (
    bases,
    PARTIALLY_SUPPORTED_DATABASE_TYPE,
)

Base = bases['sit']
if Base.metadata.info.get('type', '') in PARTIALLY_SUPPORTED_DATABASE_TYPE:
    schema = None
else:
    schema = 'api3'


class UrlShortener(Base):
    __tablename__ = 'url_shortener'
    __table_args__ = ({'schema': schema, 'autoload': False})
    URL_MAX_LENGTH = 2048
    short_url = Column(String(10), primary_key=True)
    url = Column(String(URL_MAX_LENGTH), nullable=False)
    createtime = Column(DateTime)
    accesstime = Column(DateTime)
    portal = Column(String(200))


class Files(Base):
    __tablename__ = 'files'
    __table_args__ = ({'schema': schema, 'autoload': False})
    admin_id = Column(String(24), primary_key=True)
    file_id = Column(String(24), primary_key=True)
    mime_type = Column(String(50), nullable=False)
    createtime = Column(DateTime)
    accesstime = Column(DateTime)
    portal = Column(String(200))
