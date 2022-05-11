from django.urls import path
from .views import store_rss_feed_from_source, store_new_symbols

urlpatterns = [
    path('symbols', store_new_symbols, name='store_symbols'),
    path('symbols/<str:symbol>', store_rss_feed_from_source, name='store_feeds'),
    # path('<int:pk>/', CustomerDetail.as_view(), name='retrieve-customer'),
    # path('update/<int:pk>/', CustomerUpdate.as_view(), name='update-customer'),
    # # path('delete/<int:pk>/', CustomerDelete.as_view(), name='delete-customer')
]
