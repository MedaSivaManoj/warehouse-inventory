from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Sum, Q
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import ProdMast, StckMain, StckDetail
from .serializers import (
    ProdMastSerializer, StckMainSerializer, StckDetailSerializer,
    StockMovementSerializer, InventoryReportSerializer
)


# API Views
class ProdMastViewSet(viewsets.ModelViewSet):
    queryset = ProdMast.objects.all()
    serializer_class = ProdMastSerializer
    
    def get_queryset(self):
        queryset = ProdMast.objects.all()
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        return queryset
    
    @action(detail=True, methods=['get'])
    def stock_movements(self, request, pk=None):
        """Get stock movements for a specific product"""
        product = self.get_object()
        movements = StckDetail.objects.filter(product=product).select_related('stck_main')
        serializer = StckDetailSerializer(movements, many=True)
        return Response(serializer.data)


class StckMainViewSet(viewsets.ModelViewSet):
    queryset = StckMain.objects.all()
    serializer_class = StckMainSerializer
    
    def get_queryset(self):
        queryset = StckMain.objects.all()
        transaction_type = self.request.query_params.get('transaction_type')
        if transaction_type:
            queryset = queryset.filter(transaction_type=transaction_type)
        
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        if date_from:
            queryset = queryset.filter(transaction_date__gte=date_from)
        if date_to:
            queryset = queryset.filter(transaction_date__lte=date_to)
        
        return queryset


class StockMovementView(APIView):
    """API endpoint for creating stock movements"""
    
    def post(self, request):
        serializer = StockMovementSerializer(data=request.data)
        if serializer.is_valid():
            try:
                stock_main = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Stock movement created successfully',
                    'transaction_id': stock_main.transaction_id
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'success': False,
                    'message': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class InventoryReportView(APIView):
    """API endpoint for inventory reports"""
    
    def get(self, request):
        products = ProdMast.objects.filter(is_active=True)
        report_data = []
        
        for product in products:
            # Get last movement date
            last_movement = StckDetail.objects.filter(product=product).order_by('-created_at').first()
            last_movement_date = last_movement.created_at if last_movement else None
            
            # Determine stock status
            current_stock = product.current_stock
            if current_stock <= 0:
                stock_status = 'Out of Stock'
            elif current_stock <= product.minimum_stock:
                stock_status = 'Low Stock'
            else:
                stock_status = 'In Stock'
            
            report_data.append({
                'product_code': product.product_code,
                'product_name': product.product_name,
                'unit': product.unit,
                'current_stock': current_stock,
                'minimum_stock': product.minimum_stock,
                'stock_status': stock_status,
                'last_movement_date': last_movement_date
            })
        
        serializer = InventoryReportSerializer(report_data, many=True)
        return Response(serializer.data)


# Web Views
def dashboard(request):
    """Main dashboard view"""
    # Get summary statistics
    total_products = ProdMast.objects.filter(is_active=True).count()
    low_stock_products = []
    out_of_stock_products = []
    
    for product in ProdMast.objects.filter(is_active=True):
        current_stock = product.current_stock
        if current_stock <= 0:
            out_of_stock_products.append(product)
        elif current_stock <= product.minimum_stock:
            low_stock_products.append(product)
    
    recent_transactions = StckMain.objects.all()[:10]
    
    context = {
        'total_products': total_products,
        'low_stock_count': len(low_stock_products),
        'out_of_stock_count': len(out_of_stock_products),
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'inventory/dashboard.html', context)


def product_list(request):
    """Product list view"""
    products = ProdMast.objects.filter(is_active=True)
    
    # Add current stock to each product
    for product in products:
        product.stock_level = product.current_stock
    
    return render(request, 'inventory/product_list.html', {'products': products})


def product_detail(request, product_id):
    """Product detail view"""
    product = get_object_or_404(ProdMast, id=product_id)
    
    # Get stock movements for this product
    movements = StckDetail.objects.filter(product=product).select_related('stck_main').order_by('-created_at')
    
    context = {
        'product': product,
        'movements': movements,
        'current_stock': product.current_stock
    }
    
    return render(request, 'inventory/product_detail.html', context)


