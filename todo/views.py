from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render

from todo.serializers import CompanyDetailSerializer, CompanySerializer, SprintSerializer, TaskSerializer
from.models import Company, Duration, Employee, Section, Task, TaskComment, TaskDuration, TaskFeedback
import datetime
def calculate_total_duration(request):
    task_duration = None
    
    if request.method == 'POST':
        employee_id = request.POST.get('employee_id')
        company_id = request.POST.get('company_id')
        section_id = request.POST.get('section_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        
        tasks = Task.objects.all()
        
        if employee_id != "" and company_id != "":
            tasks = tasks.filter(assigned_to__id=employee_id, company__id=company_id)
        
        if section_id != "":
            tasks = tasks.filter(assigned_to__section__id=section_id)

        if start_date and end_date:
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
            duration_range = (end_date - start_date).days
            tasks_with_duration = [task for task in tasks if any(Duration.objects.filter(task=task, at=(start_date + datetime.timedelta(days=duration))).exists() for duration in range(duration_range+1))]
            tasks = tasks_with_duration
                
        total_duration = sum(task.calculate_task_durations() for task in tasks)
        task_duration = TaskDuration.objects.create(duration=total_duration)
    
    return render(request, 'calculate_total_duration.html', {'task_duration': task_duration, "companies": Company.objects.all(), "employees": Employee.objects.all(), "sections": Section.objects.all()})


from datetime import date, timedelta
from django.utils import timezone

from django.http import JsonResponse
from django.views import View

class EmployeeTaskView(APIView):
    def get(self, request, employee_uuid):
        try:
            employee = Employee.objects.get(uuid=employee_uuid)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'Employee not found'}, status=404)

        today = date.today()

        # Get daily tasks
        daily_tasks = Task.objects.filter(
            assigned_to=employee,
            date_in_dev_at__date=today
        )

        # Get weekly tasks
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        weekly_tasks = Task.objects.filter(
            assigned_to=employee,
            created__date__range=[start_of_week, end_of_week]
        )

        # Get tasks in "is_dev" status
        dev_tasks = Task.objects.filter(
            assigned_to=employee,
        )

        # Serialize tasks
        daily_tasks_data = [TaskSerializer(Task.objects.get(id = task['id'])).data for task in daily_tasks.values()]
        weekly_tasks_data = [TaskSerializer(Task.objects.get(id = task['id'])).data for task in weekly_tasks.values()]
        dev_tasks_data = [TaskSerializer(Task.objects.get(id = task['id'])).data for task in dev_tasks.values()]
        print(daily_tasks)
        response_data = {
            'daily_tasks': daily_tasks_data,
            'weekly_tasks': weekly_tasks_data,
            'employee_tasks': dev_tasks_data
        }

        return Response(response_data)
from django.middleware.csrf import get_token
    
from rest_framework.response import Response

class EmployeeTaskUpdateView(APIView):
    def post(self, request, employee_uuid):
        if 'task_uuid' not in request.data:
            return Response({'error': 'task_uuid field is required'}, status=400)
        task_uuid = request.data.get('task_uuid')
        try:
            task = Task.objects.get(uuid=task_uuid)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=404)

        try:
            employee = Employee.objects.get(uuid=employee_uuid)
        except Employee.DoesNotExist:
            return Response({'error': 'Employee not found'}, status=404)

        # Check if the employee is assigned to the task
        if employee not in task.assigned_to.all():
            return Response({'error': 'You are not assigned to this task'}, status=403)

        task_data = request.data.dict()
        for key, value in task_data.items():
            if hasattr(task, key):
                setattr(task, key, value)

        # Update task information
       
        task.save()

        # Add a comment to the task
        comment_text = request.data.get('comment')
        if comment_text:
            comment = TaskComment.objects.create(task=task, employee=employee, feedback_text=comment_text)
            
        feedback_text = request.data.get('feedback')
        if feedback_text:
            if 'company_uuid' not in request.POST:
                return JsonResponse({'error': 'company_uuid field is  required while adding feedback'}, status=400)
            company = Company.objects.get(uuid = request.data.get('company_uuid')  )
            feedback = TaskFeedback.objects.create(task=task,company =company,  feedback_text=feedback_text)
            

        return Response({"task":TaskSerializer(task).data,'message': 'Task updated successfully'})
    

    
class TaskDetailView(APIView):
    def get(self, request, employee_uuid,task_uuid):
        try:
            task = Task.objects.get(uuid=task_uuid)
        except Task.DoesNotExist:
            return JsonResponse({'error': 'Task not found'}, status=404)
        try:
            employee = Employee.objects.get(uuid=employee_uuid)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'please contact company to get your unique id or refresh it '}, status=404)
        if employee not in task.assigned_to.all():
            return JsonResponse({'error': 'you are not assigned to this task'}, status=404)
        return Response(TaskSerializer(task).data)
    
class CheckKey(APIView):
    def post(self, request,):
        is_employee = False
        is_company = False
        is_active = False
        if 'uuid' not in request.POST:
                return JsonResponse({'error': 'uuid field is  required while adding feedback'}, status=400)
        try:
            employee = Employee.objects.get(uuid = request.data.get('uuid') )
            is_employee  = True
            is_active = employee.is_active
        except Employee.DoesNotExist:
            pass
        try:
            company = Company.objects.get(uuid = request.data.get('uuid') )
            is_company  = True
            is_active = company.is_active
        except Company.DoesNotExist:
            pass
        context =  {
            'is_employee' : is_employee,
            'is_company' :is_company,
            'is_active' :is_active,
        }
        return Response(context)
