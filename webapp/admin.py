from django.contrib import admin
from .models import Category, Product, Customer, Order, Profile, Testimonial
from django.contrib.auth.models import User
# Register your models here.
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(Profile)

# combine profile info and user info
class ProfileInline(admin.StackedInline):
    model = Profile

#extend User model
class UserAdmin(admin.ModelAdmin):
    model = User
    field = ["username", "first_name", "last_name", "email"]
    inlines = [ProfileInline]

# Unregister the previous way
admin.site.unregister(User)
# Re-register the new way
admin.site.register(User, UserAdmin)
@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'rating', 'review', 'date')
    search_fields = ('name', 'review')
