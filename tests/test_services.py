import pytest
from app.services import CSVService
from app.models import Product


class TestCSVService:
    """Test cases for CSV parsing and validation"""

    def test_parse_csv_valid(self):
        """Test parsing a valid CSV file"""
        csv_content = b"""sku,name,brand,color,size,mrp,price,quantity
TEST-001,Test Product,TestBrand,Red,M,1000,800,10"""
        
        rows = CSVService.parse_csv(csv_content)
        
        assert len(rows) == 1
        assert rows[0]['sku'] == 'TEST-001'
        assert rows[0]['name'] == 'Test Product'
        assert rows[0]['brand'] == 'TestBrand'

    def test_parse_csv_empty(self):
        """Test parsing an empty CSV (header only)"""
        csv_content = b"""sku,name,brand,color,size,mrp,price,quantity"""
        
        rows = CSVService.parse_csv(csv_content)
        
        assert len(rows) == 0

    def test_validate_price_less_than_mrp(self, db_session):
        """Test validation passes when price <= mrp"""
        rows = [{
            'sku': 'TEST-001',
            'name': 'Test Product',
            'brand': 'TestBrand',
            'color': 'Red',
            'size': 'M',
            'mrp': '1000',
            'price': '800',
            'quantity': '10'
        }]
        
        result = CSVService.validate_and_store_products(rows, db_session)
        
        assert result['valid_rows'] == 1
        assert result['invalid_rows'] == 0
        assert len(result['errors']) == 0

    def test_validate_price_greater_than_mrp(self, db_session):
        """Test validation fails when price > mrp"""
        rows = [{
            'sku': 'TEST-002',
            'name': 'Test Product',
            'brand': 'TestBrand',
            'color': 'Red',
            'size': 'M',
            'mrp': '800',
            'price': '1000',
            'quantity': '10'
        }]
        
        result = CSVService.validate_and_store_products(rows, db_session)
        
        assert result['valid_rows'] == 0
        assert result['invalid_rows'] == 1
        assert len(result['errors']) == 1
        assert 'price' in result['errors'][0]['errors'][0].lower()

    def test_validate_negative_quantity(self, db_session):
        """Test validation fails when quantity < 0"""
        rows = [{
            'sku': 'TEST-003',
            'name': 'Test Product',
            'brand': 'TestBrand',
            'color': 'Red',
            'size': 'M',
            'mrp': '1000',
            'price': '800',
            'quantity': '-5'
        }]
        
        result = CSVService.validate_and_store_products(rows, db_session)
        
        assert result['valid_rows'] == 0
        assert result['invalid_rows'] == 1
        assert len(result['errors']) == 1

    def test_validate_missing_required_fields(self, db_session):
        """Test validation fails when required fields are missing"""
        rows = [{
            'sku': '',
            'name': 'Test Product',
            'brand': '',
            'color': 'Red',
            'size': 'M',
            'mrp': '1000',
            'price': '800',
            'quantity': '10'
        }]
        
        result = CSVService.validate_and_store_products(rows, db_session)
        
        assert result['invalid_rows'] == 1
        assert len(result['errors']) == 1

    def test_validate_zero_quantity_allowed(self, db_session):
        """Test validation passes when quantity = 0"""
        rows = [{
            'sku': 'TEST-004',
            'name': 'Test Product',
            'brand': 'TestBrand',
            'color': 'Red',
            'size': 'M',
            'mrp': '1000',
            'price': '800',
            'quantity': '0'
        }]
        
        result = CSVService.validate_and_store_products(rows, db_session)
        
        assert result['valid_rows'] == 1
        assert result['invalid_rows'] == 0

    def test_duplicate_sku_updates_product(self, db_session):
        """Test that duplicate SKU updates existing product"""
        rows1 = [{
            'sku': 'TEST-005',
            'name': 'Test Product',
            'brand': 'TestBrand',
            'color': 'Red',
            'size': 'M',
            'mrp': '1000',
            'price': '800',
            'quantity': '10'
        }]
        
        rows2 = [{
            'sku': 'TEST-005',
            'name': 'Updated Product',
            'brand': 'TestBrand',
            'color': 'Blue',
            'size': 'L',
            'mrp': '1200',
            'price': '900',
            'quantity': '15'
        }]
        
        # First upload
        result1 = CSVService.validate_and_store_products(rows1, db_session)
        assert result1['valid_rows'] == 1
        
        # Second upload with same SKU
        result2 = CSVService.validate_and_store_products(rows2, db_session)
        assert result2['valid_rows'] == 1
        
        # Verify product was updated
        product = db_session.query(Product).filter(Product.sku == 'TEST-005').first()
        assert product.name == 'Updated Product'
        assert product.color == 'Blue'
        assert product.quantity == 15
        
        # Verify only one product exists
        count = db_session.query(Product).filter(Product.sku == 'TEST-005').count()
        assert count == 1
