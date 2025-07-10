from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PurchaseOrderViewSet, purchase_order_list

# Create a DRF router to automatically generate REST API routes
router = DefaultRouter()

# Register the PurchaseOrderViewSet under the prefix 'api/purchase-orders'
# This will generate routes like:
#   GET    /api/purchase-orders/            List all POs
#   POST   /api/purchase-orders/            Create a new PO
#   GET    /api/purchase-orders/{id}/       Retrieve a PO
#   PUT    /api/purchase-orders/{id}/       Update a PO
#   DELETE /api/purchase-orders/{id}/       Delete a PO
#   POST   /api/purchase-orders/{id}/approve/   Custom action to approve
#   POST   /api/purchase-orders/{id}/receive/   Custom action to receive goods
router.register(
    r'api/purchase-orders',
    PurchaseOrderViewSet,
    basename='purchaseorder'
)

# Define URL patterns for this app
urlpatterns = [
    # Include the automatically generated DRF API URLs
    path('', include(router.urls)),

    # HTML page for viewing purchase orders in a Bootstrap table
    # Accessible via: /purchase-orders/
    path('purchase-orders/', purchase_order_list, name='po_list'),
]