def stock_in_form(request):
    """Stock in form view"""
    if request.method == 'POST':
        # Process form data
        transaction_id = request.POST.get('transaction_id')
        reference_number = request.POST.get('reference_number', '')
        remarks = request.POST.get('remarks', '')
        created_by = request.POST.get('created_by')
        
        # Create transaction
        stock_main = StckMain.objects.create(
            transaction_id=transaction_id,
            transaction_date=timezone.now(),
            transaction_type='IN',
            reference_number=reference_number,
            remarks=remarks,
            created_by=created_by
        )
        
        # Process items (assuming they're passed as form data)
        product_ids = request.POST.getlist('product_id')
        quantities = request.POST.getlist('quantity')
        unit_prices = request.POST.getlist('unit_price')
        
        for i, product_id in enumerate(product_ids):
            if product_id and quantities[i] and unit_prices[i]:
                product = ProdMast.objects.get(id=product_id)
                StckDetail.objects.create(
                    stck_main=stock_main,
                    product=product,
                    quantity=int(quantities[i]),
                    unit_price=float(unit_prices[i])
                )
        
        return render(request, 'inventory/success.html', {
            'message': 'Stock in transaction created successfully',
            'transaction_id': transaction_id
        })
    
    products = ProdMast.objects.filter(is_active=True)
    return render(request, 'inventory/stock_in_form.html', {'products': products})


def stock_out_form(request):
    """Stock out form view"""
    if request.method == 'POST':
        # Similar to stock_in_form but with OUT transaction type
        # and stock validation
        transaction_id = request.POST.get('transaction_id')
        reference_number = request.POST.get('reference_number', '')
        remarks = request.POST.get('remarks', '')
        created_by = request.POST.get('created_by')
        
        # Validate stock availability first
        product_ids = request.POST.getlist('product_id')
        quantities = request.POST.getlist('quantity')
        
        errors = []
        for i, product_id in enumerate(product_ids):
            if product_id and quantities[i]:
                product = ProdMast.objects.get(id=product_id)
                requested_qty = int(quantities[i])
                current_stock = product.current_stock
                
                if requested_qty > current_stock:
                    errors.append(f"Insufficient stock for {product.product_name}. Available: {current_stock}, Requested: {requested_qty}")
        
        if errors:
            products = ProdMast.objects.filter(is_active=True)
            return render(request, 'inventory/stock_out_form.html', {
                'products': products,
                'errors': errors
            })
        
        # Create transaction
        stock_main = StckMain.objects.create(
            transaction_id=transaction_id,
            transaction_date=timezone.now(),
            transaction_type='OUT',
            reference_number=reference_number,
            remarks=remarks,
            created_by=created_by
        )
        
        # Process items
        unit_prices = request.POST.getlist('unit_price')
        
        for i, product_id in enumerate(product_ids):
            if product_id and quantities[i] and unit_prices[i]:
                product = ProdMast.objects.get(id=product_id)
                StckDetail.objects.create(
                    stck_main=stock_main,
                    product=product,
                    quantity=int(quantities[i]),
                    unit_price=float(unit_prices[i])
                )
        
        return render(request, 'inventory/success.html', {
            'message': 'Stock out transaction created successfully',
            'transaction_id': transaction_id
        })
    
    products = ProdMast.objects.filter(is_active=True)
    return render(request, 'inventory/stock_out_form.html', {'products': products})


def transaction_list(request):
    """Transaction list view"""
    transactions = StckMain.objects.all()
    
    # Filter by transaction type if provided
    transaction_type = request.GET.get('type')
    if transaction_type:
        transactions = transactions.filter(transaction_type=transaction_type)
    
    return render(request, 'inventory/transaction_list.html', {
        'transactions': transactions,
        'current_filter': transaction_type
    })
