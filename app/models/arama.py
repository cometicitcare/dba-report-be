"""
Buddhist Affairs MIS Dashboard - Aramadata (Arama/Hermitage) Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Date
from datetime import datetime

from app.database import Base


class Aramadata(Base):
    """Arama (Hermitage) Registration"""
    __tablename__ = "aramadata"
    
    ar_id = Column(Integer, primary_key=True, autoincrement=True)
    ar_trn = Column(String(10), unique=True, nullable=False)  # Registration Number
    ar_vname = Column(String(200))  # Name
    ar_addrs = Column(String(200))  # Address
    ar_mobile = Column(String(10), nullable=False)
    ar_whtapp = Column(String(10), nullable=False)  # WhatsApp
    ar_email = Column(String(200), unique=True)
    ar_typ = Column(String(10), nullable=False)  # Type
    ar_gndiv = Column(String(10), nullable=False)  # GN Division
    ar_fmlycnt = Column(Integer)  # Family count
    ar_bgndate = Column(Date)  # Begin date
    ar_ownercd = Column(String(12), nullable=False)  # Owner code
    ar_parshawa = Column(String(10), nullable=False)  # Parshawa
    ar_ssbmcode = Column(String(10))  # SSBM code
    ar_syojakarmakrs = Column(String(100))  # Coordinator
    ar_syojakarmdate = Column(Date)
    ar_landownrship = Column(String(150))  # Land ownership
    ar_landsize = Column(String(200))  # Land size
    ar_landownershiptype = Column(String(500))  # Land ownership type
    ar_pralename = Column(String(50))
    ar_pralesigdate = Column(Date)
    ar_bacgrecmn = Column(String(100))
    ar_bacgrcmdate = Column(Date)
    ar_minissecrsigdate = Column(Date)
    ar_minissecrmrks = Column(String(200))
    ar_ssbmsigdate = Column(Date)
    
    # Location fields
    ar_province = Column(String(100))
    ar_district = Column(String(100))
    ar_divisional_secretariat = Column(String(100))
    ar_pradeshya_sabha = Column(String(100))
    
    # Arama info
    ar_nikaya = Column(String(50))
    ar_viharadhipathi_name = Column(String(200))
    ar_period_established = Column(String(100))
    ar_buildings_description = Column(String(1000))
    ar_dayaka_families_count = Column(String(50))
    ar_kulangana_committee = Column(String(500))
    ar_dayaka_sabha = Column(String(500))
    ar_temple_working_committee = Column(String(500))
    ar_other_associations = Column(String(500))
    
    # Certification fields
    ar_land_info_certified = Column(Boolean)
    ar_resident_bhikkhus_certified = Column(Boolean)
    ar_resident_silmathas_certified = Column(Boolean)
    ar_inspection_report = Column(String(1000))
    ar_inspection_code = Column(String(100))
    ar_grama_niladhari_division_ownership = Column(String(200))
    ar_sanghika_donation_deed = Column(Boolean)
    ar_government_donation_deed = Column(Boolean)
    ar_government_donation_deed_in_progress = Column(Boolean)
    ar_authority_consent_attached = Column(Boolean)
    ar_recommend_new_center = Column(Boolean)
    ar_recommend_registered_temple = Column(Boolean)
    
    # Annex 2 fields
    ar_annex2_recommend_construction = Column(Boolean)
    ar_annex2_land_ownership_docs = Column(Boolean)
    ar_annex2_chief_incumbent_letter = Column(Boolean)
    ar_annex2_coordinator_recommendation = Column(Boolean)
    ar_annex2_divisional_secretary_recommendation = Column(Boolean)
    ar_annex2_approval_construction = Column(Boolean)
    ar_annex2_referral_resubmission = Column(Boolean)
    
    # Workflow fields
    ar_workflow_status = Column(String(20), default="PENDING", nullable=False)
    ar_approval_status = Column(String(20))
    ar_approved_by = Column(String(25))
    ar_approved_at = Column(DateTime(timezone=True))
    ar_rejected_by = Column(String(25))
    ar_rejected_at = Column(DateTime(timezone=True))
    ar_rejection_reason = Column(String(500))
    ar_printed_at = Column(DateTime(timezone=True))
    ar_printed_by = Column(String(25))
    ar_scanned_at = Column(DateTime(timezone=True))
    ar_scanned_by = Column(String(25))
    ar_scanned_document_path = Column(String(500))
    
    # Audit fields
    ar_version = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    ar_is_deleted = Column(Boolean, default=False, nullable=False)
    ar_created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    ar_updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    ar_created_by = Column(String(25))
    ar_updated_by = Column(String(25))
    ar_version_number = Column(Integer, default=1, nullable=False)
    ar_form_id = Column(String(50))
    ar_created_by_district = Column(String(10))
    ar_is_temporary_record = Column(Boolean, default=False)
