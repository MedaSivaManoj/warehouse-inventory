from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# API router
router = DefaultRouter()
router.register(r'products', views.ProdMastViewSet)
router.register(r'transactions', views.StckMainViewSet)

app_name = 'inventory'

urlpatterns = [
    # Web views
    path('', views.dashboard, name='dashboard'),
    path('products/', views.product_list, name='product_list'),
    path('products/<int:product_id>/', views.product_detail, name='product_detail'),
    path('stock-in/', views.stock_in_form, name='stock_in_form'),
    path('stock-out/', views.stock_out_form, name='stock_out_form'),
    path('transactions/', views.transaction_list, name='transaction_list'),
    path('historical-inventory/', views.historical_inventory, name='historical_inventory'),
    
    # API endpoints
    path('api/', include(router.urls)),
    path('api/stock-movement/', views.StockMovementView.as_view(), name='stock_movement_api'),
    path('api/inventory-report/', views.InventoryReportView.as_view(), name='inventory_report_api'),
    path('api/historical-inventory/', views.HistoricalInventoryView.as_view(), name='historical_inventory_api'),
]
