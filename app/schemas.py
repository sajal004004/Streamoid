from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ProductBase(BaseModel):
    """Base product schema"""
    sku: str = Field(min_length=1, description="SKU cannot be empty")
    name: str = Field(min_length=1, description="Name cannot be empty")
    brand: str = Field(min_length=1, description="Brand cannot be empty")
    color: Optional[str] = None
    size: Optional[str] = None
    mrp: float = Field(gt=0, description="MRP must be greater than 0")
    price: float = Field(gt=0, description="Price must be greater than 0")
    quantity: int = Field(ge=0, description="Quantity must be >= 0")

    @field_validator('sku', 'name', 'brand')
    @classmethod
    def validate_not_empty(cls, v, info):
        """Validate that required string fields are not empty or whitespace"""
        if not v or not v.strip():
            raise ValueError(f'{info.field_name} cannot be empty or whitespace')
        return v.strip()

    @field_validator('price')
    @classmethod
    def validate_price(cls, v, info):
        """Validate that price is less than or equal to MRP"""
        if 'mrp' in info.data and v > info.data['mrp']:
            raise ValueError('price must be less than or equal to mrp')
        return v


class ProductCreate(ProductBase):
    """Schema for creating a product"""
    pass


class ProductResponse(ProductBase):
    """Schema for product response"""
    id: int

    class Config:
        from_attributes = True


class ProductListResponse(BaseModel):
    """Schema for paginated product list response"""
    total: int
    page: int
    limit: int
    products: list[ProductResponse]


class UploadResponse(BaseModel):
    """Schema for upload response"""
    message: str
    total_rows: int
    valid_rows: int
    invalid_rows: int
    errors: list[dict]


class ValidationError(BaseModel):
    """Schema for validation error"""
    row: int
    data: dict
    errors: list[str]
