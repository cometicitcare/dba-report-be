"""
Buddhist Affairs MIS Dashboard - Vihaddata (Temple/Vihara) Model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Vihaddata(Base):
    """Temple (Vihara) Registration"""
    __tablename__ = "vihaddata"
    
    vh_id = Column(Integer, primary_key=True, autoincrement=True)
    vh_trn = Column(String(10), unique=True, nullable=False)  # Temple Registration Number
    vh_vname = Column(String(200))  # Temple Name
    vh_addrs = Column(String(200))  # Address
    vh_mobile = Column(String(10))
    vh_whtapp = Column(String(10))  # WhatsApp
    vh_email = Column(String(200))
    vh_typ = Column(String(10))  # Temple Type/Grade (A, B, C, D)
    vh_gndiv = Column(String(10), ForeignKey("cmm_gndata_old.gn_gnc"))
    vh_fmlycnt = Column(Integer)  # Family count
    vh_bgndate = Column(Date)  # Begin/Establishment date
    vh_ownercd = Column(String(12))  # Owner code
    vh_parshawa = Column(String(10), ForeignKey("cmm_parshawadata.pr_prn"))
    vh_ssbmcode = Column(String(10))  # Sasana Rakshaka BM code
    vh_syojakarmakrs = Column(String(100))  # Coordinator
    vh_syojakarmdate = Column(Date)
    vh_landownrship = Column(String(150))  # Land ownership
    vh_pralename = Column(String(50))
    vh_pralesigdate = Column(Date)
    vh_bacgrecmn = Column(String(100))
    vh_bacgrcmdate = Column(Date)
    vh_minissecrsigdate = Column(Date)
    vh_minissecrmrks = Column(String(200))
    vh_ssbmsigdate = Column(Date)
    
    # Location fields
    vh_province = Column(String(100), ForeignKey("cmm_province.cp_code"))
    vh_district = Column(String(100), ForeignKey("cmm_districtdata.dd_dcode"))
    vh_divisional_secretariat = Column(String(100))
    vh_pradeshya_sabha = Column(String(100))
    
    # Temple info
    vh_nikaya = Column(String(50), ForeignKey("cmm_nikayadata.nk_nkn"))
    vh_viharadhipathi_name = Column(String(200))  # Chief monk name
    vh_viharadhipathi_regn = Column(String(50))  # Chief monk registration
    vh_period_established = Column(String(100))
    vh_buildings_description = Column(String(1000))
    vh_dayaka_families_count = Column(String(50))
    vh_kulangana_committee = Column(String(500))
    vh_dayaka_sabha = Column(String(500))
    vh_temple_working_committee = Column(String(500))
    vh_other_associations = Column(String(500))
    
    # Certification fields
    vh_land_info_certified = Column(Boolean)
    vh_resident_bhikkhus_certified = Column(Boolean)
    vh_inspection_report = Column(String(1000))
    vh_inspection_code = Column(String(100))
    vh_grama_niladhari_division_ownership = Column(String(200))
    vh_sanghika_donation_deed = Column(Boolean)
    vh_government_donation_deed = Column(Boolean)
    vh_government_donation_deed_in_progress = Column(Boolean)
    vh_authority_consent_attached = Column(Boolean)
    vh_recommend_new_center = Column(Boolean)
    vh_recommend_registered_temple = Column(Boolean)
    
    # Annex 2 fields
    vh_annex2_recommend_construction = Column(Boolean)
    vh_annex2_land_ownership_docs = Column(Boolean)
    vh_annex2_chief_incumbent_letter = Column(Boolean)
    vh_annex2_coordinator_recommendation = Column(Boolean)
    vh_annex2_divisional_secretary_recommendation = Column(Boolean)
    vh_annex2_approval_construction = Column(Boolean)
    vh_annex2_referral_resubmission = Column(Boolean)
    
    # Mahanayake fields
    vh_mahanayake_date = Column(Date)
    vh_mahanayake_letter_nu = Column(String(50))
    vh_mahanayake_remarks = Column(String(500))
    
    # Workflow fields
    vh_workflow_status = Column(String(25), default="S1_PENDING", nullable=False)
    vh_approval_status = Column(String(20))
    vh_approved_by = Column(String(25))
    vh_approved_at = Column(DateTime(timezone=True))
    vh_rejected_by = Column(String(25))
    vh_rejected_at = Column(DateTime(timezone=True))
    vh_rejection_reason = Column(String(500))
    vh_printed_at = Column(DateTime(timezone=True))
    vh_printed_by = Column(String(25))
    vh_scanned_at = Column(DateTime(timezone=True))
    vh_scanned_by = Column(String(25))
    vh_scanned_document_path = Column(String(500))
    vh_stage2_document_path = Column(String(500))
    
    # Stage 1 workflow
    vh_s1_printed_at = Column(DateTime(timezone=True))
    vh_s1_printed_by = Column(String(25))
    vh_s1_scanned_at = Column(DateTime(timezone=True))
    vh_s1_scanned_by = Column(String(25))
    vh_s1_approved_by = Column(String(25))
    vh_s1_approved_at = Column(DateTime(timezone=True))
    vh_s1_rejected_by = Column(String(25))
    vh_s1_rejected_at = Column(DateTime(timezone=True))
    vh_s1_rejection_reason = Column(String(500))
    
    # Stage 2 workflow
    vh_s2_scanned_at = Column(DateTime(timezone=True))
    vh_s2_scanned_by = Column(String(25))
    vh_s2_approved_by = Column(String(25))
    vh_s2_approved_at = Column(DateTime(timezone=True))
    vh_s2_rejected_by = Column(String(25))
    vh_s2_rejected_at = Column(DateTime(timezone=True))
    vh_s2_rejection_reason = Column(String(500))
    
    # Audit fields
    vh_version = Column(DateTime, default=datetime.utcnow, nullable=False)
    vh_is_deleted = Column(Boolean, default=False)
    vh_created_at = Column(DateTime, default=datetime.utcnow)
    vh_updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    vh_created_by = Column(String(25))
    vh_updated_by = Column(String(25))
    vh_version_number = Column(Integer, default=1)
    vh_form_id = Column(String(50))
    vh_created_by_district = Column(String(10))
    
    # Relationships
    sasanarakshana = relationship("SasanarakshanaRegist", backref="temple")
