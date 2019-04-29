from django.contrib import admin

from .models import Product, ProductFile

class ProductFileInLine(admin.TabularInline):
    model = ProductFile
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'slug']
    inlines = [ProductFileInLine,]
    class Meta:
        model = Product

# Register your models here.
admin.site.register(Product, ProductAdmin)
