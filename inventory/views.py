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
    Handles CRUD operations and custom actions for Purchase Orders.
    """
    queryset = PurchaseOrder.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return PurchaseOrderCreateSerializer
        return PurchaseOrderSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        status_param = self.request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        return queryset

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
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
        po = self.get_object()
        if po.status not in ['Approved', 'Partially Delivered']:
            return Response({'error': 'Cannot receive goods for this PO status.'}, status=400)

        received_items = request.data.get('items', [])
        all_received = True

        for item_data in received_items:
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

            # Update received quantity
            item.received_quantity += qty
            item.save()

            # Update inventory
            product = item.product
            product.current_stock += qty
            product.save()

            # Log transaction
            InventoryTransaction.objects.create(
                product=product,
                quantity=qty,
                reference=f"PO #{po.id} Receipt"
            )

            # Update reorder flag
            if product.current_stock < product.reorder_threshold:
                product.reorder_needed = True
                product.save()
            else:
                product.reorder_needed = False
                product.save()

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
        po = self.get_object()
        if po.status != 'Pending':
            return Response({'error': 'Only Pending POs can be deleted.'}, status=400)
        return super().destroy(request, *args, **kwargs)


# HTML view for displaying Purchase Orders
def purchase_order_list(request):
    """
    Renders a Bootstrap table with Purchase Orders.
    """
    pos = PurchaseOrder.objects.all().select_related('supplier')
    return render(request, 'inventory/po_list.html', {'purchase_orders': pos})
