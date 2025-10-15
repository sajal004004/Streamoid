from sqlalchemy import Column, Integer, String, Float
from app.database import Base


class Product(Base):
    """Product model for database"""
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    brand = Column(String, index=True, nullable=False)
    color = Column(String, index=True)
    size = Column(String)
    mrp = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, nullable=False)

    def to_dict(self):
        """Convert model instance to dictionary"""
        return {
            "id": self.id,
            "sku": self.sku,
            "name": self.name,
            "brand": self.brand,
            "color": self.color,
            "size": self.size,
            "mrp": self.mrp,
            "price": self.price,
            "quantity": self.quantity
        }
