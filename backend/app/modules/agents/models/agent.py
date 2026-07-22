from sqlalchemy import Column, Integer, String, Text

from app.infrastructure.database import Base
from app.infrastructure.mixins import CreatedAtMixin


class Agent(Base, CreatedAtMixin):
    """An AI-agent persona: one profession, one system prompt.

    This is BOTH the public catalog item (``GET /agents``, ``GET
    /agents/{slug}``) AND the auth-scoping boundary — every ``User`` belongs
    to exactly one agent (see ``User.agent_id``), and a user provisioned
    under one agent cannot authenticate under another.
    """

    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    slug = Column(String(160), unique=True, nullable=False, index=True)
    industry = Column(String(160), nullable=True)
    profession = Column(String(160), nullable=True)
    system_prompt = Column(Text, nullable=False)
    # Row number in the source spreadsheet/catalog this persona was imported
    # from — lets the (future) seeding script re-sync without duplicating.
    source_row_no = Column(Integer, nullable=True)
