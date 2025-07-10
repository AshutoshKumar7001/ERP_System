from rest_framework import serializers
from .models import PurchaseOrder, PurchaseOrderItem

class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for individual PurchaseOrderItem.
    Used to display line items in a Purchase Order.
    """
    class Meta:
        model = PurchaseOrderItem
        fields = [
            'id',                # Unique ID of the line item
            'product',           # Product reference
            'ordered_quantity',  # Quantity ordered
            'received_quantity'  # Quantity received so far
        ]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    """
    Serializer to represent PurchaseOrder in read operations (GET).
    Includes nested items and supplier name for display.
    """
    # Nested read-only list of PurchaseOrderItem
    items = PurchaseOrderItemSerializer(many=True, read_only=True)
    # Convenience field to include supplier's name directly
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'id',            # PO ID
            'supplier',      # Foreign key to Supplier
            'supplier_name', # Supplier name string
            'status',        # Current PO status
            'created_at',    # Creation timestamp
            'approved_at',   # Approval timestamp
            'items'          # List of PurchaseOrderItem
        ]


class PurchaseOrderCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating a new PurchaseOrder.
    Expects nested items data for line items.
    """
    # Accept nested item details while creating a PO
    items = PurchaseOrderItemSerializer(many=True)

    class Meta:
        model = PurchaseOrder
        fields = [
            'supplier',  # Supplier reference
            'items'      # List of items to be created with the PO
        ]

    def create(self, validated_data):
        """
        Custom creation logic:
        1. Pop 'items' from validated data.
        2. Create PurchaseOrder instance.
        3. Loop through items and create PurchaseOrderItem instances linked to the PO.
        """
        items_data = validated_data.pop('items')
        po = PurchaseOrder.objects.create(**validated_data)
        for item in items_data:
            PurchaseOrderItem.objects.create(
                purchase_order=po,
                **item
            )
        return po
