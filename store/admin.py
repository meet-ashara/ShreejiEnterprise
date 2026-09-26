from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Product, ProductImage, Color, User_Activity, CustomUser, Contact, ContactMessage
from django import forms
from colorfield.widgets import ColorWidget

class ProductImageInline(admin.TabularInline):  # ✅ Allows multiple images in admin panel
    model = ProductImage
    extra = 1
    min_num = 1 

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price')  
    inlines = [ProductImageInline]

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('email', 'is_staff', 'is_superuser', 'is_active', 'date_joined')
    search_fields = ('email',)
    ordering = ('-date_joined',)
    fieldsets = (
        (None, {'fields': ('email', 'password', 'is_active')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
    )


admin.site.register(Product, ProductAdmin)

# ✅ Enhanced User_Activity display with tabular format
@admin.register(User_Activity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'logout_time')
    list_filter = ('user', 'login_time')
    search_fields = ('user__email',)
    ordering = ('-login_time',)
    list_per_page = 20  # Display 20 rows per page for better readability


admin.site.register(CustomUser, CustomUserAdmin)



# ✅ Properly registering Contact and ContactMessage models

class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at')
    search_fields = ('name', 'email', 'subject')

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'message', 'created_at')
    search_fields = ('name', 'email', 'message')

class ColorAdminForm(forms.ModelForm):
    class Meta:
        model = Color
        fields = '__all__'
        widgets = {
            'color_code': ColorWidget  # ✅ Enables color picker in admin
        }

class ColorAdmin(admin.ModelAdmin):
    form = ColorAdminForm
    list_display = ('name', 'color_code')
    search_fields = ('name',)

admin.site.register(Color, ColorAdmin)