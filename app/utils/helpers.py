"""
Buddhist Affairs MIS Dashboard - Helper Utilities
"""
from typing import Any, Optional


def format_count(count: int) -> str:
    """
    Format large numbers with K/M suffixes.
    
    Examples:
        1000 -> "1K"
        1500 -> "1.5K"
        1000000 -> "1M"
    """
    if count >= 1000000:
        return f"{count/1000000:.1f}M".rstrip('0').rstrip('.')
    elif count >= 1000:
        return f"{count/1000:.1f}K".rstrip('0').rstrip('.')
    return str(count)


def safe_string(value: Any, default: str = "") -> str:
    """
    Safely convert a value to string, returning default if None.
    """
    if value is None:
        return default
    return str(value)


def clean_sql_input(value: str) -> str:
    """
    Basic SQL injection prevention.
    Note: Always prefer parameterized queries.
    """
    if not value:
        return ""
    
    # Remove potentially dangerous characters
    dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "\\"]
    cleaned = value
    for char in dangerous_chars:
        cleaned = cleaned.replace(char, "")
    
    return cleaned.strip()


def build_where_clause(filters: dict, table_alias: str = "") -> tuple:
    """
    Build SQL WHERE clause from filter dictionary.
    
    Args:
        filters: Dictionary of field:value pairs
        table_alias: Optional table alias prefix
    
    Returns:
        Tuple of (where_clause_string, params_dict)
    """
    conditions = []
    params = {}
    
    prefix = f"{table_alias}." if table_alias else ""
    
    for field, value in filters.items():
        if value is not None:
            param_name = field.replace(".", "_")
            conditions.append(f"{prefix}{field} = :{param_name}")
            params[param_name] = value
    
    if conditions:
        return " AND ".join(conditions), params
    
    return "1=1", {}


def paginate(page: int, page_size: int) -> tuple:
    """
    Calculate offset and limit for pagination.
    
    Args:
        page: Page number (1-based)
        page_size: Items per page
    
    Returns:
        Tuple of (offset, limit)
    """
    page = max(1, page)
    page_size = max(1, min(page_size, 500))  # Cap at 500
    offset = (page - 1) * page_size
    return offset, page_size
