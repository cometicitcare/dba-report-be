"""
Buddhist Affairs MIS Dashboard - Bhikku (Buddhist Monk) Models
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class BhikkuRegist(Base):
    """Bhikku (Samanera) Registration - Base registration for all monks"""
    __tablename__ = "bhikku_regist"
    
    br_id = Column(Integer, primary_key=True, autoincrement=True)
    br_regn = Column(String(20), unique=True, nullable=False)
    br_reqstdate = Column(Date)
    br_gihiname = Column(String(50))
    br_dofb = Column(Date)
    br_fathrname = Column(String(50))
    br_email = Column(String(50))
    br_mobile = Column(String(10))
    br_fathrsaddrs = Column(String(200))
    br_fathrsmobile = Column(String(10))
    br_birthpls = Column(String(50))
    br_province = Column(String(50), ForeignKey("cmm_province.cp_code"))
    br_district = Column(String(50), ForeignKey("cmm_districtdata.dd_dcode"))
    br_korale = Column(String(50))
    br_pattu = Column(String(50))
    br_division = Column(String(50))
    br_vilage = Column(String(50))
    br_gndiv = Column(String(10))
    br_viharadhipathi = Column(String(20))
    br_cat = Column(String(5))  # Category
    br_currstat = Column(String(5), nullable=False)  # Current status
    br_nikaya = Column(String(10), ForeignKey("cmm_nikayadata.nk_nkn"))
    br_parshawa = Column(String(10), ForeignKey("cmm_parshawadata.pr_prn"))
    br_livtemple = Column(String(10))  # Living temple TRN
    br_declaration_date = Column(Date)
    br_remarks = Column(String(100))
    br_robing_date = Column(Date)
    br_robing_name = Column(String(50))
    br_robing_acharya_code = Column(String(500))
    br_robing_tutor_residence = Column(String(20))
    br_robing_temple = Column(String(10))
    br_robing_after_residence_temple = Column(String(20))
    
    # Workflow fields
    br_workflow_status = Column(String(20), default="PENDING", nullable=False)
    br_approval_status = Column(String(20))
    br_approved_by = Column(String(25))
    br_approved_at = Column(DateTime)
    br_rejected_by = Column(String(25))
    br_rejected_at = Column(DateTime)
    br_rejection_reason = Column(String(500))
    br_printed_at = Column(DateTime)
    br_printed_by = Column(String(25))
    br_scanned_at = Column(DateTime)
    br_scanned_by = Column(String(25))
    br_scanned_document_path = Column(String(500))
    
    # Audit fields
    br_version = Column(DateTime, default=datetime.utcnow, nullable=False)
    br_is_deleted = Column(Boolean, default=False)
    br_created_at = Column(DateTime, default=datetime.utcnow)
    br_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    br_created_by = Column(String(25))
    br_updated_by = Column(String(25))
    br_version_number = Column(Integer, default=1)
    br_created_by_district = Column(String(10))
    br_form_id = Column(String(50))


class BhikkuHighRegist(Base):
    """Bhikku Higher Ordination (Upasampada) Registration"""
    __tablename__ = "bhikku_high_regist"
    
    bhr_id = Column(Integer, primary_key=True, autoincrement=True)
    bhr_regn = Column(String(12), unique=True, nullable=False)
    bhr_samanera_serial_no = Column(String(20), ForeignKey("bhikku_regist.br_regn"))
    bhr_reqstdate = Column(Date)
    bhr_remarks = Column(String(500))
    bhr_currstat = Column(String(5))
    bhr_parshawaya = Column(String(10))
    bhr_livtemple = Column(String(10))
    bhr_cc_code = Column(String(10))
    bhr_candidate_regn = Column(String(20), ForeignKey("bhikku_regist.br_regn"))
    bhr_higher_ordination_place = Column(String(50))
    bhr_higher_ordination_date = Column(Date)
    bhr_karmacharya_name = Column(String(100))
    bhr_upaddhyaya_name = Column(String(100))
    bhr_assumed_name = Column(String(100))
    bhr_residence_higher_ordination_trn = Column(String(50), ForeignKey("vihaddata.vh_trn"))
    bhr_residence_permanent_trn = Column(String(50), ForeignKey("vihaddata.vh_trn"))
    bhr_declaration_residence_address = Column(String(200))
    bhr_tutors_tutor_regn = Column(String(20), ForeignKey("bhikku_regist.br_regn"))
    bhr_presiding_bhikshu_regn = Column(String(20), ForeignKey("bhikku_regist.br_regn"))
    bhr_declaration_date = Column(Date)
    
    # Workflow fields
    bhr_workflow_status = Column(String(20), default="PENDING", nullable=False)
    bhr_approval_status = Column(String(20))
    bhr_approved_by = Column(String(25))
    bhr_approved_at = Column(DateTime)
    bhr_rejected_by = Column(String(25))
    bhr_rejected_at = Column(DateTime)
    bhr_rejection_reason = Column(String(500))
    bhr_printed_at = Column(DateTime)
    bhr_printed_by = Column(String(25))
    bhr_scanned_at = Column(DateTime)
    bhr_scanned_by = Column(String(25))
    bhr_scanned_document_path = Column(String(500))
    
    # Audit fields
    bhr_version = Column(DateTime, default=datetime.utcnow, nullable=False)
    bhr_is_deleted = Column(Boolean, default=False)
    bhr_created_at = Column(DateTime, default=datetime.utcnow)
    bhr_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    bhr_created_by = Column(String(25))
    bhr_updated_by = Column(String(25))
    bhr_version_number = Column(Integer, default=1)
    bhr_created_by_district = Column(String(10))
    bhr_form_id = Column(String(50))
