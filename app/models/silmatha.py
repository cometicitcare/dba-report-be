"""
Buddhist Affairs MIS Dashboard - Silmatha (Buddhist Nun) Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date, Numeric
from datetime import datetime

from app.database import Base


class SilmathaRegist(Base):
    """Silmatha (Buddhist Nun) Registration"""
    __tablename__ = "silmatha_regist"
    
    sil_id = Column(Integer, primary_key=True, autoincrement=True)
    sil_regn = Column(String(20), unique=True, nullable=False)
    sil_reqstdate = Column(Date, nullable=False)
    sil_gihiname = Column(String(50))
    sil_dofb = Column(Date)
    sil_fathrname = Column(String(50))
    sil_email = Column(String(50))
    sil_mobile = Column(String(10))
    sil_fathrsaddrs = Column(String(200))
    sil_fathrsmobile = Column(String(10))
    sil_birthpls = Column(String(50))
    sil_province = Column(String(50), ForeignKey("cmm_province.cp_code"))
    sil_district = Column(String(50), ForeignKey("cmm_districtdata.dd_dcode"))
    sil_korale = Column(String(50))
    sil_pattu = Column(String(50))
    sil_division = Column(String(50))
    sil_vilage = Column(String(50))
    sil_gndiv = Column(String(10))
    sil_viharadhipathi = Column(String(20), ForeignKey("bhikku_regist.br_regn"))
    sil_cat = Column(String(5))
    sil_currstat = Column(String(5), nullable=False)
    sil_declaration_date = Column(Date)
    sil_remarks = Column(String(100))
    sil_mahanadate = Column(Date)
    sil_mahananame = Column(String(50))
    sil_mahanaacharyacd = Column(String(500))
    sil_robing_tutor_residence = Column(String(20))
    sil_mahanatemple = Column(String(10))
    sil_robing_after_residence_temple = Column(String(20))
    sil_scanned_document_path = Column(String(500))
    sil_aramadhipathi = Column(String(20))
    sil_is_temporary_record = Column(Boolean, default=False)
    
    # Signature fields
    sil_student_signature = Column(Boolean)
    sil_acharya_signature = Column(Boolean)
    sil_aramadhipathi_signature = Column(Boolean)
    sil_district_secretary_signature = Column(Boolean)
    
    # Workflow fields
    sil_workflow_status = Column(String(20), default="PENDING", nullable=False)
    sil_approval_status = Column(String(20))
    sil_approved_by = Column(String(25))
    sil_approved_at = Column(DateTime)
    sil_rejected_by = Column(String(25))
    sil_rejected_at = Column(DateTime)
    sil_rejection_reason = Column(String(500))
    sil_printed_at = Column(DateTime)
    sil_printed_by = Column(String(25))
    sil_scanned_at = Column(DateTime)
    sil_scanned_by = Column(String(25))
    
    # Reprint fields
    sil_reprint_status = Column(String(20))
    sil_reprint_requested_by = Column(String(25))
    sil_reprint_requested_at = Column(DateTime)
    sil_reprint_request_reason = Column(String(500))
    sil_reprint_approved_by = Column(String(25))
    sil_reprint_approved_at = Column(DateTime)
    sil_reprint_rejected_by = Column(String(25))
    sil_reprint_rejected_at = Column(DateTime)
    sil_reprint_rejection_reason = Column(String(500))
    sil_reprint_completed_by = Column(String(25))
    sil_reprint_completed_at = Column(DateTime)
    sil_reprint_amount = Column(Numeric(10, 2))
    sil_reprint_remarks = Column(String(500))
    sil_reprint_form_no = Column(String(50))
    
    # Audit fields
    sil_version = Column(DateTime, default=datetime.utcnow, nullable=False)
    sil_is_deleted = Column(Boolean, default=False)
    sil_created_at = Column(DateTime, default=datetime.utcnow)
    sil_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    sil_created_by = Column(String(25))
    sil_updated_by = Column(String(25))
    sil_version_number = Column(Integer, default=1)
    sil_created_by_district = Column(String(10))
    sil_form_id = Column(String(50))
