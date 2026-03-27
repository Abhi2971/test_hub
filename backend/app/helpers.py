"""
Utility helper functions for ExamSaaS platform.
"""
import logging
from decimal import Decimal, ROUND_HALF_UP
from bson.decimal128 import Decimal128

logger = logging.getLogger(__name__)


def paise_to_rupees(paise: int) -> Decimal:
    """
    Convert paise to rupees.
    
    Args:
        paise: Amount in paise (integer)
    
    Returns:
        Decimal amount in rupees
    """
    if paise is None:
        return Decimal('0')
    return Decimal(str(paise)) / Decimal('100')


def rupees_to_paise(rupees: float) -> int:
    """
    Convert rupees to paise.
    
    Args:
        rupees: Amount in rupees (float)
    
    Returns:
        Integer amount in paise
    """
    if rupees is None:
        return 0
    d = Decimal(str(rupees)) * Decimal('100')
    return int(d.to_integral_value(rounding=ROUND_HALF_UP))


def format_currency(paise: int, currency: str = "INR") -> str:
    """
    Format paise amount as currency string.
    
    Args:
        paise: Amount in paise
        currency: Currency code (default INR)
    
    Returns:
        Formatted string like "₹199.00"
    """
    rupees = paise_to_rupees(paise)
    if currency == "INR":
        return f"\u20b9{rupees:.2f}"
    return f"{rupees:.2f} {currency}"


def decimal_to_decimal128(decimal_value: Decimal) -> Decimal128:
    """
    Convert Python Decimal to MongoDB Decimal128.
    
    Args:
        decimal_value: Python Decimal
    
    Returns:
        Decimal128 for MongoDB storage
    """
    return Decimal128(decimal_value)


def decimal128_to_decimal(decimal128_value: Decimal128) -> Decimal:
    """
    Convert MongoDB Decimal128 to Python Decimal.
    
    Args:
        decimal128_value: Decimal128 from MongoDB
    
    Returns:
        Python Decimal
    """
    if decimal128_value is None:
        return Decimal('0')
    return decimal128_value.to_decimal()


def generate_slug(text: str) -> str:
    """
    Generate URL-friendly slug from text.
    
    Args:
        text: Input text
    
    Returns:
        Slugified string
    """
    import re
    slug = text.lower()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug


def generate_ticket_number() -> str:
    """
    Generate unique ticket number.
    
    Returns:
        Ticket number string like "TKT-2024-00001"
    """
    import random
    import string
    from datetime import datetime
    year = datetime.now().year
    random_part = ''.join(random.choices(string.digits, k=5))
    return f"TKT-{year}-{random_part}"


def generate_certificate_code() -> str:
    """
    Generate unique certificate code.
    
    Returns:
        Certificate code string like "CERT-ABC123XYZ"
    """
    import random
    import string
    chars = string.ascii_uppercase + string.digits
    code = ''.join(random.choices(chars, k=12))
    return f"CERT-{code}"


def sanitize_string(text: str) -> str:
    """
    Sanitize string input for safe storage.
    
    Args:
        text: Raw input string
    
    Returns:
        Sanitized string
    """
    if not text:
        return ""
    import bleach
    return bleach.clean(text, tags=[], attributes={}, strip=True).strip()


logger.info("Helper functions loaded")
