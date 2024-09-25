from django.urls import path
from authentication.views import check_authentication, RegisterView, LoginView ,CustomTokenObtainPairView

urlpatterns = [
    path('register/', RegisterView.as_view(), name="register"),
    # path('login/', LoginView.as_view(), name='login'), 
    # Uncomment the following line if you implement the custom token view
    path('login/', CustomTokenObtainPairView.as_view(), name='login_token'), 
    # path('login/token/', CustomTokenObtainPairView.as_view(), name='login_token'), 
    path('check/', check_authentication, name='check_authentication'),
    # Uncomment the following line if you implement CSRF token retrieval
    # path('csrf/', get_csrf_token, name='get_csrf_token'), 
]
