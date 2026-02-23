"""
Buddhist Affairs MIS Dashboard - Dashboard Response Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


# ============================================
# Section 1 - Overall Summary Schemas
# ============================================

class SummaryTypeItem(BaseModel):
    """Summary A - Type breakdown item"""
    type_name: str = Field(..., description="Type name (Bikku, Silmatha, etc.)")
    type_key: str = Field(..., description="Type key for filtering")
    total: int = Field(0, description="Total count")
    icon: Optional[str] = Field(None, description="Icon identifier")


class SummaryNikayaItem(BaseModel):
    """Summary B - Nikaya breakdown item"""
    nikaya_code: str = Field(..., description="Nikaya code")
    nikaya_name: str = Field(..., description="Nikaya name")
    total: int = Field(0, description="Total bhikku count (backward compat)")
    vihara_count: int = Field(0, description="Vihara count")
    bhikku_count: int = Field(0, description="Bhikku count")
    silmatha_count: int = Field(0, description="Silmatha count")
    arama_count: int = Field(0, description="Arama count")


class SummaryGradeItem(BaseModel):
    """Summary C - Vihara Grading breakdown item"""
    grade: str = Field(..., description="Grade (A, B, C, D)")
    grade_name: str = Field(..., description="Grade display name")
    total: int = Field(0, description="Total count")


class Section1Response(BaseModel):
    """Section 1 - Overall Summary Response"""
    summary_a: List[SummaryTypeItem] = Field(default_factory=list, description="Type summary")
    summary_b: List[SummaryNikayaItem] = Field(default_factory=list, description="Nikaya summary")
    summary_c: List[SummaryGradeItem] = Field(default_factory=list, description="Grade summary")
    

# ============================================
# Section 2 - Detail Reports Schemas
# ============================================

class BikkuTypeItem(BaseModel):
    """Bikku Type breakdown item"""
    type_name: str = Field(..., description="Type (Samanera, Upasampada, Upavidi)")
    type_key: str = Field(..., description="Type key for filtering")
    total: int = Field(0, description="Total count")


class DahampasalItem(BaseModel):
    """Dahampasal location breakdown item"""
    location: str = Field(..., description="Location (In Temple, Out of Temple)")
    location_key: str = Field(..., description="Location key")
    total: int = Field(0, description="Total count")


class TeacherItem(BaseModel):
    """Dahampasal Teacher breakdown item"""
    teacher_type: str = Field(..., description="Teacher type")
    teacher_key: str = Field(..., description="Teacher type key")
    total: int = Field(0, description="Total count")


class StudentItem(BaseModel):
    """Dahampasal Student breakdown item"""
    gender: str = Field(..., description="Gender (Male, Female)")
    gender_key: str = Field(..., description="Gender key")
    total: int = Field(0, description="Total count")


class Section2Response(BaseModel):
    """Section 2 - Detail Reports Response"""
    bikku_type: List[BikkuTypeItem] = Field(default_factory=list)
    dahampasal: List[DahampasalItem] = Field(default_factory=list)
    dahampasal_teachers: List[TeacherItem] = Field(default_factory=list)
    dahampasal_students: List[StudentItem] = Field(default_factory=list)


class GeographicItem(BaseModel):
    """Geographic breakdown item (Province/District)"""
    code: str = Field(..., description="Province/District code")
    name: str = Field(..., description="Province/District name")
    ssbm_count: int = Field(0, description="SSBM count")
    bikku_count: int = Field(0, description="Bikku count")
    silmatha_count: int = Field(0, description="Silmatha count")
    dahampasal_teachers_count: int = Field(0, description="Dahampasal Teachers count")
    dahampasal_students_count: int = Field(0, description="Dahampasal Students count")
    vihara_count: int = Field(0, description="Vihara count")
    arama_count: int = Field(0, description="Arama count")
    dahampasal_count: int = Field(0, description="Dahampasal count")


class GeographicResponse(BaseModel):
    """Geographic data response"""
    data: List[GeographicItem] = Field(default_factory=list)
    total_count: int = Field(0, description="Total records")


# ============================================
# Section 3 - Selection Reports Schemas
# ============================================

class ParshawaItem(BaseModel):
    """Parshawa breakdown item"""
    parshawa_code: str = Field(..., description="Parshawa code")
    parshawa_name: str = Field(..., description="Parshawa name")
    total: int = Field(0, description="Total vihara count")
    vihara_count: int = Field(0, description="Vihara count")
    bhikku_count: int = Field(0, description="Bhikku count")
    silmatha_count: int = Field(0, description="Silmatha count")
    arama_count: int = Field(0, description="Arama count")


class SSBMItem(BaseModel):
    """SSBM by Nikaya breakdown item"""
    nikaya_code: str = Field(..., description="Nikaya code")
    nikaya_name: str = Field(..., description="Nikaya name")
    total: int = Field(0, description="Total SSBM count")
    vihara_count: int = Field(0, description="Vihara count")
    bhikku_count: int = Field(0, description="Bhikku count")
    silmatha_count: int = Field(0, description="Silmatha count")
    arama_count: int = Field(0, description="Arama count")


class DivisionalSecItem(BaseModel):
    """Divisional Secretariat breakdown item"""
    ds_code: str = Field(..., description="DS code")
    ds_name: str = Field(..., description="DS name")
    total: int = Field(0, description="Total vihara count")
    vihara_count: int = Field(0, description="Vihara count")
    bhikku_count: int = Field(0, description="Bhikku count")
    silmatha_count: int = Field(0, description="Silmatha count")
    arama_count: int = Field(0, description="Arama count")


class GNItem(BaseModel):
    """Grama Niladhari Division breakdown item"""
    gn_code: str = Field(..., description="GN code")
    gn_name: str = Field(..., description="GN name")
    total: int = Field(0, description="Total vihara count")
    vihara_count: int = Field(0, description="Vihara count")
    bhikku_count: int = Field(0, description="Bhikku count")
    silmatha_count: int = Field(0, description="Silmatha count")
    arama_count: int = Field(0, description="Arama count")


class TempleListItem(BaseModel):
    """Temple list item for Section 3"""
    vihara_id:      Optional[str] = Field(None, description="Internal TRN key")
    reg_no:         Optional[str] = Field(None, description="Temple registration number (vh_trn)")
    vihara_name:    Optional[str] = Field(None, description="Temple name (Sinhala)")
    vihara_name_en: Optional[str] = Field(None, description="Temple name (English)")
    address:        Optional[str] = Field(None, description="Address")
    nikaya_name:    Optional[str] = Field(None, description="Nikaya name")
    parshawa_name:  Optional[str] = Field(None, description="Parshawa name")
    grade:          Optional[str] = Field(None, description="Temple grade/type")
    province_name:  Optional[str] = Field(None, description="Province name")
    district_name:  Optional[str] = Field(None, description="District name")
    ds_name:        Optional[str] = Field(None, description="Divisional Secretariat name")
    gn_name:        Optional[str] = Field(None, description="GN Division name")
    chief_of_temple: Optional[str] = Field(None, description="Viharadhipathi name")
    mobile:         Optional[str] = Field(None, description="Mobile number")
    updated_at:     Optional[str] = Field(None, description="Last updated datetime (vh_updated_at)")
    # legacy aliases kept for backward compatibility
    temple_trn:     Optional[str] = Field(None, description="Alias for reg_no")
    temple_name:    Optional[str] = Field(None, description="Alias for vihara_name")


class Section3Response(BaseModel):
    """Section 3 - Selection Reports Response"""
    parshawa: List[ParshawaItem] = Field(default_factory=list)
    ssbm_by_nikaya: List[SSBMItem] = Field(default_factory=list)
    divisional_secretariat: List[DivisionalSecItem] = Field(default_factory=list)
    gn_divisions: List[GNItem] = Field(default_factory=list)
    temples: List[TempleListItem] = Field(default_factory=list)


# ============================================
# Persons (Bhikku / Silmatha) Schemas
# ============================================

class PersonListItem(BaseModel):
    """Person list item — Bhikku or Silmatha"""
    person_id:     Optional[str] = Field(None)
    reg_no:        Optional[str] = Field(None)
    person_type:   Optional[str] = Field(None, description="BHIKKU or SILMATHA")
    name:          Optional[str] = Field(None, description="Display name (ordained or lay)")
    lay_name:      Optional[str] = Field(None)
    ordained_name: Optional[str] = Field(None)
    dob:           Optional[str] = Field(None)
    mobile:        Optional[str] = Field(None)
    nikaya_name:   Optional[str] = Field(None)
    parshawa_name: Optional[str] = Field(None)
    vihara_name:   Optional[str] = Field(None)
    province_name: Optional[str] = Field(None)
    district_name: Optional[str] = Field(None)
    category:      Optional[str] = Field(None, description="br_cat / sil_cat")
    status:        Optional[str] = Field(None, description="Current status code")
    updated_at:    Optional[str] = Field(None)


# ============================================
# Section 4 - Temple Profile Schemas
# ============================================

class TempleGeneralInfo(BaseModel):
    """Temple general information"""
    temple_trn: str
    name: str
    address: Optional[str] = None
    mobile: Optional[str] = None
    email: Optional[str] = None
    registration_no: Optional[str] = None
    viharadhipathi_name: Optional[str] = None
    viharadhipathi_regn: Optional[str] = None
    nikaya: Optional[str] = None
    parshawa: Optional[str] = None
    establishment_date: Optional[date] = None
    period_established: Optional[str] = None


class TempleLocation(BaseModel):
    """Temple location details"""
    province: Optional[str] = None
    province_name: Optional[str] = None
    district: Optional[str] = None
    district_name: Optional[str] = None
    divisional_secretariat: Optional[str] = None
    pradeshya_sabha: Optional[str] = None
    gn_division: Optional[str] = None


class TempleViharanga(BaseModel):
    """Temple buildings/structures"""
    buildings_description: Optional[str] = None
    dayaka_families_count: Optional[str] = None
    kulangana_committee: Optional[str] = None
    dayaka_sabha: Optional[str] = None
    temple_working_committee: Optional[str] = None
    other_associations: Optional[str] = None


class TempleDahampasal(BaseModel):
    """Temple Dahampasal information"""
    dahampasal_name: Optional[str] = None
    teachers_count: int = 0
    students_count: int = 0


class TempleProfileResponse(BaseModel):
    """Section 4 - Temple Profile Response"""
    general_info: TempleGeneralInfo
    location: TempleLocation
    viharanga: TempleViharanga
    dahampasal: Optional[TempleDahampasal] = None
    grade: Optional[str] = None
    workflow_status: Optional[str] = None
