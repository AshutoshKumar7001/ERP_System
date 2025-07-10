**Inventory & Purchase Order Workflow - Project Documentation**

---

## 🌐 Overview

This project implements a simple **Purchase Order (PO) Management System** integrated with **Inventory Management**, forming a core module in an ERP Accounting System. It supports CRUD operations for POs, inventory tracking, role-based approval workflows, and stock alerts.

---

## 📂 Models (Django ORM)

### 1. Supplier

Stores details of vendors/suppliers.

* `name`: string
* `contact_email`: email
* `phone`: string
* `address`: text

### 2. Product

Manages product information and stock.

* `name`, `sku`, `price`, `description`
* `current_stock`, `reorder_threshold`, `reorder_needed`

### 3. PurchaseOrder

Tracks each PO issued to a supplier.

* `supplier`, `created_by`, `created_at`
* `status`: Pending, Approved, Partially Delivered, Completed
* `approved_at`

### 4. PurchaseOrderItem

Items within a PO (linked to Product).

* `purchase_order`, `product`, `ordered_quantity`, `received_quantity`

### 5. InventoryTransaction

Logs every inventory update.

* `product`, `quantity`, `timestamp`, `reference`

---

## 🛠️ API Endpoints (DRF ViewSet)

### Create Purchase Order

* **Endpoint**: `POST /api/purchase-orders/`
* **Access**: Authenticated users
* **Logic**: Creates a PO with status `Pending`

### Approve a Purchase Order

* **Endpoint**: `POST /api/purchase-orders/{id}/approve/`
* **Access**: Only "Manager" role
* **Logic**: Status changes to `Approved`

### Receive Goods from PO

* **Endpoint**: `POST /api/purchase-orders/{id}/receive/`
* **Logic**:

  * Updates `received_quantity`
  * If all items received: `Completed`
  * If some items received: `Partially Delivered`
  * Inventory updated
  * If stock < threshold: set `reorder_needed = True`

### List/Filter POs

* **Endpoint**: `GET /api/purchase-orders/?status=Pending`
* **Logic**: Filter by status

### Delete a PO

* **Endpoint**: `DELETE /api/purchase-orders/{id}/`
* **Access**: Only `Pending` status deletable

---

## 🔒 Business Rules

* **RBAC**: Managers can approve POs. Authenticated users can create.
* **Partial Deliveries**: Multiple `receive` calls allowed until completion.
* **Inventory Update**: Only triggered on `receive`.
* **Reorder Flag**: Auto-marked if stock < `reorder_threshold`

---

## 🎨 Frontend (Basic UI)

* Bootstrap-based Django templates
* List of POs with status filter
* "Approve" and "Receive" buttons via AJAX
