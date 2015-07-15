# -*- coding: utf-8

from sqlalchemy import Column, String, DateTime, Integer
from geoalchemy2.types import Geometry
from chsdi.models import bases

Base = bases['sit']


class UrlShortener(Base):
    __tablename__ = 'url_shortener'
    __table_args__ = ({'schema': 'api3', 'autoload': False})
    URL_MAX_LENGTH = 2048
    short_url = Column(String(10), primary_key=True)
    url = Column(String(URL_MAX_LENGTH), nullable=False)
    createtime = Column(DateTime)


class Files(Base):
    __tablename__ = 'files'
    __table_args__ = ({'schema': 'api3', 'autoload': False})
    admin_id = Column(String(24), primary_key=True)
    file_id = Column(String(24), primary_key=True)
    mime_type = Column(String(50), nullable=False)
    createtime = Column(DateTime)


class Communes(Base):
    __tablename__ = 'communes'
    __table_args__ = ({'schema': 'userdata', 'autoload': False})
    gid = Column(Integer, primary_key=True)
    nom = Column(String)
    the_geom = Column(Geometry(geometry_type='GEOMETRY', srid=21781, dimension=2))
