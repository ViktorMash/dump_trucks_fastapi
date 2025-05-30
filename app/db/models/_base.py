from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import Column, Integer, DateTime
from sqlalchemy.sql import func


from app.config import settings
from app.db.session import Base


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=False), server_default=func.now())
    updated_at = Column(DateTime(timezone=False), onupdate=func.now())

    @hybrid_property
    def created_at_formatted(self):
        if self.created_at:
            return self.created_at.strftime(settings.date_format)
        return None

    @hybrid_property
    def updated_at_formatted(self):
        if self.updated_at:
            return self.updated_at.strftime(settings.date_format)
        return None