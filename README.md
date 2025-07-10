# Inventory & Purchase Order Workflow - Project Documentation

## 🛠️ Project Setup

**Requirements:**

* Python 3.8+
* PostgreSQL
* Django
* Django REST Framework

**Steps:**

1. Clone the repository.
2. Create a virtual environment.
3. Install dependencies with `pip install -r requirements.txt`.
4. Configure your PostgreSQL database in `settings.py`.
5. Run migrations: `python manage.py migrate`.
6. Create a superuser: `python manage.py createsuperuser`.
7. Start the development server: `python manage.py runserver`.

## 🌐 Overview

This project implements a simple Purchase Order (PO) Management System integrated with Inventory Management as part of an ERP Accounting System.

## 📂 Models

**Supplier**: Stores supplier information.

**Product**: Holds product details and stock.

**PurchaseOrder**: Records purchase orders.

**PurchaseOrderItem**: Line items per order.

**InventoryTransaction**: Logs inventory changes.

## 🛠️ API Endpoints

* Create Purchase Order: `POST /api/purchase-orders/`
* Approve Purchase Order: `POST /api/purchase-orders/{id}/approve/`
* Receive Goods: `POST /api/purchase-orders/{id}/receive/`
* List & Filter POs: `GET /api/purchase-orders/?status=`
* Delete Purchase Order: `DELETE /api/purchase-orders/{id}/`

## 🔐 Business Rules

* Only managers can approve POs.
* Inventory updates when goods are received.
* Partial deliveries update inventory incrementally.
* Reorder flags are triggered when stock falls below thresholds.

## 🎨 Frontend

Basic Django templates styled with Bootstrap. AJAX used for approving and receiving POs.
