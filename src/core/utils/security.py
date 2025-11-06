"""Security Utilities"""

import os
import secrets
from typing import Optional
from datetime import datetime, timedelta

try:
    import bcrypt
    BCRYPT_AVAILABLE = True
except ImportError:
    BCRYPT_AVAILABLE = False
    bcrypt = None

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    jwt = None


def hash_password(password: str) -> str:
    """
    Hash password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password
    """
    if not BCRYPT_AVAILABLE:
        raise ImportError("bcrypt not installed. Install: pip install bcrypt")

    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify password against hash.

    Args:
        password: Plain text password
        hashed: Hashed password

    Returns:
        True if password matches hash
    """
    if not BCRYPT_AVAILABLE:
        raise ImportError("bcrypt not installed. Install: pip install bcrypt")

    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def generate_token(
    data: dict,
    secret_key: str = None,
    expires_minutes: int = 60,
    algorithm: str = "HS256",
) -> str:
    """
    Generate JWT token.

    Args:
        data: Payload data
        secret_key: Secret key for signing
        expires_minutes: Token expiration time in minutes
        algorithm: JWT algorithm

    Returns:
        JWT token
    """
    if not JWT_AVAILABLE:
        raise ImportError("PyJWT not installed. Install: pip install PyJWT")

    key = secret_key or os.getenv("JWT_SECRET_KEY", "default-secret-key")

    payload = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    payload.update({"exp": expire, "iat": datetime.utcnow()})

    token = jwt.encode(payload, key, algorithm=algorithm)
    return token


def verify_token(token: str, secret_key: str = None, algorithm: str = "HS256") -> Optional[dict]:
    """
    Verify and decode JWT token.

    Args:
        token: JWT token
        secret_key: Secret key for verification
        algorithm: JWT algorithm

    Returns:
        Decoded payload or None if invalid
    """
    if not JWT_AVAILABLE:
        raise ImportError("PyJWT not installed. Install: pip install PyJWT")

    key = secret_key or os.getenv("JWT_SECRET_KEY", "default-secret-key")

    try:
        payload = jwt.decode(token, key, algorithms=[algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def generate_secret_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure secret key.

    Args:
        length: Length of the key in bytes

    Returns:
        Hex-encoded secret key
    """
    return secrets.token_hex(length)


def generate_session_id() -> str:
    """Generate a secure session ID."""
    return secrets.token_urlsafe(32)
