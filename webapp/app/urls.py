from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('quiz/', views.quiz_view, name='quiz'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('logout/', views.logout_view, name='logout'),
    path('add-phone/', views.add_phone_number, name='add_phone'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('connect/<int:target_id>/', views.track_whatsapp_click, name='track_whatsapp'),
    path('metrics/', views.metrics_dashboard, name='metrics_dashboard'),
]