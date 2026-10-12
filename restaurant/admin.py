from django.contrib import admin
from .models import Category, MenuItem, Reservation, Order, OrderItem, Testimonial


class MenuItemInline(admin.TabularInline):
    model = MenuItem
    extra = 1
    fields = ('name', 'price', 'is_available', 'is_chef_special')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'items_count')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order', 'name')

    def items_count(self, obj):
        return obj.items.count()
    items_count.short_description = "Dishes"


@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'rating', 'is_chef_special', 'is_vegetarian', 'is_available')
    list_filter = ('category', 'is_available', 'is_chef_special', 'is_vegetarian', 'is_vegan', 'is_gluten_free')
    search_fields = ('name', 'description')
    list_editable = ('price', 'is_available', 'is_chef_special')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('booking_code', 'customer_name', 'date', 'time_slot', 'guests', 'seating_area', 'status', 'created_at')
    list_filter = ('status', 'seating_area', 'date')
    search_fields = ('booking_code', 'customer_name', 'email', 'phone')
    list_editable = ('status',)
    date_hierarchy = 'date'


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('item_name', 'price', 'quantity', 'item_subtotal')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'customer_name', 'order_type', 'total', 'status', 'created_at')
    list_filter = ('status', 'order_type', 'created_at')
    search_fields = ('order_number', 'customer_name', 'email', 'phone')
    list_editable = ('status',)
    inlines = [OrderItemInline]
    date_hierarchy = 'created_at'


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ('author_name', 'designation', 'rating', 'dish_highlight', 'is_featured')
    list_filter = ('rating', 'is_featured')
    search_fields = ('author_name', 'comment')


from .models import DishReview

@admin.register(DishReview)
class DishReviewAdmin(admin.ModelAdmin):
    list_display = ('menu_item', 'author_name', 'rating', 'headline', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_approved', 'created_at')
    search_fields = ('author_name', 'headline', 'comment', 'menu_item__name')
    list_editable = ('is_approved',)



# Custom Django Admin Site Branding
admin.site.site_header = "L'Étoile Dorée | Haute Gastronomie Admin"
admin.site.site_title = "L'Étoile Dorée Administration"
admin.site.index_title = "Restaurant Operations & Culinary Database"

