import csv
import io
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from pydantic import ValidationError

from app.models import Product
from app.schemas import ProductCreate, ValidationError as SchemaValidationError


class CSVService:

    @staticmethod
    def parse_csv(file_content: bytes) -> List[Dict[str, Any]]:
        """
        Parses CSV file content into list of dictionaries
        
        Args:
            file_content: Raw bytes of CSV file
            
        Returns:
            List of dictionaries representing each row
        """
        content = file_content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        return list(csv_reader)

    @staticmethod
    def validate_and_store_products(
        rows: List[Dict[str, Any]], 
        db: Session
    ) -> Dict[str, Any]:
        """
        Validate CSV rows and store valid products in database
        
        Args:
            rows: List of product dictionaries from CSV
            db: Database session
            
        Returns:
            Dictionary with upload statistics and errors
        """
        valid_count = 0
        invalid_count = 0
        errors = []

        for idx, row in enumerate(rows, start=2):  # Start from 2 (header is row 1)
            try:
                # Clean and prepare data
                product_data = CSVService._prepare_product_data(row)
                
                # Validate using Pydantic schema
                product_schema = ProductCreate(**product_data)
                
                # Check if SKU already exists
                existing_product = db.query(Product).filter(
                    Product.sku == product_schema.sku
                ).first()
                
                if existing_product:
                    # Update existing product
                    for key, value in product_schema.model_dump().items():
                        setattr(existing_product, key, value)
                else:
                    # Create new product
                    product = Product(**product_schema.model_dump())
                    db.add(product)
                
                db.commit()
                valid_count += 1
                
            except ValidationError as e:
                invalid_count += 1
                error_messages = [
                    f"{err['loc'][0]}: {err['msg']}" 
                    for err in e.errors()
                ]
                errors.append({
                    "row": idx,
                    "data": row,
                    "errors": error_messages
                })
                
            except Exception as e:
                invalid_count += 1
                errors.append({
                    "row": idx,
                    "data": row,
                    "errors": [str(e)]
                })

        return {
            "total_rows": len(rows),
            "valid_rows": valid_count,
            "invalid_rows": invalid_count,
            "errors": errors
        }

    @staticmethod
    def _prepare_product_data(row: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and prepare product data from CSV row
        
        Args:
            row: Raw dictionary from CSV
            
        Returns:
            Cleaned dictionary with proper types
        """
        # Strip whitespace from all string values and convert empty strings to None for optional fields
        cleaned = {}
        for k, v in row.items():
            if isinstance(v, str):
                v = v.strip()
                # Keep empty strings as-is for required fields (will be caught by Pydantic validation)
                # Convert empty strings to None only for optional fields (color, size)
                if not v and k in ['color', 'size']:
                    cleaned[k] = None
                else:
                    cleaned[k] = v if v else v  # Keep empty string for validation
            else:
                cleaned[k] = v
        
        # Convert numeric fields
        if 'mrp' in cleaned and cleaned['mrp']:
            cleaned['mrp'] = float(cleaned['mrp'])
        if 'price' in cleaned and cleaned['price']:
            cleaned['price'] = float(cleaned['price'])
        if 'quantity' in cleaned and cleaned['quantity']:
            cleaned['quantity'] = int(cleaned['quantity'])
        
        return cleaned


class ProductService:
    """Service for product operations"""

    @staticmethod
    def get_products(
        db: Session,
        page: int = 1,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Get paginated list of products
        
        Args:
            db: Database session
            page: Page number (1-indexed)
            limit: Number of items per page
            
        Returns:
            Dictionary with total count and products
        """
        offset = (page - 1) * limit
        
        total = db.query(Product).count()
        products = db.query(Product).offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "products": products
        }

    @staticmethod
    def search_products(
        db: Session,
        brand: str = None,
        color: str = None,
        min_price: float = None,
        max_price: float = None,
        page: int = 1,
        limit: int = 10
    ) -> Dict[str, Any]:
        """
        Search and filter products
        
        Args:
            db: Database session
            brand: Filter by brand
            color: Filter by color
            min_price: Minimum price filter
            max_price: Maximum price filter
            page: Page number
            limit: Items per page
            
        Returns:
            Dictionary with filtered products
        """
        query = db.query(Product)
        
        # Apply filters
        if brand:
            query = query.filter(Product.brand.ilike(f"%{brand}%"))
        
        if color:
            query = query.filter(Product.color.ilike(f"%{color}%"))
        
        if min_price is not None:
            query = query.filter(Product.price >= min_price)
        
        if max_price is not None:
            query = query.filter(Product.price <= max_price)
        
        # Get total count and paginated results
        total = query.count()
        offset = (page - 1) * limit
        products = query.offset(offset).limit(limit).all()
        
        return {
            "total": total,
            "page": page,
            "limit": limit,
            "products": products
        }
