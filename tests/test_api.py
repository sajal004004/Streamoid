import pytest
import io
from app.models import Product


class TestProductAPI:
    """Test cases for product API endpoints"""

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"

    def test_upload_csv_valid(self, client):
        """Test uploading a valid CSV file"""
        csv_content = """sku,name,brand,color,size,mrp,price,quantity
TEST-001,Test Product,TestBrand,Red,M,1000,800,10
TEST-002,Test Product 2,TestBrand,Blue,L,1200,900,5"""
        
        files = {
            'file': ('products.csv', io.BytesIO(csv_content.encode()), 'text/csv')
        }
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data['total_rows'] == 2
        assert data['valid_rows'] == 2
        assert data['invalid_rows'] == 0

    def test_upload_csv_with_invalid_rows(self, client):
        """Test uploading CSV with some invalid rows"""
        csv_content = """sku,name,brand,color,size,mrp,price,quantity
TEST-001,Test Product,TestBrand,Red,M,1000,800,10
TEST-002,Test Product 2,TestBrand,Blue,L,800,1200,5
TEST-003,Test Product 3,TestBrand,Green,S,1500,1000,-5"""
        
        files = {
            'file': ('products.csv', io.BytesIO(csv_content.encode()), 'text/csv')
        }
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert data['total_rows'] == 3
        assert data['valid_rows'] == 1
        assert data['invalid_rows'] == 2
        assert len(data['errors']) == 2

    def test_upload_non_csv_file(self, client):
        """Test uploading a non-CSV file"""
        files = {
            'file': ('test.txt', io.BytesIO(b'not a csv'), 'text/plain')
        }
        
        response = client.post("/upload", files=files)
        
        assert response.status_code == 400
        assert "Only CSV files are allowed" in response.json()['detail']

    def test_list_products_empty(self, client):
        """Test listing products when database is empty"""
        response = client.get("/products")
        
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 0
        assert data['page'] == 1
        assert data['limit'] == 10
        assert len(data['products']) == 0

    def test_list_products_with_data(self, client, db_session):
        """Test listing products with data"""
        # Add test products
        products = [
            Product(sku=f'TEST-00{i}', name=f'Product {i}', brand='TestBrand',
                   color='Red', size='M', mrp=1000, price=800, quantity=10)
            for i in range(1, 6)
        ]
        for p in products:
            db_session.add(p)
        db_session.commit()
        
        response = client.get("/products")
        
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 5
        assert len(data['products']) == 5

    def test_list_products_pagination(self, client, db_session):
        """Test product listing with pagination"""
        # Add test products
        products = [
            Product(sku=f'TEST-00{i}', name=f'Product {i}', brand='TestBrand',
                   color='Red', size='M', mrp=1000, price=800, quantity=10)
            for i in range(1, 16)
        ]
        for p in products:
            db_session.add(p)
        db_session.commit()
        
        # Get first page
        response = client.get("/products?page=1&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 15
        assert data['page'] == 1
        assert data['limit'] == 5
        assert len(data['products']) == 5
        
        # Get second page
        response = client.get("/products?page=2&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert data['page'] == 2
        assert len(data['products']) == 5

    def test_search_by_brand(self, client, db_session):
        """Test searching products by brand"""
        products = [
            Product(sku='TEST-001', name='Product 1', brand='BrandA',
                   color='Red', size='M', mrp=1000, price=800, quantity=10),
            Product(sku='TEST-002', name='Product 2', brand='BrandB',
                   color='Blue', size='L', mrp=1200, price=900, quantity=5),
            Product(sku='TEST-003', name='Product 3', brand='BrandA',
                   color='Green', size='S', mrp=1500, price=1000, quantity=8),
        ]
        for p in products:
            db_session.add(p)
        db_session.commit()
        
        response = client.get("/products/search?brand=BrandA")
        
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 2
        assert len(data['products']) == 2
        assert all(p['brand'] == 'BrandA' for p in data['products'])

    def test_search_by_color(self, client, db_session):
        """Test searching products by color"""
        products = [
            Product(sku='TEST-001', name='Product 1', brand='BrandA',
                   color='Red', size='M', mrp=1000, price=800, quantity=10),
            Product(sku='TEST-002', name='Product 2', brand='BrandB',
                   color='Blue', size='L', mrp=1200, price=900, quantity=5),
            Product(sku='TEST-003', name='Product 3', brand='BrandA',
                   color='Red', size='S', mrp=1500, price=1000, quantity=8),
        ]
        for p in products:
            db_session.add(p)
        db_session.commit()
        
        response = client.get("/products/search?color=Red")
        
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 2
        assert all(p['color'] == 'Red' for p in data['products'])

    def test_search_by_price_range(self, client, db_session):
        """Test searching products by price range"""
        products = [
            Product(sku='TEST-001', name='Product 1', brand='BrandA',
                   color='Red', size='M', mrp=1000, price=500, quantity=10),
            Product(sku='TEST-002', name='Product 2', brand='BrandB',
                   color='Blue', size='L', mrp=1200, price=1000, quantity=5),
            Product(sku='TEST-003', name='Product 3', brand='BrandA',
                   color='Green', size='S', mrp=2000, price=1500, quantity=8),
        ]
        for p in products:
            db_session.add(p)
        db_session.commit()
        
        response = client.get("/products/search?minPrice=600&maxPrice=1200")
        
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 1
        assert data['products'][0]['price'] == 1000

    def test_search_multiple_filters(self, client, db_session):
        """Test searching with multiple filters"""
        products = [
            Product(sku='TEST-001', name='Product 1', brand='BrandA',
                   color='Red', size='M', mrp=1000, price=800, quantity=10),
            Product(sku='TEST-002', name='Product 2', brand='BrandA',
                   color='Blue', size='L', mrp=1200, price=900, quantity=5),
            Product(sku='TEST-003', name='Product 3', brand='BrandB',
                   color='Red', size='S', mrp=1500, price=850, quantity=8),
        ]
        for p in products:
            db_session.add(p)
        db_session.commit()
        
        response = client.get("/products/search?brand=BrandA&color=Red&minPrice=500&maxPrice=900")
        
        assert response.status_code == 200
        data = response.json()
        assert data['total'] == 1
        assert data['products'][0]['sku'] == 'TEST-001'

    def test_search_invalid_price_range(self, client):
        """Test search with invalid price range (min > max)"""
        response = client.get("/products/search?minPrice=1000&maxPrice=500")
        
        assert response.status_code == 400
        assert "minPrice cannot be greater than maxPrice" in response.json()['detail']
