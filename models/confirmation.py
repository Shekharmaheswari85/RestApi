from db import db
from uuid import uuid4
from time import time

CONFIRMATION_EXPIRATION_DELTA = 60  # 60 seconds


class ConfirmationModel(db.Model):
    __tablename__ = "confirmations"

    id = db.Column(db.String(80), primary_key=True)
    expire_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("UserModel")

    def __init__(self, user_id: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.id = (
            uuid4().hex
        )  # universal unique identifier ~ long hash which is universally unique
        self.expire_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA
        self.confirmed = False

    @classmethod
    def find_by_id(cls, _id: str) -> "ConfirmationModel":
        return cls.query.filter_by(id=_id).first()

    @property
    def expired(self) -> bool:
        return (
            time() > self.expire_at
        )  # current time  > time when created + confirmation_delta

    def force_to_expire(self) -> None:
        if not self.expired:  # True()
            self.expire_at = int(time())
            self.save_to_db()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()