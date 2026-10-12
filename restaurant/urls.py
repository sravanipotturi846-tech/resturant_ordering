from django.urls import path
from . import views

app_name = 'restaurant'

urlpatterns = [
    path('', views.home, name='home'),
    path('api/menu/', views.menu_api, name='menu_api'),
    path('api/reserve/', views.reserve_table, name='reserve_table'),
    path('api/order/', views.place_order, name='place_order'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('api/update-status/', views.update_status, name='update_status'),
    path('order/<str:order_number>/receipt/', views.receipt_view, name='receipt_view'),
    
    # Customer Authentication & Profile
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),

    # Dish Reviews & Ratings
    path('api/dish/<int:item_id>/reviews/', views.dish_reviews_api, name='dish_reviews_api'),
    path('api/dish/review/submit/', views.submit_dish_review, name='submit_dish_review'),
]
