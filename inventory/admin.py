from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Supplier, Product, PurchaseOrder, PurchaseOrderItem, InventoryTransaction

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'contact_email', 'phone']

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'sku', 'current_stock', 'reorder_threshold', 'reorder_needed']
    list_filter = ['reorder_needed']
    search_fields = ['name', 'sku']

class PurchaseOrderItemInline(admin.TabularInline):
    model = PurchaseOrderItem
    extra = 1

@admin.register(PurchaseOrder)
class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'supplier', 'status', 'created_by', 'created_at', 'approved_at']
    list_filter = ['status', 'created_at']
    search_fields = ['supplier__name']
    inlines = [PurchaseOrderItemInline]

@admin.register(InventoryTransaction)
class InventoryTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'product', 'quantity', 'timestamp', 'reference']
    list_filter = ['timestamp']

