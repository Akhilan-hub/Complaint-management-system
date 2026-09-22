from django.urls import path
from . import views

urlpatterns = [
    # Authentication
    path('', views.login_view, name='root'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # User Routes
    path('dashboard/', views.user_dashboard_view, name='user_dashboard'),
    path('complaint/submit/', views.submit_complaint_view, name='submit_complaint'),
    path('complaints/my/', views.my_complaints_view, name='my_complaints'),
    path('complaint/<int:pk>/', views.complaint_detail_view, name='complaint_detail'),
    path('complaint/<int:pk>/delete/', views.delete_complaint_view, name='delete_complaint'),
    path('complaints/bulk-delete/', views.bulk_delete_complaints_view, name='bulk_delete_complaints'),

    # Admin Routes
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
    path('admin/complaint/<int:pk>/', views.admin_complaint_detail_view, name='admin_complaint_detail'),
    path('admin/complaint/<int:pk>/take/', views.admin_take_complaint_view, name='admin_take_complaint'),
    path('admin/complaint/<int:pk>/submit-resolution/', views.admin_submit_resolution_view, name='admin_submit_resolution'),
    path('admin/complaint/<int:pk>/resolve/', views.admin_resolve_complaint_view, name='admin_resolve_complaint'),
    path('admin/complaint/<int:pk>/manual-confirm/', views.admin_manual_confirm_view, name='admin_manual_confirm'),
]
