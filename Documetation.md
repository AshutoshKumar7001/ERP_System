---

# 📘 **Inventory & Purchase Order Workflow - Project Documentation**

---

## 🌐 **Overview**

This project implements a **Purchase Order (PO) Management System** integrated with **Inventory Management**, forming a core module in an ERP Accounting System.
It supports:

✅ CRUD operations for POs and suppliers
✅ Inventory tracking and automatic updates
✅ Role-based approval workflows
✅ Reorder threshold alerts

---

## 📂 **Models (Django ORM)**

### 🏷️ 1. **Supplier**

Stores vendor details.

* `name`: string
* `contact_email`: email
* `phone`: string
* `address`: text

---

### 📦 2. **Product**

Manages product information and stock.

* `name`, `sku`, `price`, `description`
* `current_stock`: current inventory quantity
* `reorder_threshold`: trigger level for reordering
* `reorder_needed`: flag for low stock

---

### 🧾 3. **PurchaseOrder**

Tracks POs issued to suppliers.

* `supplier`: FK to Supplier
* `created_by`: FK to User
* `status`: `Pending` | `Approved` | `Partially Delivered` | `Completed`
* `created_at`: timestamp
* `approved_at`: timestamp (nullable)

---

### 📄 4. **PurchaseOrderItem**

Individual line items in a PO.

* `purchase_order`: FK
* `product`: FK
* `ordered_quantity`
* `received_quantity`

---

### 📝 5. **InventoryTransaction**

Logs stock adjustments.

* `product`: FK
* `quantity`: +/- quantity
* `timestamp`
* `reference`: description (e.g., `PO #5 Receipt`)

---

## 🛠️ **API Endpoints (Django REST Framework)**

Below are the main REST endpoints:

---

### 🔗 **Supplier API**

* `GET /api/suppliers/`
* `POST /api/suppliers/`
* `PUT /api/suppliers/{id}/`
* `DELETE /api/suppliers/{id}/`

---

### 📦 **Product API**

* `GET /api/products/`
* `POST /api/products/`

---

### 🧾 **Purchase Order API**

#### ✏️ Create Purchase Order

* **Endpoint:** `POST /api/purchase-orders/`
* **Access:** Any authenticated user
* **Logic:** Creates PO with `Pending` status

---

#### ✅ Approve a Purchase Order

* **Endpoint:** `POST /api/purchase-orders/{id}/approve/`
* **Access:** Only users in `Manager` role
* **Logic:** Status updated to `Approved`

---

#### 📥 Receive Goods

* **Endpoint:** `POST /api/purchase-orders/{id}/receive/`
* **Logic:**

  * Updates `received_quantity`
  * Marks as `Completed` if all received
  * Marks as `Partially Delivered` if partially received
  * Updates inventory
  * Sets `reorder_needed = True` if stock below threshold

---

#### 📄 List & Filter POs

* **Endpoint:** `GET /api/purchase-orders/?status=Pending`
* **Logic:** Filter by status query param

---

#### 🗑️ Delete a PO

* **Endpoint:** `DELETE /api/purchase-orders/{id}/`
* **Access:** Only `Pending` POs can be deleted

---

## 🔒 **Business Rules**

* ✅ **RBAC:** Only Managers can approve POs
* ✅ **Partial Deliveries:** Multiple receipts allowed
* ✅ **Inventory Update:** Only on `receive`
* ✅ **Reorder Flag:** Auto-trigger when below threshold

---

## 🎨 **Frontend (Basic UI)**

* Django Templates with **Bootstrap**
* Table listing all POs with status filters
* **Approve** and **Receive Goods** buttons using jQuery AJAX calls

---

## 🚀 **How to Run**

1. **Install dependencies**

   ```
   pip install -r requirements.txt
   ```
2. **Migrate DB**

   ```
   python manage.py makemigrations
   python manage.py migrate
   ```
3. **Create superuser**

   ```
   python manage.py createsuperuser
   ```
4. **Run server**

   ```
   python manage.py runserver
   ```

---

✅ **Tip:** You can extend this with:

* Swagger/OpenAPI documentation
* Email notifications
* Docker deployment
* Celery tasks for auto-reordering
