from django.urls import path
from . import views

urlpatterns=[
  path('',views.home,name='home'),
  path('query_results.html', views.query_results, name='query_results'),
  path('add_transaction.html', views.add_transaction, name='add_transaction'),
  path('home.html', views.home, name='home'),
  path('buy_stocks.html', views.buy_stocks, name='buy_stocks')
]