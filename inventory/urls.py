from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PurchaseOrderViewSet, purchase_order_list

router = DefaultRouter()
router.register(r'api/purchase-orders', PurchaseOrderViewSet, basename='purchaseorder')

urlpatterns = [
    path('', include(router.urls)),
    path('purchase-orders/', purchase_order_list, name='po_list'),
]
