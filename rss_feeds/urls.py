from django.urls import path
from .views import get_rss_feed_for_symbol, store_symbols

urlpatterns = [
    path('symbols', store_symbols, name='store_symbols'),
    path('symbols/<str:symbol>', get_rss_feed_for_symbol, name='get_rss_feed_for_symbol'),
    # path('<int:pk>/', CustomerDetail.as_view(), name='retrieve-customer'),
    # path('update/<int:pk>/', CustomerUpdate.as_view(), name='update-customer'),
    # # path('delete/<int:pk>/', CustomerDelete.as_view(), name='delete-customer')
]
