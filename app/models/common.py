"""
Buddhist Affairs MIS Dashboard - Common Reference Models
Province, District, Nikaya, Parshawa, Divisional Secretariat, GN, etc.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class CmmProvince(Base):
    """Province reference table"""
    __tablename__ = "cmm_province"
    
    cp_id = Column(Integer, primary_key=True, autoincrement=True)
    cp_code = Column(String(10), unique=True, nullable=False)
    cp_name = Column(String(200))
    cp_version = Column(DateTime, default=datetime.utcnow, nullable=False)
    cp_is_deleted = Column(Boolean, default=False)
    cp_created_at = Column(DateTime, default=datetime.utcnow)
    cp_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    cp_created_by = Column(String(25))
    cp_updated_by = Column(String(25))
    cp_version_number = Column(Integer, default=1)
    
    # Relationships
    districts = relationship("CmmDistrictdata", back_populates="province")


class CmmDistrictdata(Base):
    """District reference table"""
    __tablename__ = "cmm_districtdata"
    
    dd_id = Column(Integer, primary_key=True, autoincrement=True)
    dd_dcode = Column(String(10), unique=True, nullable=False)
    dd_dname = Column(String(200))
    dd_prcode = Column(String(10), ForeignKey("cmm_province.cp_code"), nullable=False)
    dd_version = Column(DateTime, default=datetime.utcnow, nullable=False)
    dd_is_deleted = Column(Boolean, default=False)
    dd_created_at = Column(DateTime, default=datetime.utcnow)
    dd_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    dd_created_by = Column(String(25))
    dd_updated_by = Column(String(25))
    dd_version_number = Column(Integer, default=1)
    
    # Relationships
    province = relationship("CmmProvince", back_populates="districts")
    divisional_secretariats = relationship("CmmDvsec", back_populates="district")


class CmmNikayadata(Base):
    """Nikaya (Buddhist Order) reference table"""
    __tablename__ = "cmm_nikayadata"
    
    nk_id = Column(Integer, primary_key=True, autoincrement=True)
    nk_nkn = Column(String(10), unique=True, nullable=False)
    nk_nname = Column(String(200))
    nk_nahimicd = Column(String(12), ForeignKey("bhikku_regist.br_regn"))
    nk_startdate = Column(Date)
    nk_rmakrs = Column(String(200))
    nk_version = Column(DateTime, default=datetime.utcnow, nullable=False)
    nk_is_deleted = Column(Boolean, default=False)
    nk_created_at = Column(DateTime, default=datetime.utcnow)
    nk_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    nk_created_by = Column(String(25))
    nk_updated_by = Column(String(25))
    nk_version_number = Column(Integer, default=1)
    
    # Relationships
    parshawadat = relationship("CmmParshawadata", back_populates="nikaya")


class CmmParshawadata(Base):
    """Parshawa (Buddhist Section) reference table"""
    __tablename__ = "cmm_parshawadata"
    
    pr_id = Column(Integer, primary_key=True, autoincrement=True)
    pr_prn = Column(String(20), unique=True, nullable=False)
    pr_pname = Column(String(200))
    pr_nayakahimi = Column(String(20), nullable=False)
    pr_rmrks = Column(String(200))
    pr_startdate = Column(Date)
    pr_nikayacd = Column(String(10), ForeignKey("cmm_nikayadata.nk_nkn"))
    pr_version = Column(DateTime, default=datetime.utcnow, nullable=False)
    pr_is_deleted = Column(Boolean, default=False)
    pr_created_at = Column(DateTime, default=datetime.utcnow)
    pr_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    pr_created_by = Column(String(25))
    pr_updated_by = Column(String(25))
    pr_version_number = Column(Integer, default=1)
    
    # Relationships
    nikaya = relationship("CmmNikayadata", back_populates="parshawadat")


class CmmDvsec(Base):
    """Divisional Secretariat reference table"""
    __tablename__ = "cmm_dvsec"
    
    dv_id = Column(Integer, primary_key=True, autoincrement=True)
    dv_dvcode = Column(String(10), unique=True, nullable=False)
    dv_distrcd = Column(String(10), ForeignKey("cmm_districtdata.dd_dcode"), nullable=False)
    dv_dvname = Column(String(200))
    dv_version = Column(DateTime, default=datetime.utcnow, nullable=False)
    dv_is_deleted = Column(Boolean, default=False)
    dv_created_at = Column(DateTime, default=datetime.utcnow)
    dv_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    dv_created_by = Column(String(25))
    dv_updated_by = Column(String(25))
    dv_version_number = Column(Integer, default=1)
    
    # Relationships
    district = relationship("CmmDistrictdata", back_populates="divisional_secretariats")
    gn_divisions = relationship("CmmGndata", back_populates="divisional_secretariat")


class CmmGndata(Base):
    """Grama Niladhari Division reference table"""
    __tablename__ = "cmm_gndata"
    
    gn_id = Column(Integer, primary_key=True, autoincrement=True)
    gn_gnc = Column(String(10), unique=True, nullable=False)
    gn_gnc_code = Column(Integer)
    gn_gnname = Column(String(200))
    gn_mbile = Column(String(10))
    gn_email = Column(String(40))
    gn_dvcode = Column(String(10), ForeignKey("cmm_dvsec.dv_dvcode"), nullable=False)
    gn_version = Column(DateTime, default=datetime.utcnow, nullable=False)
    gn_is_deleted = Column(Boolean, default=False)
    gn_created_at = Column(DateTime, default=datetime.utcnow)
    gn_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    gn_created_by = Column(String(25))
    gn_updated_by = Column(String(25))
    gn_version_number = Column(Integer, default=1)
    
    # Relationships
    divisional_secretariat = relationship("CmmDvsec", back_populates="gn_divisions")


class CmmSasanarbm(Base):
    """Sasana Rakshaka Bala Mandala Master reference"""
    __tablename__ = "cmm_sasanarbm"
    
    sr_id = Column(Integer, primary_key=True, autoincrement=True)
    sr_ssbmcode = Column(String(10), unique=True, nullable=False)
    sr_name = Column(String(200))


class SasanarakshanaRegist(Base):
    """Sasanarakshaka Bala Mandala Registration"""
    __tablename__ = "sasanarakshana_regist"
    
    sar_id = Column(Integer, primary_key=True, autoincrement=True)
    sar_temple_trn = Column(String(255), ForeignKey("vihaddata.vh_trn"), nullable=False)
    sar_temple_address = Column(String(500))
    sar_mandala_name = Column(String(255))
    sar_bank_name = Column(String(255))
    sar_account_number = Column(String(100))
    sar_president_name = Column(String(255))
    sar_deputy_president_name = Column(String(255))
    sar_vice_president_1_name = Column(String(255))
    sar_vice_president_2_name = Column(String(255))
    sar_general_secretary_name = Column(String(255))
    sar_deputy_secretary_name = Column(String(255))
    sar_treasurer_name = Column(String(255))
    sar_committee_member_1 = Column(String(255))
    sar_committee_member_2 = Column(String(255))
    sar_committee_member_3 = Column(String(255))
    sar_committee_member_4 = Column(String(255))
    sar_committee_member_5 = Column(String(255))
    sar_committee_member_6 = Column(String(255))
    sar_committee_member_7 = Column(String(255))
    sar_committee_member_8 = Column(String(255))
    sar_chief_organizer_name = Column(String(255))
    sar_is_deleted = Column(Boolean, default=False)
    sar_created_at = Column(DateTime, default=datetime.utcnow)
    sar_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sar_created_by = Column(String(25))
    sar_updated_by = Column(String(25))
    sar_version_number = Column(Integer, default=1)
