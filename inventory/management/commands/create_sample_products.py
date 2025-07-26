from django.core.management.base import BaseCommand
from inventory.models import ProdMast


class Command(BaseCommand):
    help = 'Create sample products for testing the warehouse inventory system'

    def handle(self, *args, **options):
        # Sample products data
        sample_products = [
            {
                'product_code': 'LAP001',
                'product_name': 'Dell Laptop',
                'description': 'Dell Latitude 5520 Business Laptop',
                'unit': 'pcs',
                'price': 75000.00,
                'minimum_stock': 5,
                'is_active': True,
            },
            {
                'product_code': 'MOU001',
                'product_name': 'Wireless Mouse',
                'description': 'Logitech MX Master 3 Wireless Mouse',
                'unit': 'pcs',
                'price': 8500.00,
                'minimum_stock': 10,
                'is_active': True,
            },
            {
                'product_code': 'KEL001',
                'product_name': 'Mechanical Keyboard',
                'description': 'Corsair K95 RGB Platinum',
                'unit': 'pcs',
                'price': 15000.00,
                'minimum_stock': 8,
                'is_active': True,
            },
            {
                'product_code': 'CAB001',
                'product_name': 'USB-C Cable',
                'description': '2-meter USB-C to USB-A cable',
                'unit': 'pcs',
                'price': 800.00,
                'minimum_stock': 25,
                'is_active': True,
            }
        ]

        self.stdout.write(self.style.SUCCESS('Creating sample products...'))
        
        created_count = 0
        updated_count = 0
        
        for product_data in sample_products:
            product, created = ProdMast.objects.get_or_create(
                product_code=product_data['product_code'],
                defaults=product_data
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Created: {product.product_code} - {product.product_name}')
                )
            else:
                # Update existing product
                for key, value in product_data.items():
                    setattr(product, key, value)
                product.save()
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'⟳ Updated: {product.product_code} - {product.product_name}')
                )
        
        self.stdout.write('\n' + '='*60)
        self.stdout.write(self.style.SUCCESS(f'✅ SUMMARY:'))
        self.stdout.write(self.style.SUCCESS(f'   Products created: {created_count}'))
        self.stdout.write(self.style.SUCCESS(f'   Products updated: {updated_count}'))
        self.stdout.write(self.style.SUCCESS(f'   Total products: {ProdMast.objects.count()}'))
        self.stdout.write('='*60)
        
        # Show current stock status
        self.stdout.write(self.style.SUCCESS('\n📦 CURRENT INVENTORY STATUS:'))
        for product in ProdMast.objects.filter(is_active=True):
            current_stock = product.current_stock
            status = "🔴 Out of Stock" if current_stock <= 0 else "🟡 Low Stock" if current_stock <= product.minimum_stock else "🟢 In Stock"
            
            self.stdout.write(
                f'   {product.product_code}: {current_stock} {product.unit} - {status}'
            )
        
        self.stdout.write('\n' + self.style.SUCCESS('🎉 Sample products are ready!'))
        self.stdout.write(self.style.SUCCESS('💡 Next steps:'))
        self.stdout.write('   1. Go to: http://127.0.0.1:8000/products/')
        self.stdout.write('   2. Or admin panel: http://127.0.0.1:8000/admin/inventory/prodmast/')
        self.stdout.write('   3. Create some stock IN transactions to add inventory')
