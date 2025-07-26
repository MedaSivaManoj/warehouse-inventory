from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class ProdMast(models.Model):
    """Product Master - stores the details of the products"""
    product_code = models.CharField(max_length=50, unique=True, help_text="Unique product code")
    product_name = models.CharField(max_length=200, help_text="Product name")
    description = models.TextField(blank=True, help_text="Product description")
    unit = models.CharField(max_length=20, help_text="Unit of measurement (kg, pcs, etc.)")
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Unit price"
    )
    minimum_stock = models.PositiveIntegerField(default=0, help_text="Minimum stock level")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'prodmast'
        verbose_name = 'Product Master'
        verbose_name_plural = 'Product Masters'

    def __str__(self):
        return f"{self.product_code} - {self.product_name}"

    @property
    def current_stock(self):
        """Calculate current stock from all transactions"""
        from django.db.models import Sum
        stock_in = StckDetail.objects.filter(
            product=self,
            stck_main__transaction_type='IN'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        stock_out = StckDetail.objects.filter(
            product=self,
            stck_main__transaction_type='OUT'
        ).aggregate(total=Sum('quantity'))['total'] or 0
        
        return stock_in - stock_out


class StckMain(models.Model):
    """Stock Main - stores the transaction details"""
    TRANSACTION_TYPES = [
        ('IN', 'Stock In'),
        ('OUT', 'Stock Out'),
        ('ADJ', 'Adjustment'),
    ]
    
    transaction_id = models.CharField(max_length=50, unique=True, help_text="Unique transaction ID")
    transaction_date = models.DateTimeField(help_text="Transaction date and time")
    transaction_type = models.CharField(
        max_length=3, 
        choices=TRANSACTION_TYPES,
        help_text="Type of transaction"
    )
    reference_number = models.CharField(max_length=100, blank=True, help_text="Reference number (PO, Invoice, etc.)")
    remarks = models.TextField(blank=True, help_text="Additional remarks")
    created_by = models.CharField(max_length=100, help_text="User who created the transaction")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stckmain'
        verbose_name = 'Stock Transaction'
        verbose_name_plural = 'Stock Transactions'
        ordering = ['-transaction_date']

    def __str__(self):
        return f"{self.transaction_id} - {self.get_transaction_type_display()}"

    @property
    def total_items(self):
        """Get total number of items in this transaction"""
        return self.details.count()

    @property
    def total_quantity(self):
        """Get total quantity in this transaction"""
        from django.db.models import Sum
        return self.details.aggregate(total=Sum('quantity'))['total'] or 0


class StckDetail(models.Model):
    """Stock Detail - stores the details of the products within each transaction"""
    stck_main = models.ForeignKey(
        StckMain, 
        on_delete=models.CASCADE, 
        related_name='details',
        help_text="Reference to main transaction"
    )
    product = models.ForeignKey(
        ProdMast, 
        on_delete=models.CASCADE, 
        related_name='stock_movements',
        help_text="Product involved in transaction"
    )
    quantity = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Quantity moved"
    )
    unit_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Unit price at time of transaction"
    )
    batch_number = models.CharField(max_length=50, blank=True, help_text="Batch/Lot number")
    expiry_date = models.DateField(null=True, blank=True, help_text="Expiry date if applicable")
    remarks = models.TextField(blank=True, help_text="Item-specific remarks")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'stckdetail'
        verbose_name = 'Stock Detail'
        verbose_name_plural = 'Stock Details'
        unique_together = ['stck_main', 'product']  # Prevent duplicate products in same transaction

    def __str__(self):
        return f"{self.product.product_code} - {self.quantity} {self.product.unit}"

    @property
    def total_value(self):
        """Calculate total value of this line item"""
        return self.quantity * self.unit_price

    def clean(self):
        """Custom validation"""
        from django.core.exceptions import ValidationError
        
        # For stock out transactions, check if enough stock is available
        if self.stck_main.transaction_type == 'OUT':
            current_stock = self.product.current_stock
            if self.quantity > current_stock:
                raise ValidationError(
                    f'Insufficient stock for {self.product.product_name}. '
                    f'Available: {current_stock}, Requested: {self.quantity}'
                )
