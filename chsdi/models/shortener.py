# -*- coding: utf-8

from sqlalchemy import Column, String, DateTime
from chsdi.models import bases

Base = bases['sit']


class UrlShortener(Base):
    __dbname__ = 'sit_dev'
    __tablename__ = 'url_shortener'
    __table_args__ = ({'schema': 'api3', 'autoload': False})
    URL_MAX_LENGTH = 2048
    short_url = Column(String(10), primary_key=True)
    url = Column(String(URL_MAX_LENGTH), nullable=False)
    timestamp = Column(DateTime)
