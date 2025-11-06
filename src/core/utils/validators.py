"""Input Validators"""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        True if valid email format
    """
    if not email:
        return False

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_phone(phone: str, country_code: str = None) -> bool:
    """
    Validate phone number format.

    Args:
        phone: Phone number to validate
        country_code: Optional country code

    Returns:
        True if valid phone format
    """
    if not phone:
        return False

    # Remove common separators
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)

    # Basic validation: 7-15 digits
    if not re.match(r"^\+?[0-9]{7,15}$", cleaned):
        return False

    return True


def validate_passport(passport_number: str) -> bool:
    """
    Validate passport number format.

    Args:
        passport_number: Passport number to validate

    Returns:
        True if valid passport format
    """
    if not passport_number:
        return False

    # Passport format varies by country
    # General validation: 6-12 alphanumeric characters
    if len(passport_number) < 6 or len(passport_number) > 12:
        return False

    # Should contain at least one letter or digit
    if not re.match(r"^[A-Z0-9]+$", passport_number.upper()):
        return False

    return True


def validate_date(date_str: str, format: str = "%Y-%m-%d") -> bool:
    """
    Validate date string format.

    Args:
        date_str: Date string to validate
        format: Expected date format

    Returns:
        True if valid date format
    """
    from datetime import datetime

    if not date_str:
        return False

    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.

    Args:
        filename: Original filename

    Returns:
        Sanitized filename
    """
    # Remove path components
    filename = filename.split("/")[-1].split("\\")[-1]

    # Remove dangerous characters
    filename = re.sub(r'[^\w\s.-]', '', filename)

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:250] + ("." + ext if ext else "")

    return filename


def validate_file_extension(filename: str, allowed_extensions: list) -> bool:
    """
    Validate file extension.

    Args:
        filename: Filename to check
        allowed_extensions: List of allowed extensions (e.g., ['.jpg', '.png'])

    Returns:
        True if extension is allowed
    """
    if not filename or not allowed_extensions:
        return False

    ext = filename.lower().split(".")[-1] if "." in filename else ""
    ext_with_dot = f".{ext}"

    return ext_with_dot in [e.lower() for e in allowed_extensions]
