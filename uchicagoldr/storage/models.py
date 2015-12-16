# coding: utf-8
from sqlalchemy import Column, create_engine, Date, DateTime, Float, ForeignKey, Integer, MetaData, String, Table, text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


engine = create_engine("mysql+pymysql://ldr:JaQhXZZ5ZB8V3Gsu@duodecimo.lib.uchicago.edu/ldr_development")
Base = declarative_base(engine)
metadata = MetaData()
metadata.reflect(bind=engine)

class Family(Base):
    __table__ = Table('Family', metadata, autoload = True)


class Agent(Base):
    __table__ = Table('Agent', metadata, autoload = True)


class AgentRole(Base):
    __table__ = Table('AgentRole', metadata, autoload = True)


class Department(Base):
    __table__ = Table('Department', metadata, autoload = True)


class AssignedFamily(Base):
    __table__ = Table('AssignedFamily', metadata, autoload = True)


class RelatedFilePointer(Base):
    __table__ = Table('RelatedFilePointer', metadata, autoload = True)


class FamilyHasType(Base):
    __table__ = Table('FamilyHasType', metadata, autoload = True)


class FamilyStatus(Base):
    __table__ = Table('FamilyStatus', metadata, autoload = True)


class FamilyVersion(Base):
    __table__ = Table('FamilyVersion', metadata, autoload = True)


class ValidateRecord(Base):
    __table__ = Table("ValidateRecord", metadata, autoload = True)


class RelatedFamily(Base):
    __table__ = Table("RelatedFamily", metadata, autoload = True)


class FamilyType(Base):
    __table__ = Table("FamilyType", metadata, autoload = True)


class StructuralFamilyRequired(Base):
    __table__ = Table("structureFamilyRequired", metadata, autoload = True)


class StructuralRule(Base):
    __table__ = Table("structuralRule", metadata, autoload = True)


class FilePointer(Base):
    __table__ = Table("FilePointer", metadata, autoload = True)


class Schema(Base):
    __table__ = Table("Schema", metadata, autoload = True)


class DescriptiveRule(Base):
    __table__ = Table("descriptiveRule", metadata, autoload = True)


class StructuralCondition(Base):
    __table__ = Table("structuralCondition", metadata, autoload = True)


class StructuralFileTypeRequired(Base):
    __table__ = Table("structureFileTypeRequired", metadata, autoload = True)


class Attribute(Base):
    __table__ = Table("Attribute", metadata, autoload = True)


class FamilyAttribute(Base):
    __table__ = Table("FamilyAttribute", metadata, autoload = True)
