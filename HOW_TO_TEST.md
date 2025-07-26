# How to Test the Warehouse Inventory System

This guide will walk you through testing all features of the warehouse inventory management system step by step.

## Prerequisites
- Ensure the Django server is running: `python manage.py runserver`
- Access URLs:
  - **Main Application**: http://127.0.0.1:8000/
  - **Admin Panel**: http://127.0.0.1:8000/admin/
  - **API Base**: http://127.0.0.1:8000/api/

## Test Credentials
- **Username**: admin
- **Password**: Sivamanoj@1406

---

## Step 1: Add Products via Admin Panel

### 1.1 Access Admin Panel
1. Navigate to: http://127.0.0.1:8000/admin/
2. Login with credentials above
3. You should see the Django admin dashboard

### 1.2 Add Sample Products
Click **"Product Masters"** → **"Add Product Master"** and create these products:

**Product 1:**
```
Product Code: LAP001
Product Name: Dell Laptop
Description: Dell Latitude 5520 Business Laptop
Unit: pcs
Price: 75000.00
Minimum Stock: 5
Is Active: ✓ (checked)
```

**Product 2:**
```
Product Code: MOU001
Product Name: Wireless Mouse
Description: Logitech MX Master 3 Wireless Mouse
Unit: pcs
Price: 8500.00
Minimum Stock: 10
```

**Product 3:**
```
Product Code: KEL001
Product Name: Mechanical Keyboard
Description: Corsair K95 RGB Platinum
Unit: pcs
Price: 15000.00
Minimum Stock: 8
```

**Product 4:**
```
Product Code: CAB001
Product Name: USB-C Cable
Description: 2-meter USB-C to USB-A cable
Unit: pcs
Price: 800.00
Minimum Stock: 25
```

### 1.3 Verify Products
- Go to **"Product Masters"** list view
- Confirm all 4 products are created
- Note that **Current Stock** shows 0 for all (expected)

---

## Step 2: Create Stock IN Transactions

### 2.1 Initial Stock Purchase
1. Go to main dashboard: http://127.0.0.1:8000/
2. Click the green **"Stock In"** button
3. Fill out the form:

```
Transaction ID: SI-2025-001
Reference Number: PO-2025-JAN-001
Created By: admin
Remarks: Initial inventory purchase for Q1 2025

Items to Add:
Row 1:
- Product: LAP001 - Dell Laptop
- Quantity: 12
- Unit Price: 72000.00
- Batch Number: LAP-B001

Row 2 (click "Add Item"):
- Product: MOU001 - Wireless Mouse
- Quantity: 30
- Unit Price: 8200.00
- Batch Number: MOU-B001
```

4. Click **"Create Stock In Transaction"**
5. You should see a success message with transaction ID

### 2.2 Second Stock Purchase
Repeat the process with:

```
Transaction ID: SI-2025-002
Reference Number: PO-2025-JAN-002
Created By: admin
Remarks: Additional accessories purchase

Items:
Row 1:
- Product: KEL001 - Mechanical Keyboard
- Quantity: 15
- Unit Price: 14500.00

Row 2:
- Product: CAB001 - USB-C Cable
- Quantity: 50
- Unit Price: 750.00
```

### 2.3 Verify Stock IN
1. Go to dashboard: http://127.0.0.1:8000/
2. Check the summary cards:
   - **Total Products**: Should show 4
   - **Recent Transactions**: Should show your new transactions
3. Go to **Products** page: http://127.0.0.1:8000/products/
4. Verify current stock levels:
   - LAP001: 12 pcs
   - MOU001: 30 pcs
   - KEL001: 15 pcs
   - CAB001: 50 pcs

---

## Step 3: Test Stock OUT Transactions with Validation

### 3.1 Valid Stock OUT Transaction
1. From dashboard, click **"Stock Out"** (yellow button)
2. Create a valid transaction:

```
Transaction ID: SO-2025-001
Reference Number: INV-2025-001
Created By: admin
Remarks: Sale to ABC Company

Items to Remove:
Row 1:
- Product: LAP001 - Dell Laptop (Stock: 12)
- Quantity: 3
- Unit Price: 78000.00

Row 2:
- Product: MOU001 - Wireless Mouse (Stock: 30)
- Quantity: 5
- Unit Price: 9000.00
```

3. Click **"Create Stock Out Transaction"**
4. Should succeed with success message

### 3.2 Test Insufficient Stock Validation
1. Try another stock out with invalid quantities:

```
Transaction ID: SO-2025-002
Created By: admin
Remarks: Testing validation

Items:
- Product: LAP001 - Dell Laptop (Stock: 9 remaining)
- Quantity: 15  ← This should fail!
- Unit Price: 78000.00
```

