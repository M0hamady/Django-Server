from django.urls import path
from .views import (
    CheckKey,
    CompanyDetailView,
    Employee_data,
    TaskDurationAPIView,
    calculate_total_duration,
    EmployeeTaskView,
    EmployeeTaskUpdateView,
    TaskDetailView,
)

urlpatterns = [
    path('calculate-total-duration/', calculate_total_duration, name='calculate_total_duration'),
    path('employee/<uuid:employee_uuid>/tasks/', EmployeeTaskView.as_view(), name='employee_tasks'),
    path('employee/check/', CheckKey.as_view(), name='employee_Check'),
    path('employee/<uuid:employee_uuid>/data/', Employee_data.as_view(), name='employee_Check'),
    path('task/<uuid:employee_uuid>/add-comment/', EmployeeTaskUpdateView.as_view(), name='add_comment_to_task'),
    path('task/<uuid:employee_uuid>/duration/', TaskDurationAPIView.as_view(), name='duration_of_task'),
    # path('task/<int:task_id>/update/', EmployeeTaskUpdateView.as_view(), name='employee_task_update'),
    path('task/<uuid:task_uuid>/<uuid:employee_uuid>/', TaskDetailView.as_view(), name='task_detail'),
    path('company/<uuid:company_uuid>/detail/', CompanyDetailView.as_view(), name='company_detail'),
    # path('company/<uuid:company_uuid>/', CompanyDetailView.as_view(), name='company_detail'),
]