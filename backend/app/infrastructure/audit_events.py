from sqlalchemy import event
from sqlalchemy.orm import Mapper

from app.core.user_context import current_agent_id, current_user_id
from app.infrastructure.database import Base


@event.listens_for(Base, "before_insert", propagate=True)
def before_insert(mapper: Mapper, connection, target):
    if hasattr(target, "created_by"):
        uid = current_user_id.get()
        if uid:
            target.created_by = uid
            target.updated_by = uid

    if hasattr(target, "agent_id") and target.agent_id is None:
        aid = current_agent_id.get()
        if aid:
            target.agent_id = aid


@event.listens_for(Base, "before_update", propagate=True)
def before_update(mapper: Mapper, connection, target):
    if hasattr(target, "updated_by"):
        uid = current_user_id.get()
        if uid:
            target.updated_by = uid
