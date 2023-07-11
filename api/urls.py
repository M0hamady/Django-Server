from django.urls import path
from . import views

urlpatterns = [
    path('todos/', views.TodoListCreate.as_view()),
    path('todos/<int:pk>', views.TodoRetrieveUpdateDestroy.as_view()),
    path('todos/<int:pk>/complete', views.TodoToggleComplete.as_view()),
    path('signup/', views.signup,),
    path('login/', views.login,),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('users/', views.CustomUserAPIView.as_view(), name='users'),
    path('rest-auth/google/', views.GoogleLogin.as_view(), name='google_login'),
    path('rest-auth/google/register/', views.GoogleRegister.as_view(), name='google_register'),
    # path('reset-password/', views.ResetPasswordView.as_view(), name='reset-password'),
    # path('reset-password-confirm/<str:uidb64>/<str:token>/', views.ResetPasswordConfirmView.as_view(), name='reset-password-confirm'),
]
