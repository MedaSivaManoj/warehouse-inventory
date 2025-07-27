# Warehouse Inventory Management System

A Django-based warehouse inventory tracking system that helps manage stock movements and provides real-time inventory insights.

## Features

### Core Functionality
- **Product Management**: Add, edit, and track products with codes, names, pricing, and minimum stock levels
- **Stock Movements**: Record stock in/out transactions with proper validation
- **Real-time Inventory**: Automatic calculation of current stock levels
- **Historical Inventory**: View inventory levels as they were at any specific point in time
- **Low Stock Alerts**: Dashboard alerts for products below minimum stock levels
- **Transaction History**: Complete audit trail of all stock movements

### Technical Features
- **Clean API Design**: RESTful APIs for all operations
- **Input Validation**: Comprehensive validation for all user inputs
- **Admin Interface**: Full Django admin integration
- **Responsive UI**: Bootstrap-based modern interface
- **Database Schema**: Optimized schema with proper relationships

## Database Schema

### Tables
1. **prodmast** - Product Master
   - Stores product details (code, name, price, minimum stock)
   - Tracks product status and metadata

2. **stckmain** - Stock Transaction Main
   - Records transaction headers (ID, date, type, reference)
   - Links to transaction details

3. **stckdetail** - Stock Transaction Details
   - Stores individual product movements within transactions
   - Links products to transactions with quantities and prices

## Installation & Setup

### Prerequisites
- Python 3.8+
- Django 5.2+
- Django REST Framework

### Quick Start
1. **Install Dependencies**:
   ```bash
   pip install django djangorestframework
   ```

2. **Database Setup**:
   ```bash
   python manage.py migrate
   ```

3. **Create Admin User**:
   ```bash
   python manage.py createsuperuser
   ```

4. **Start Server**:
   ```bash
   python manage.py runserver
   ```

5. **Access Application**:
   - Main Dashboard: http://127.0.0.1:8000/
   - Admin Panel: http://127.0.0.1:8000/admin/
   - API Docs: http://127.0.0.1:8000/api/

## Usage

### Web Interface
- **Dashboard**: Overview of inventory status and recent transactions
- **Products**: Manage product catalog and view stock levels
- **Stock Operations**: Record stock in/out movements
- **Transactions**: View transaction history and details
- **Historical Inventory**: View inventory levels at any specific date in the past

### API Endpoints

#### Products
- `GET /api/products/` - List all products
- `POST /api/products/` - Create new product
- `GET /api/products/{id}/` - Get product details
- `PUT /api/products/{id}/` - Update product
- `DELETE /api/products/{id}/` - Delete product

#### Transactions
- `GET /api/transactions/` - List transactions
- `POST /api/transactions/` - Create transaction
- `GET /api/transactions/{id}/` - Get transaction details

#### Stock Operations
- `POST /api/stock-movement/` - Create stock movement
- `GET /api/inventory-report/` - Get inventory report
- `GET /api/historical-inventory/` - Get historical inventory at specific date

### API Usage Examples

#### Create Stock In Transaction
```json
POST /api/stock-movement/
{
    "transaction_id": "SI-001",
    "transaction_type": "IN",
    "created_by": "admin",
    "reference_number": "PO-12345",
    "items": [
        {
            "product_id": "1",
            "quantity": "100",
            "unit_price": "50.00"
        }
    ]
}
```

#### Create Stock Out Transaction
```json
POST /api/stock-movement/
{
    "transaction_id": "SO-001",
    "transaction_type": "OUT",
    "created_by": "admin",
    "items": [
        {
            "product_id": "1",
            "quantity": "25",
            "unit_price": "50.00"
        }
    ]
}
```

#### Get Historical Inventory
```json
GET /api/historical-inventory/?date=2025-01-15
{
    "query_date": "2025-01-15T23:59:59Z",
    "inventory_snapshot": [
        {
            "product_code": "LAP001",
            "product_name": "Dell Laptop",
            "unit": "pcs",
            "stock_at_date": 8,
            "minimum_stock": 5,
            "stock_status": "In Stock",
            "last_movement_date": "2025-01-15T10:30:00Z"
        }
    ]
}
```

## Key Features & Validations

### Input Validations
- **Product Code**: Required, unique, auto-uppercase
- **Quantities**: Must be positive integers
- **Prices**: Must be positive decimals
- **Stock Out**: Validates sufficient stock availability
- **Transaction Dates**: Cannot be in future

### Business Logic
- **Current Stock Calculation**: Real-time calculation from all transactions
- **Stock Status Tracking**: Automatic categorization (In Stock/Low Stock/Out of Stock)
- **Minimum Stock Alerts**: Dashboard notifications for low stock items
- **Transaction Integrity**: Prevents duplicate products in same transaction

### Security Features
- **CSRF Protection**: Built-in Django CSRF protection
- **Admin Authentication**: Secure admin panel access
- **Input Sanitization**: Automatic data cleaning and validation

## Project Structure
```
warehouse_inventory/
├── inventory/
│   ├── models.py          # Database models
│   ├── views.py           # Web and API views
│   ├── serializers.py     # API serializers
│   ├── admin.py           # Admin configuration
│   ├── urls.py            # URL routing
│   └── templates/         # HTML templates
├── warehouse_inventory/
│   ├── settings.py        # Django settings
│   └── urls.py            # Main URL configuration
└── manage.py              # Django management script
```

## Admin Panel Features
- **Product Management**: Full CRUD operations with search and filtering
- **Transaction Management**: View and edit transactions with inline details
- **Stock Details**: Comprehensive view of all stock movements
- **Dashboard Widgets**: Quick access to key inventory metrics

## Development Notes
- Built for legacy system integration
- Extensible architecture for future enhancements
- Clean separation of concerns
- Comprehensive error handling
- Optimized database queries

## Credentials
- **Admin Username**: admin
- **Admin Password**: Sivamanoj@1406

## Support
This is an MVP designed for a small warehouse operation. The system can be extended with additional features like:
- Barcode scanning
- Multi-warehouse support
- Advanced reporting
- Email notifications
- Mobile app integration
