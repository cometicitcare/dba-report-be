"""
Buddhist Affairs MIS Dashboard - Filter Schemas
"""
from pydantic import BaseModel, Field
from typing import Optional


class DashboardFilters(BaseModel):
    """Filter parameters for dashboard queries"""
    
    # Type filter (from Summary A)
    type_filter: Optional[str] = Field(
        None, 
        description="Type filter: bikku, silmatha, dahampasal_teachers, dahampasal_students, vihara, arama, dahampasal, ssbm"
    )
    
    # Nikaya filter (from Summary B)
    nikaya_code: Optional[str] = Field(
        None, 
        description="Nikaya code filter"
    )
    
    # Grade filter (from Summary C)
    grade: Optional[str] = Field(
        None, 
        description="Vihara grade filter: A, B, C, D"
    )
    
    # Geographic filters
    province_code: Optional[str] = Field(
        None, 
        description="Province code filter"
    )
    
    district_code: Optional[str] = Field(
        None, 
        description="District code filter"
    )
    
    ds_code: Optional[str] = Field(
        None, 
        description="Divisional Secretariat code filter"
    )
    
    gn_code: Optional[str] = Field(
        None, 
        description="Grama Niladhari division code filter"
    )
    
    # Parshawa filter
    parshawa_code: Optional[str] = Field(
        None, 
        description="Parshawa code filter"
    )

    # SSBM filter
    ssbm_code: Optional[str] = Field(
        None,
        description="Sasanarakshana Bala Mandala code filter"
    )

    # Bikku type filter
    bikku_type: Optional[str] = Field(
        None, 
        description="Bikku type: samanera, upasampada, upavidi"
    )
    
    # Pagination
    page: int = Field(1, ge=1, description="Page number")
    page_size: int = Field(50, ge=1, le=500, description="Items per page")
    
    class Config:
        use_enum_values = True


class ProvinceFilter(BaseModel):
    """Province specific filters"""
    province_code: Optional[str] = None
    type_filter: Optional[str] = None
    nikaya_code: Optional[str] = None
    grade: Optional[str] = None


class DistrictFilter(BaseModel):
    """District specific filters"""
    province_code: Optional[str] = None
    district_code: Optional[str] = None
    type_filter: Optional[str] = None
    nikaya_code: Optional[str] = None
    grade: Optional[str] = None


class TempleFilter(BaseModel):
    """Temple list filters"""
    province_code: Optional[str] = None
    district_code: Optional[str] = None
    ds_code: Optional[str] = None
    gn_code: Optional[str] = None
    nikaya_code: Optional[str] = None
    parshawa_code: Optional[str] = None
    ssbm_code: Optional[str] = None
    grade: Optional[str] = None
    search: Optional[str] = Field(None, description="Search term for temple name")
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
