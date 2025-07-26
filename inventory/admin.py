from django.contrib import admin
from .models import ProdMast, StckMain, StckDetail


@admin.register(ProdMast)
class ProdMastAdmin(admin.ModelAdmin):
    list_display = ['product_code', 'product_name', 'unit', 'price', 'current_stock', 'minimum_stock', 'is_active']
    list_filter = ['is_active', 'unit', 'created_at']
    search_fields = ['product_code', 'product_name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'current_stock']
    fieldsets = (
        ('Basic Information', {
            'fields': ('product_code', 'product_name', 'description', 'unit')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'minimum_stock', 'current_stock')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


class StckDetailInline(admin.TabularInline):
    model = StckDetail
    extra = 1
    fields = ['product', 'quantity', 'unit_price', 'batch_number', 'expiry_date', 'remarks']


@admin.register(StckMain)
class StckMainAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'transaction_date', 'transaction_type', 'total_items', 'total_quantity', 'created_by']
    list_filter = ['transaction_type', 'transaction_date', 'created_by']
    search_fields = ['transaction_id', 'reference_number', 'remarks']
    readonly_fields = ['created_at', 'updated_at', 'total_items', 'total_quantity']
    inlines = [StckDetailInline]
    date_hierarchy = 'transaction_date'
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('transaction_id', 'transaction_date', 'transaction_type', 'reference_number')
        }),
        ('Details', {
            'fields': ('remarks', 'created_by')
        }),
        ('Summary', {
            'fields': ('total_items', 'total_quantity'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StckDetail)
class StckDetailAdmin(admin.ModelAdmin):
    list_display = ['stck_main', 'product', 'quantity', 'unit_price', 'total_value', 'batch_number']
    list_filter = ['stck_main__transaction_type', 'product', 'expiry_date']
    search_fields = ['product__product_name', 'product__product_code', 'batch_number']
    readonly_fields = ['total_value', 'created_at']
    
    def total_value(self, obj):
        return f"₹{obj.total_value:,.2f}"
    total_value.short_description = 'Total Value'
