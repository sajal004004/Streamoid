from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services import CSVService, ProductService
from app.schemas import UploadResponse, ProductListResponse, ProductResponse

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a CSV file with product data.
    
    The CSV should have the following columns:
    - sku (required): Unique product code
    - name (required): Product title
    - brand (required): Brand name
    - color (optional): Product color
    - size (optional): Product size
    - mrp (required): Maximum Retail Price (must be > 0)
    - price (required): Selling price (must be > 0 and <= mrp)
    - quantity (required): Available quantity (must be >= 0)
    
    Returns:
        Statistics about the upload including valid/invalid rows and errors
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=400,
            detail="Only CSV files are allowed"
        )
    
    try:
        # Read file content
        content = await file.read()
        
        # Parse CSV
        rows = CSVService.parse_csv(content)
        
        if not rows:
            raise HTTPException(
                status_code=400,
                detail="CSV file is empty or has no data rows"
            )
        
        # Validate and store products
        result = CSVService.validate_and_store_products(rows, db)
        
        return {
            "message": f"Successfully processed {result['valid_rows']} out of {result['total_rows']} products",
            **result
        }
        
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail="Invalid CSV file encoding. Please use UTF-8 encoding"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing CSV file: {str(e)}"
        )


@router.get("/products", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1, description="Page number (starting from 1)"),
    limit: int = Query(10, ge=1, le=100, description="Items per page (max 100)"),
    db: Session = Depends(get_db)
):
    """
    Get a paginated list of all products.
    
    Args:
        page: Page number (default: 1)
        limit: Number of items per page (default: 10, max: 100)
    
    Returns:
        Paginated list of products with total count
    """
    result = ProductService.get_products(db, page=page, limit=limit)
    return result


@router.get("/products/search", response_model=ProductListResponse)
def search_products(
    brand: Optional[str] = Query(None, description="Filter by brand name"),
    color: Optional[str] = Query(None, description="Filter by color"),
    minPrice: Optional[float] = Query(None, ge=0, description="Minimum price"),
    maxPrice: Optional[float] = Query(None, ge=0, description="Maximum price"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Search and filter products.
    
    Args:
        brand: Filter by brand name (case-insensitive partial match)
        color: Filter by color (case-insensitive partial match)
        minPrice: Minimum price filter
        maxPrice: Maximum price filter
        page: Page number (default: 1)
        limit: Items per page (default: 10, max: 100)
    
    Returns:
        Filtered and paginated list of products
    """
    # Validate price range
    if minPrice is not None and maxPrice is not None and minPrice > maxPrice:
        raise HTTPException(
            status_code=400,
            detail="minPrice cannot be greater than maxPrice"
        )
    
    result = ProductService.search_products(
        db,
        brand=brand,
        color=color,
        min_price=minPrice,
        max_price=maxPrice,
        page=page,
        limit=limit
    )
    
    return result
