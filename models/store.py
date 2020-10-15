from db import db


class StoreModel(db.Model):
    __tablename__ = "stores"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(90))
    items = db.relationship("ItemModel", lazy="dynamic")

    def __init__(self, name):
        self.name = name

    def json(self):
        return {"name": self.name, "items": [item.json() for item in self.items.all()]}
        # if we are not having a big amount of data  in our database then we can go
        # for self.item relationship as it will return all the item with the same store.id but it
        # can cause problem in case when we have a lot of data in our database
        # and it could slow down our whole process thats why we use lazy='dynamic' so
        # that our system couldn't computationally slow down

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