class Employee_data(APIView):
    def post(self, request,employee_uuid):
        if 'uuid' not in request.POST:
                return JsonResponse({'error': 'uuid field is  required while adding feedback'}, status=400)
        try:
            employee = Employee.objects.get(uuid=employee_uuid)
            if not employee.is_active:
                return JsonResponse({'error': f'hi {employee.user.username} you are not active any more please contact CodeOcean'}, status=400)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'please contact company to get your unique id or refresh it '}, status=404)
        
        
        context =  {
            'username' : employee.user.username,
            'email' : employee.user.email,
            'team' : employee.section.name,
            'team_shortcut' : employee.section.shortcut,
            'is_active' :employee.is_active,
            'tasks_count' :employee.get_all_tasks().count(),
            'tasks_count' :employee.get_all_tasks().count(),
            'completed_tasks_count' :employee.get_all_non_completed_tasks().count(),
            'companies_worked_with_count' :len(employee.get_all_companies()),
            'future_sprints' :[SprintSerializer(name).data for name in employee.get_future_sprints()],
        }
        return Response(context)
from rest_framework import status
from django.urls import reverse
class TaskDurationAPIView(APIView):
    def post(self, request, employee_uuid):
        try:
            employee = Employee.objects.get(uuid=employee_uuid)
            if not employee.is_active:
                return JsonResponse({'error': f'hi {employee.user.username} you are not active anymore, please contact CodeOcean'}, status=400)
        except Employee.DoesNotExist:
            return JsonResponse({'error': 'please contact the company to get your unique ID or refresh it'}, status=404)
        
        if 'task_uuid' not in request.data:
            return Response({'error': 'task_uuid field is required'}, status=400)
        
        task_uuid = request.data.get('task_uuid')
        
        try:
            task = Task.objects.get(uuid=task_uuid)
        except Task.DoesNotExist:
            return Response({'error': 'Task not found'}, status=404)
        
        if task.calculate_task_completion_percentage() == 100:
            return Response({"error": "Task is already finished"}, status=status.HTTP_400_BAD_REQUEST)

        current_time = timezone.now()

        # Check if there is an ongoing duration for the user
        ongoing_duration = Duration.objects.filter(task=task, assigned_to=employee, end_time__isnull=True).last()

        if 'end_time' in request.data:
            if ongoing_duration:
                print(ongoing_duration.start_time,ongoing_duration.end_time)
                ongoing_duration.end_time = current_time
                ongoing_duration.save()

                return Response({
                "message": "last duration finished successfully",
                 "duration":ongoing_duration.uuid,
                "duration_start_time":ongoing_duration.start_time,
                "task": TaskSerializer(task).data
            }, status=status.HTTP_200_OK)
            else:
                return Response({"error": "No ongoing duration found"}, status=status.HTTP_400_BAD_REQUEST)
        
        # If there are no ongoing durations, start a new duration
        if 'start_time' in request.data and not ongoing_duration:
            start_time = request.data['start_time']
            duration = Duration.objects.create(task=task, start_time=current_time)
            duration.assigned_to.add(employee)
            
            return Response({
                "message": "New duration started successfully",
                "duration":duration.uuid,
                "duration_start_time":duration.start_time,
                "task": TaskSerializer(task).data
            }, status=status.HTTP_200_OK)
        elif 'start_time' in request.data and  ongoing_duration:
            return Response({
                "message": "you have an opened duration ",
                "duration":ongoing_duration.uuid,
                "duration_start_time":ongoing_duration.start_time,
                "task": TaskSerializer(task).data
            }, status=status.HTTP_200_OK)
        elif   ongoing_duration:
            return Response({
                "message": "you have an opened duration ",
                "duration":ongoing_duration.uuid,
                "duration_start_time":ongoing_duration.start_time,
                "task": TaskSerializer(task).data
            }, status=status.HTTP_200_OK)
        elif 'start_time'  not in request.data and not ongoing_duration:
            duration = Duration.objects.create(task=task, start_time=current_time)
            duration.assigned_to.add(employee)
            return Response({
                "message": "New duration started successfully",
                "duration":duration.uuid,
                "duration_start_time":duration.start_time,
                "task": TaskSerializer(task).data
            }, status=status.HTTP_200_OK)
#+++++++++++++++++++++++++++++++++++++++++++++++++++++
#company

class CompanyDetailView(APIView):
    def get(self, request, company_uuid,):
        try:
            company = Company.objects.get(uuid=company_uuid)
        except Company.DoesNotExist:
            return JsonResponse({'error': 'company not found'}, status=404)
        
        return Response(CompanySerializer(company).data)
    def put(self, request, company_uuid,):
        try:
            company = Company.objects.get(uuid=company_uuid)
        except Company.DoesNotExist:
            return JsonResponse({'error': 'company not found'}, status=404)
        if 'project_uuid' in request.data:
            return Response(CompanyDetailSerializer(company).data)
        else:    return JsonResponse({'error': 'project_uuid is required'}, status=404)