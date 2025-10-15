# Product Catalog Management API

A robust backend service built with Python and FastAPI for managing product catalogs from CSV files. This service allows sellers to upload, validate, store, and search their product inventory efficiently.

## 🚀 Features

- **CSV Upload & Validation**: Upload product catalogs in CSV format with automatic validation
- **Data Validation**: Enforces business rules (price ≤ MRP, quantity ≥ 0, required fields)
- **RESTful APIs**: Clean and well-documented API endpoints
- **Pagination Support**: Efficient data retrieval with pagination
- **Advanced Search**: Filter products by brand, color, and price range
- **Database Storage**: SQLite database for persistent storage
- **Unit Tests**: Comprehensive test coverage
- **Docker Support**: Containerized for easy deployment

## 📋 Requirements

- Python 3.11+
- pip (Python package manager)
- Docker (optional, for containerized deployment)

## 🛠️ Installation & Setup

### Option 1: Local Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd streamoid
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # Linux/Mac
   python -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

   The API will be available at: `http://localhost:8000`

### Option 2: Docker Setup

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

   The API will be available at: `http://localhost:8000`

2. **Stop the containers**
   ```bash
   docker-compose down
   ```

## 📚 API Documentation

Once the application is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Endpoints

#### 1. Health Check
```http
GET /
```

**Response:**
```json
{
  "status": "healthy",
  "message": "Product Catalog API is running",
  "version": "1.0.0"
}
```

---

#### 2. Upload CSV
```http
POST /upload
```

Upload a CSV file containing product data.

**Request:**
- Content-Type: `multipart/form-data`
- Body: CSV file

**CSV Format:**
```csv
sku,name,brand,color,size,mrp,price,quantity
TSHIRT-RED-001,Classic Cotton T-Shirt,StreamThreads,Red,M,799,499,20
```

**Required Fields:**
- `sku`: Unique product code (string)
- `name`: Product name (string)
- `brand`: Brand name (string)
- `mrp`: Maximum Retail Price (float, must be > 0)
- `price`: Selling price (float, must be > 0 and ≤ mrp)
- `quantity`: Available quantity (integer, must be ≥ 0)

**Optional Fields:**
- `color`: Product color (string)
- `size`: Product size (string)

**Validation Rules:**
- `price` must be less than or equal to `mrp`
- `quantity` must be greater than or equal to 0
- All required fields must be present and non-empty
- Duplicate SKUs will update existing products

**Response:**
```json
{
  "message": "Successfully processed 20 out of 20 products",
  "total_rows": 20,
  "valid_rows": 20,
  "invalid_rows": 0,
  "errors": []
}
```

**Example with cURL:**
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_data/products.csv"
```
---

#### 3. List All Products
```http
GET /products?page=1&limit=10
```

Retrieve a paginated list of all products.

**Query Parameters:**
- `page` (optional): Page number, default = 1, minimum = 1
- `limit` (optional): Items per page, default = 10, minimum = 1, maximum = 100

**Response:**
```json
{
  "total": 20,
  "page": 1,
  "limit": 10,
  "products": [
    {
      "id": 1,
      "sku": "TSHIRT-RED-001",
      "name": "Classic Cotton T-Shirt",
      "brand": "StreamThreads",
      "color": "Red",
      "size": "M",
      "mrp": 799.0,
      "price": 499.0,
      "quantity": 20
    }
  ]
}
```

**Example with cURL:**
```bash
curl -X GET "http://localhost:8000/products?page=1&limit=10"
```

---

#### 4. Search Products
```http
GET /products/search?brand=StreamThreads&color=Red&minPrice=500&maxPrice=2000
```

Search and filter products based on multiple criteria.

**Query Parameters:**
- `brand` (optional): Filter by brand name (case-insensitive partial match)
- `color` (optional): Filter by color (case-insensitive partial match)
- `minPrice` (optional): Minimum price filter (inclusive)
- `maxPrice` (optional): Maximum price filter (inclusive)
- `page` (optional): Page number, default = 1
- `limit` (optional): Items per page, default = 10, maximum = 100

**Response:**
```json
{
  "total": 3,
  "page": 1,
  "limit": 10,
  "products": [
    {
      "id": 1,
      "sku": "TSHIRT-RED-001",
      "name": "Classic Cotton T-Shirt",
      "brand": "StreamThreads",
      "color": "Red",
      "size": "M",
      "mrp": 799.0,
      "price": 499.0,
      "quantity": 20
    }
  ]
}
```

**Example Searches:**

1. **Search by brand:**
   ```bash
   curl -X GET "http://localhost:8000/products/search?brand=StreamThreads"
   ```

2. **Search by color:**
   ```bash
   curl -X GET "http://localhost:8000/products/search?color=Red"
   ```

3. **Search by price range:**
   ```bash
   curl -X GET "http://localhost:8000/products/search?minPrice=500&maxPrice=2000"
   ```

4. **Combined filters:**
   ```bash
   curl -X GET "http://localhost:8000/products/search?brand=StreamThreads&color=Red&minPrice=400&maxPrice=600"
   ```

---

## 🧪 Testing

### Run Test Files
```bash
# Test CSV services
pytest tests/test_services.py -v

