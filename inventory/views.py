from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.shortcuts import render
from .models import PurchaseOrder, PurchaseOrderItem, InventoryTransaction, Product
from .serializers import PurchaseOrderSerializer, PurchaseOrderCreateSerializer

class PurchaseOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Purchase Orders.
    Provides:
    - CRUD operations (list, create, retrieve, update, delete)
    - Custom actions for approving and receiving orders.
    """
    queryset = PurchaseOrder.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """
        Return different serializers depending on action:
        - create: PurchaseOrderCreateSerializer (expects nested items)
        - others: PurchaseOrderSerializer (read representation)
        """
        if self.action == 'create':
            return PurchaseOrderCreateSerializer
        return PurchaseOrderSerializer

    def get_queryset(self):
        """
        Optionally filter purchase orders by status via query param:
        Example: /api/purchase-orders/?status=Pending
        """
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    def perform_create(self, serializer):
        """
        When creating a purchase order, set created_by to current user.
        """
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """
        Custom action to approve a PO.
        Business Rules:
        - Only users in 'Manager' group can approve.
        - Only POs with status 'Pending' can be approved.
        """
        po = self.get_object()
        if not request.user.groups.filter(name='Manager').exists():
            return Response({'error': 'Only Managers can approve POs.'}, status=403)
        if po.status != 'Pending':
            return Response({'error': 'Only Pending POs can be approved.'}, status=400)

        po.status = 'Approved'
        po.approved_at = timezone.now()
        po.save()
        return Response({'status': 'PO approved.'})

    @action(detail=True, methods=['post'])
    def receive(self, request, pk=None):
        """
        Custom action to receive goods for a PO.
        Business Rules:
        - Only 'Approved' or 'Partially Delivered' POs can receive goods.
        - Each received item quantity must be positive and <= remaining quantity.
        - Updates inventory stock and logs InventoryTransaction.
        - Sets PO status to Completed or Partially Delivered.
        - Updates reorder flag based on new stock levels.
        """
        po = self.get_object()
        if po.status not in ['Approved', 'Partially Delivered']:
            return Response({'error': 'Cannot receive goods for this PO status.'}, status=400)

        received_items = request.data.get('items', [])
        all_received = True  # Flag to track if all items are fulfilled

        for item_data in received_items:
            # Find corresponding PurchaseOrderItem
            try:
                item = po.items.get(id=item_data['id'])
            except PurchaseOrderItem.DoesNotExist:
                return Response({'error': f"Item ID {item_data['id']} not found in this PO."}, status=404)

            qty = item_data['received_quantity']
            if qty <= 0:
                return Response({'error': 'Received quantity must be positive.'}, status=400)

            remaining_qty = item.ordered_quantity - item.received_quantity
            if qty > remaining_qty:
                return Response({'error': f"Cannot receive more than remaining quantity ({remaining_qty})."}, status=400)

            # Update item received quantity
            item.received_quantity += qty
            item.save()

            # Increment inventory
            product = item.product
            product.current_stock += qty
            product.save()

            # Log inventory transaction
            InventoryTransaction.objects.create(
                product=product,
                quantity=qty,
                reference=f"PO #{po.id} Receipt"
            )

            # Update reorder flag
            if product.current_stock < product.reorder_threshold:
                product.reorder_needed = True
            else:
                product.reorder_needed = False
            product.save()

            # If any item not fully received, mark PO as partially delivered
            if item.received_quantity < item.ordered_quantity:
                all_received = False

        # Update PO status
        if all_received:
            po.status = 'Completed'
        else:
            po.status = 'Partially Delivered'
        po.save()

        return Response({'status': f'PO marked as {po.status}.'})

    def destroy(self, request, *args, **kwargs):
        """
        Override delete to enforce business rule:
        - Only POs with status 'Pending' can be deleted.
        """
        po = self.get_object()
        if po.status != 'Pending':
            return Response({'error': 'Only Pending POs can be deleted.'}, status=400)
        return super().destroy(request, *args, **kwargs)


# HTML view to display Purchase Orders with Bootstrap table
def purchase_order_list(request):
    """
    Renders a simple HTML template showing all Purchase Orders.
    Used for basic UI/testing.
    """
    pos = PurchaseOrder.objects.all().select_related('supplier')
    return render(request, 'inventory/po_list.html', {'purchase_orders': pos})
