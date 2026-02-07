from sqlmodel import Session

from app.domain.entities.db.user import Item
from app.transport.schemas import ItemCreate
from tests.utils.user import create_random_user
from tests.utils.utils import random_lower_string


def create_random_item(db: Session) -> Item:
    user = create_random_user(db)
    owner_id = user.id
    assert owner_id is not None
    title = random_lower_string()
    description = random_lower_string()
    item = Item.model_validate(
        ItemCreate(title=title, description=description),
        update={"owner_id": owner_id},
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item
