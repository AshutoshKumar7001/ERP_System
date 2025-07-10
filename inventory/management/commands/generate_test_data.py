from django.core.management.base import BaseCommand
from inventory.models import Supplier, Product, PurchaseOrder, PurchaseOrderItem
from django.contrib.auth import get_user_model
from random import randint, choice
from django.utils import timezone

User = get_user_model()


class Command(BaseCommand):
    help = "Generate lots of dummy data for testing Purchase Orders, Suppliers, and Products"

    def handle(self, *args, **options):
        NUM_SUPPLIERS = 10
        NUM_PRODUCTS = 50
        NUM_POS = 30
        MAX_ITEMS_PER_PO = 5

        # Create suppliers
        suppliers = []
        for i in range(NUM_SUPPLIERS):
            supplier, _ = Supplier.objects.get_or_create(
                name=f"Supplier {i+1}",
                defaults={
                    "contact_email": f"supplier{i+1}@example.com",
                    "phone": f"999000{i+1}",
                    "address": f"{i+1} Market Road, City"
                }
            )
            suppliers.append(supplier)
        self.stdout.write(self.style.SUCCESS(f"Created {NUM_SUPPLIERS} suppliers"))

        # Create products
        products = []
        for i in range(NUM_PRODUCTS):
            product, _ = Product.objects.get_or_create(
                name=f"Product {i+1}",
                defaults={
                    "sku": f"P{i+1:04d}",
                    "price": round(randint(50, 5000) + 0.99, 2),
                    "current_stock": randint(0, 200),
                    "reorder_threshold": randint(5, 20),
                    "reorder_needed": False,
                    "description": "Sample product description."
                }
            )
            products.append(product)
        self.stdout.write(self.style.SUCCESS(f"Created {NUM_PRODUCTS} products"))

        # Create test user if not exists
        user, created = User.objects.get_or_create(username="testuser")
        if created:
            user.set_password("password")
            user.save()
            self.stdout.write(self.style.SUCCESS("Created test user 'testuser' with password 'password'"))
        else:
            self.stdout.write(self.style.SUCCESS("Using existing test user 'testuser'"))

        # Create Purchase Orders
        for i in range(NUM_POS):
            supplier = choice(suppliers)
            status = choice(["Pending", "Approved", "Partially Delivered", "Completed"])
            po = PurchaseOrder.objects.create(
                supplier=supplier,
                status=status,
                created_by=user,
                created_at=timezone.now(),
                approved_at=timezone.now() if status in ["Approved", "Partially Delivered", "Completed"] else None
            )
            num_items = randint(1, MAX_ITEMS_PER_PO)
            for _ in range(num_items):
                product = choice(products)
                ordered_qty = randint(1, 20)
                received_qty = 0
                if status in ["Partially Delivered", "Completed"]:
                    # For testing, mark some as received
                    received_qty = randint(0, ordered_qty)
                PurchaseOrderItem.objects.create(
                    purchase_order=po,
                    product=product,
                    ordered_quantity=ordered_qty,
                    received_quantity=received_qty
                )

        self.stdout.write(self.style.SUCCESS(f"Created {NUM_POS} purchase orders with line items"))
