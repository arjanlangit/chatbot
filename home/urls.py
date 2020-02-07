from django.urls import path
from home import views

app_name = 'home'

urlpatterns =[
    path('d2e9283344703466452c5b07d1caf6dcf1b9a1d196559ef584', views.ChatbotView.as_view(), name='webhook'),
    # path('', views.webhook, name='webhook'),

]