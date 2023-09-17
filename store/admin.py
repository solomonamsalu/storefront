from typing import Any, List, Optional, Tuple
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from .models import *
from django.db.models import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse

class InventoryFilter(admin.SimpleListFilter):
    title='inventory'
    parameter_name='inventroy'

    def lookups(self, request,model_admin):
        return [
            ('<10','Low')
        ]
    def queryset(self, request, queryset:QuerySet):
        if self.value()=='<10':
            return queryset.filter(inventory__lt=10)
        

class ProductImageInLine(admin.TabularInline):
    model=ProductImage
    readonly_fields=['thumbnail']

    def thumbnail(self,instance):
        if instance.image.name!='':
            return format_html(f'<img src="{instance.image.url}" class="thumbnail" />')
                                  
        return ''
    
@admin.register(Product)
class ProductAdmmin(admin.ModelAdmin):
    prepopulated_fields={
        'slug':['title']
    }
    autocomplete_fields=['collection']
    actions=['clear_inventory']
    inlines=[ProductImageInLine]
    list_display=['title','price','collection_title']
    list_editable=['price']
    list_filter=['collection','last_update',InventoryFilter]
    list_per_page=10
    list_select_related=['collection']
    search_fields=['title']

    def collection_title(self,product):
        return product.collection.title
    @admin.action(description="Clear inventory")
    def clear_inventory(self,request,queryset):
        updated_count=queryset.update(inventory=0)
        self.message_user(
            request,
            f'{updated_count} product were successfully updated'
        )
    class Media:
        css= {
            'all': ['store/styles.css']
            }


@admin.register(Collection)
class ColloctionAdmin(admin.ModelAdmin):
    list_display=['title','products_count']  
    search_fields=['title']
    @admin.display(ordering='products_count')
    def products_count(self,collection):
        url=(reverse('admin:store_product_changelist')+'?'+urlencode({'collection_id':str (collection.id)}))
        return format_html('<a href="{}">{}</a>',url,collection.products_count)
    
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(
            products_count=Count('product')
        )

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display=['first_name','last_name','membership']
    list_editable=['membership']
    list_select_related=['user']
    ordering=['user__first_name','user__last_name']
    list_per_page=10
    search_fields=['first_name','last_name']

class OrderItemInline(admin.TabularInline):
       autocomplete_fields=['product']
       model=OrderItem

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display=['id','placed_at','customer']
    autocomplete_fields=['customer']
    inlines=[OrderItemInline]
@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display=['order','product','quantity','unit_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display=['id']


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display=['id','product','quantity']



# Register your models here.