2. Click **"Create Stock Out Transaction"**
3. **Expected Result**: Should show error message: 
   *"Insufficient stock for Dell Laptop. Available: 9, Requested: 15"*

### 3.3 Valid Small Stock OUT
Create a smaller valid transaction:

```
Transaction ID: SO-2025-003
Reference Number: INV-2025-002
Created By: admin

Items:
- Product: KEL001 - Mechanical Keyboard
- Quantity: 2
- Unit Price: 16000.00
```

---

## Step 4: View Real-time Dashboard Status

### 4.1 Dashboard Metrics
1. Go to dashboard: http://127.0.0.1:8000/
2. **Verify the following metrics**:
   - **Total Products**: 4
   - **Current stock levels** (should be updated):
     - LAP001: 9 pcs (12 - 3)
     - MOU001: 25 pcs (30 - 5)
     - KEL001: 13 pcs (15 - 2)
     - CAB001: 50 pcs (unchanged)

### 4.2 Stock Status Indicators
Check if products show correct status:
- **Green (In Stock)**: Products above minimum stock
- **Yellow (Low Stock)**: Products at or below minimum stock
- **Red (Out of Stock)**: Products with 0 stock

### 4.3 Low Stock Alerts
If any products are below minimum stock, they should appear in:
- **Low Stock** card on dashboard
- **Low Stock Products** alert section

---

## Step 5: Advanced Testing

### 5.1 Product Detail View
1. Go to **Products** page
2. Click the eye icon for any product
3. **Verify**:
   - Product details are correct
   - Current stock matches dashboard
   - Stock movement history shows all transactions
   - Movement types are color-coded (green for IN, yellow for OUT)

### 5.2 Transaction History
1. Go to **Transactions** page: http://127.0.0.1:8000/transactions/
2. **Test filtering**:
   - Click **"Stock In"** filter → Should show only IN transactions
   - Click **"Stock Out"** filter → Should show only OUT transactions
   - Click **"All"** → Should show all transactions
3. **Verify transaction details**:
   - Transaction IDs are correct
   - Dates are recent
   - Item counts and quantities are accurate

### 5.3 Admin Panel Integration
1. Go to admin panel: http://127.0.0.1:8000/admin/
2. **Test Product Management**:
   - Click **"Product Masters"**
   - Use search box to find products
   - Filter by "Is Active" status
3. **Test Transaction Management**:
   - Click **"Stock Transactions"**
   - Click on any transaction to see details
   - Verify inline editing of transaction details

---

## Step 6: API Testing

### 6.1 Test API Endpoints in Browser
Open these URLs to test API responses:

**Products API:**
- http://127.0.0.1:8000/api/products/
- Should return JSON list of all products with current stock

**Transactions API:**
- http://127.0.0.1:8000/api/transactions/
- Should return JSON list of all transactions with details

**Inventory Report API:**
- http://127.0.0.1:8000/api/inventory-report/
- Should return current stock status for all products

### 6.2 API Stock Movement (Advanced)
If you have a tool like Postman or curl:

**Create Stock IN via API:**
```bash
curl -X POST http://127.0.0.1:8000/api/stock-movement/ \
  -H "Content-Type: application/json" \
  -d '{
    "transaction_id": "API-IN-001",
    "transaction_type": "IN",
    "created_by": "api_test",
    "reference_number": "API-TEST-001",
    "items": [
      {
        "product_id": "1",
        "quantity": "5",
        "unit_price": "75000.00"
      }
    ]
  }'
```

---

## Expected Results Summary

After completing all tests, you should have:

✅ **4 Products created** with proper details
✅ **Stock IN transactions** increasing inventory
✅ **Stock OUT validation** preventing overselling
✅ **Real-time stock calculation** showing accurate levels
✅ **Dashboard metrics** updating automatically
✅ **Transaction history** tracking all movements
✅ **Low stock alerts** (if any products below minimum)
✅ **API endpoints** returning proper JSON responses

---

## Troubleshooting

### Common Issues:

**1. Server not running:**
- Run: `python manage.py runserver`
- Check: http://127.0.0.1:8000/

**2. Login fails:**
- Use exact credentials: admin / Sivamanoj@1406
- If forgotten, create new superuser: `python manage.py createsuperuser`

**3. Template errors:**
- All templates should be created
- Restart server if needed

**4. Stock calculation wrong:**
- Check transaction details in admin panel
- Verify transaction types (IN vs OUT)

**5. Validation not working:**
- Ensure you're testing with quantities greater than available stock
- Check error messages in red alert boxes

---

