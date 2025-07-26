from rest_framework import serializers
from .models import ProdMast, StckMain, StckDetail
from django.utils import timezone


class ProdMastSerializer(serializers.ModelSerializer):
    current_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = ProdMast
        fields = '__all__'
        
    def validate_product_code(self, value):
        if not value.strip():
            raise serializers.ValidationError("Product code cannot be empty")
        return value.upper().strip()
    
    def validate_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value


class StckDetailSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.product_name', read_only=True)
    product_code = serializers.CharField(source='product.product_code', read_only=True)
    total_value = serializers.ReadOnlyField()
    
    class Meta:
        model = StckDetail
        fields = ['id', 'product', 'product_name', 'product_code', 'quantity', 
                 'unit_price', 'total_value', 'batch_number', 'expiry_date', 'remarks']
    
    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value
    
    def validate_unit_price(self, value):
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than 0")
        return value


class StckMainSerializer(serializers.ModelSerializer):
    details = StckDetailSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_quantity = serializers.ReadOnlyField()
    
    class Meta:
        model = StckMain
        fields = '__all__'
    
    def validate_transaction_id(self, value):
        if not value.strip():
            raise serializers.ValidationError("Transaction ID cannot be empty")
        return value.upper().strip()
    
    def validate_transaction_date(self, value):
        if value > timezone.now():
            raise serializers.ValidationError("Transaction date cannot be in the future")
        return value


class StockMovementSerializer(serializers.Serializer):
    """Serializer for creating stock movements (IN/OUT transactions)"""
    transaction_id = serializers.CharField(max_length=50)
    transaction_type = serializers.ChoiceField(choices=[('IN', 'Stock In'), ('OUT', 'Stock Out')])
    transaction_date = serializers.DateTimeField(default=timezone.now)
    reference_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    remarks = serializers.CharField(required=False, allow_blank=True)
    created_by = serializers.CharField(max_length=100)
    
    # Product details
    items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField()
        ),
        write_only=True
    )
    
    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError("At least one item is required")
        
        for item in value:
            required_fields = ['product_id', 'quantity', 'unit_price']
            for field in required_fields:
                if field not in item:
                    raise serializers.ValidationError(f"'{field}' is required for each item")
            
            try:
                quantity = int(item['quantity'])
                if quantity <= 0:
                    raise serializers.ValidationError("Quantity must be greater than 0")
            except ValueError:
                raise serializers.ValidationError("Quantity must be a valid number")
            
            try:
                unit_price = float(item['unit_price'])
                if unit_price <= 0:
                    raise serializers.ValidationError("Unit price must be greater than 0")
            except ValueError:
                raise serializers.ValidationError("Unit price must be a valid number")
        
        return value
    
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        
        # Create main transaction
        stock_main = StckMain.objects.create(**validated_data)
        
        # Create detail records
        for item_data in items_data:
            try:
                product = ProdMast.objects.get(id=item_data['product_id'])
            except ProdMast.DoesNotExist:
                raise serializers.ValidationError(f"Product with ID {item_data['product_id']} not found")
            
            # For OUT transactions, check stock availability
            if validated_data['transaction_type'] == 'OUT':
                current_stock = product.current_stock
                requested_qty = int(item_data['quantity'])
                if requested_qty > current_stock:
                    raise serializers.ValidationError(
                        f"Insufficient stock for {product.product_name}. "
                        f"Available: {current_stock}, Requested: {requested_qty}"
                    )
            
            StckDetail.objects.create(
                stck_main=stock_main,
                product=product,
                quantity=int(item_data['quantity']),
                unit_price=float(item_data['unit_price']),
                batch_number=item_data.get('batch_number', ''),
                expiry_date=item_data.get('expiry_date'),
                remarks=item_data.get('remarks', '')
            )
        
        return stock_main


class InventoryReportSerializer(serializers.Serializer):
    """Serializer for inventory report"""
    product_code = serializers.CharField()
    product_name = serializers.CharField()
    unit = serializers.CharField()
    current_stock = serializers.IntegerField()
    minimum_stock = serializers.IntegerField()
    stock_status = serializers.CharField()
    last_movement_date = serializers.DateTimeField()
