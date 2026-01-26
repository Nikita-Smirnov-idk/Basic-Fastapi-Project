import logging
import uuid

from sqlmodel import Session

from app.models.db.models import Item
from app.models.items.models import ItemCreate

logger = logging.getLogger(__name__)


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    logger.info("Item created, item_id=%s owner_id=%s", db_item.id, owner_id)
    return db_item