class Supplement:
    def __init__(self, id, name, description, brand_id, price):
        self.id = id
        self.name = name
        self.description = description
        self.brand_id = brand_id
        self.price = price

    def to_json(self):
        return {'id': self.id, 'name': self.name, 'description': self.description, 'brand_id': self.brand_id, 'price': self.price}