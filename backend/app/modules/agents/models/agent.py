from sqlalchemy import Column, Integer, String, Text

from app.infrastructure.database import Base
from app.infrastructure.mixins import CreatedAtMixin


class Agent(Base, CreatedAtMixin):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    slug = Column(String(160), unique=True, nullable=False, index=True)
    industry = Column(String(160), nullable=True)
    profession = Column(String(160), nullable=True)
    system_prompt = Column(Text, nullable=False)
    source_row_no = Column(Integer, nullable=True)
