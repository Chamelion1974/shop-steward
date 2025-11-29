"""
Password reset token model.
"""
from sqlalchemy import Column, String, DateTime, ForeignKey
from datetime import datetime, timedelta
import uuid
import secrets

from ..database import Base


class PasswordResetToken(Base):
    """Password reset token model."""

    __tablename__ = "password_reset_tokens"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String, unique=True, nullable=False, index=True)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)  # Track if token was used

    @staticmethod
    def generate_token():
        """Generate a secure random token."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def get_expiry_time(hours=1):
        """Get expiry time (default 1 hour from now)."""
        return datetime.utcnow() + timedelta(hours=hours)

    def is_valid(self):
        """Check if token is still valid."""
        return (
            self.used_at is None
            and self.expires_at > datetime.utcnow()
        )

    def __repr__(self):
        return f"<PasswordResetToken {self.token[:8]}... for user {self.user_id}>"
