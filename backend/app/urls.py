"""
MakuUP Studio — App URL Configuration
All routes under /api/ (prefix set in makuup/urls.py)
"""
from django.urls import path
from app.auth.auth_views import login_view, logout_view, refresh_token_view
from app.views import (
    health_check,
    # Bookings
    create_booking,
    list_bookings,
    delete_booking,
    update_booking_status,
    # Portfolio
    list_portfolio,
    upload_portfolio,
    delete_portfolio_item,
    # Testimonials
    list_testimonials,
    create_testimonial,
    update_testimonial,
    delete_testimonial,
    submit_testimonial,
    list_pending_testimonials,
    approve_testimonial,
    # Payments
    create_payment_order,
    verify_payment,
)

urlpatterns = [
    # Health
    path('health/',                                 health_check,           name='health'),

    # Auth
    path('auth/login/',                             login_view,             name='auth-login'),
    path('auth/logout/',                            logout_view,            name='auth-logout'),
    path('auth/refresh/',                           refresh_token_view,     name='auth-refresh'),

    # Bookings — public
    path('bookings/create/',                        create_booking,         name='booking-create'),

    # Bookings — protected (dashboard)
    path('bookings/list/',                          list_bookings,          name='booking-list'),
    path('bookings/delete/<str:booking_id>/',       delete_booking,         name='booking-delete'),
    path('bookings/update-status/<str:booking_id>/',update_booking_status,  name='booking-update-status'),

    # Portfolio
    path('portfolio/',                              list_portfolio,         name='portfolio-list'),
    path('portfolio/upload/',                       upload_portfolio,       name='portfolio-upload'),
    path('portfolio/delete/<str:item_id>/',         delete_portfolio_item,  name='portfolio-delete'),

    # Testimonials
    path('testimonials/',                           list_testimonials,          name='testimonial-list'),
    path('testimonials/create/',                    create_testimonial,         name='testimonial-create'),
    path('testimonials/submit/',                    submit_testimonial,         name='testimonial-submit'),
    path('testimonials/pending/',                   list_pending_testimonials,  name='testimonial-pending'),
    path('testimonials/approve/<str:testi_id>/',    approve_testimonial,        name='testimonial-approve'),
    path('testimonials/update/<str:testi_id>/',     update_testimonial,         name='testimonial-update'),
    path('testimonials/delete/<str:testi_id>/',     delete_testimonial,         name='testimonial-delete'),

    # Payments
    path('payment/create-order/',                   create_payment_order,   name='payment-create'),
    path('payment/verify/',                         verify_payment,         name='payment-verify'),
]
