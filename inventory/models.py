from django.db import models
from django.contrib.auth import get_user_model

# Get the User model
User = get_user_model()

# Supplier model stores vendor information
class Supplier(models.Model):
    # Name of the supplier
    name = models.CharField(max_length=255)
    # Contact email address
    contact_email = models.EmailField()
    # Optional phone number
    phone = models.CharField(max_length=20, blank=True)
    # Optional physical address
    address = models.TextField(blank=True)

    def __str__(self):
        return self.name

# Product model stores items that can be ordered and stocked
class Product(models.Model):
    # Product name
    name = models.CharField(max_length=255)
    # Optional description
    description = models.TextField(blank=True)
    # Unique Stock Keeping Unit identifier
    sku = models.CharField(max_length=50, unique=True)
    # Price per unit
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Current stock quantity in inventory
    current_stock = models.IntegerField(default=0)
    # Threshold below which reordering is needed
    reorder_threshold = models.IntegerField(default=5)
    # Flag indicating if reordering is necessary
    reorder_needed = models.BooleanField(default=False)

    def __str__(self):
        return self.name

# PurchaseOrder model represents an order sent to a supplier
class PurchaseOrder(models.Model):
    # Status options for the purchase order
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Partially Delivered', 'Partially Delivered'),
        ('Completed', 'Completed'),
    ]
    # Supplier linked to this purchase order
    supplier = models.ForeignKey(Supplier, on_delete=models.CASCADE)
    # User who created the purchase order
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    # Current status of the purchase order
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    # Timestamp when the purchase order was created
    created_at = models.DateTimeField(auto_now_add=True)
    # Timestamp when the purchase order was approved
    approved_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'PO #{self.id} - {self.supplier.name}'

# PurchaseOrderItem model stores line items for each purchase order
class PurchaseOrderItem(models.Model):
    # The related purchase order
    purchase_order = models.ForeignKey(PurchaseOrder, related_name='items', on_delete=models.CASCADE)
    # The product being ordered
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # Quantity ordered for this item
    ordered_quantity = models.IntegerField()
    # Quantity received so far
    received_quantity = models.IntegerField(default=0)

# InventoryTransaction logs any inventory updates
class InventoryTransaction(models.Model):
    # The product whose stock was updated
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # Quantity added (positive) or removed (negative)
    quantity = models.IntegerField()
    # Timestamp when the transaction was recorded
    timestamp = models.DateTimeField(auto_now_add=True)
    # Reference or note (e.g., "PO #7 Receipt")
    reference = models.CharField(max_length=255)