# Test API endpoints
pytest tests/test_api.py -v
```

### Test Coverage
The test suite includes:
- CSV parsing and validation tests
- Data validation rule tests (price ≤ MRP, quantity ≥ 0)
- Duplicate SKU handling tests
- API endpoint tests (upload, list, search)
- Pagination tests
- Filter combination tests

---

## 📁 Project Structure

```
streamoid/
├── app/
│   ├── __init__.py
│   ├── database.py        # Database configuration
│   ├── models.py          # SQLAlchemy models
│   ├── schemas.py         # Pydantic schemas
│   ├── services.py        # Business logic
│   └── routes.py          # API endpoints
├── sample_data/
│   └── products.csv       # Sample CSV file
├── tests/
│   ├── __init__.py
│   ├── conftest.py        # Test configuration
│   ├── test_services.py   # Service tests
│   └── test_api.py        # API tests
├── .dockerignore
├── .env                   # Environment variables
├── .gitignore
├── Dockerfile             # Docker image definition
├── main.py                # Application entry point
├── README.md              # This file
└── requirements.txt       # Python dependencies
```

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
DATABASE_URL=sqlite:///./products.db
```

For PostgreSQL (optional):
```env
DATABASE_URL=postgresql://user:password@localhost/dbname
```

---

## 📊 Sample Data

A sample CSV file is provided in `sample_data/products.csv` with 20 products across different categories:
- Apparel (T-shirts, Jeans, Dresses, etc.)
- Footwear (Sneakers)
- Accessories (Bags, Belts)
- Ethnic Wear (Sarees, Kurtas)

To upload the sample data:
```bash
curl -X POST "http://localhost:8000/upload" \
  -F "file=@sample_data/products.csv"
```

---

## 🎯 Example Workflow

1. **Start the server**
   ```bash
   python main.py
   ```

2. **Upload products**
   ```bash
   curl -X POST "http://localhost:8000/upload" \
     -F "file=@sample_data/products.csv"
   ```

3. **List all products**
   ```bash
   curl "http://localhost:8000/products?page=1&limit=10"
   ```

4. **Search products**
   ```bash
   # By brand
   curl "http://localhost:8000/products/search?brand=StreamThreads"
   
   # By color
   curl "http://localhost:8000/products/search?color=Red"
   
   # By price range
   curl "http://localhost:8000/products/search?minPrice=500&maxPrice=1500"
   ```

---

## 🐛 Error Handling

The API provides clear error messages for common scenarios:

### Invalid CSV Format
```json
{
  "detail": "Only CSV files are allowed"
}
```

### Validation Errors
```json
{
  "message": "Successfully processed 18 out of 20 products",
  "total_rows": 20,
  "valid_rows": 18,
  "invalid_rows": 2,
  "errors": [
    {
      "row": 5,
      "data": {"sku": "TEST-001", "price": "1200", "mrp": "1000"},
      "errors": ["price: price must be less than or equal to mrp"]
    }
  ]
}
```

### Invalid Price Range
```json
{
  "detail": "minPrice cannot be greater than maxPrice"
}
```

---

## 🚀 Deployment

### Production Considerations

1. **Use PostgreSQL for production:**
   ```env
   DATABASE_URL=postgresql://user:password@host:5432/dbname
   ```

2. **Set up proper CORS origins in `main.py`:**
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       ...
   )
   ```

3. **Use environment variables for sensitive data**

4. **Enable HTTPS in production**

5. **Set up logging and monitoring**

---

## 📝 License

This project is created as part of a technical assessment.

---

## 👨‍💻 Author

Created for Streamoid Technologies Technical Assessment

---

## 🤝 Support

For issues or questions:
1. Check the API documentation at http://localhost:8000/docs
2. Review the test cases for usage examples
3. Ensure all dependencies are properly installed

---

## ✨ Features Checklist

- ✅ CSV Upload & Parsing
- ✅ Data Validation (price ≤ MRP, quantity ≥ 0, required fields)
- ✅ Database Storage (SQLite)
- ✅ List Products API with Pagination
- ✅ Search API (brand, color, price range filters)
- ✅ Comprehensive Unit Tests
- ✅ Docker Support
- ✅ Complete API Documentation
- ✅ Error Handling
- ✅ Sample Data Included
