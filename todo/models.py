import calendar
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class AdminCompany(models.Model):
    name = models.CharField(max_length=100)
    # Add other fields specific to the admin company

    def __str__(self):
        return self.name

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
    def get_all_companies(self):
        return Company.objects.filter(admin_company=self)

    def get_all_employees(self):
        return Employee.objects.filter(admin_company=self)

    def get_all_tasks(self):
        return Task.objects.filter(company__admin_company=self)
class Company(models.Model):
    name = models.CharField(max_length=100)
    admin_company = models.ForeignKey(AdminCompany, on_delete=models.SET_NULL,null=True,default=1)
    # Add other fields specific to a company

    def __str__(self):
        return self.name

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def get_admin_company(self):
        return self.admin_company

    def set_admin_company(self, admin_company):
        self.admin_company = admin_company

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
    def get_all_tasks(self):
        return Task.objects.filter(company=self)
    def get_all_completed_tasks(self):
        return Task.objects.filter(company=self, completed=True)

    def get_all_non_completed_tasks(self):
        return Task.objects.filter(company=self, completed=False) 

class Section(models.Model):
    name= models.CharField( max_length=10)


    def __str__(self):
        return self.name

    def __unicode__(self):
        return 

class Employee(models.Model):
    admin_company = models.ForeignKey(AdminCompany, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add other fields specific to an employee

    def __str__(self):
        return self.user.username

    def get_admin_company(self):
        return self.admin_company

    def set_admin_company(self, admin_company):
        self.admin_company = admin_company

    def get_user(self):
        print(self.user.username)
        return self.user.username

    def set_user(self, user):
        self.user = user

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
    def get_all_tasks(self):
        return Task.objects.filter(assigned_to=self)
    def get_all_completed_tasks(self):
        return Task.objects.filter(assigned_to=self, completed=True)

    def get_all_non_completed_tasks(self):
        return Task.objects.filter(assigned_to=self, completed=False) 
    # @property
    # def count_completed_tasks_hours(self):
    #     hours = Task.objects.filter(completed =True,)

class Task(models.Model):
    title = models.CharField(max_length=100)
    memo = models.TextField(blank=True)
    created = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    duration = models.PositiveIntegerField()
    week_of_month = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(4)], null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(Employee, blank=True)
    assigned_at = models.CharField(max_length=100, null=True, choices=[(month, month) for month in calendar.month_name[1:]])

    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.assigned_to:
            self.assigned_to = datetime.datetime.now().strftime('%B')
        if not self.week_of_month:
            self.week_of_month = datetime.datetime.now().strftime('%U')
        super().save(*args, **kwargs)
    # Getter and setter methods for all fields
    def get_title(self):
        return self.title

    def set_title(self, title):
        self.title = title

    def get_memo(self):
        return self.memo

    def set_memo(self, memo):
        self.memo = memo

    def get_created(self):
        return self.created

    def set_created(self, created):
        self.created = created

    def get_completed(self):
        return self.completed

    def set_completed(self, completed):
        self.completed = completed

    def get_duration(self):
        return self.duration

    def set_duration(self, duration):
        self.duration = duration

    def get_week_of_month(self):
        return self.week_of_month

    def set_week_of_month(self, week_of_month):
        self.week_of_month = week_of_month

    def get_company(self):
        return self.company

    def set_company(self, company):
        self.company = company

    def get_assigned_to(self):
        return self.assigned_to

    def set_assigned_to(self, assigned_to):
        self.assigned_to = assigned_to

    # Additional methods for sign_to_month
    def sign_to_month(self, month):
        month.tasks.add(self)
    # Additional methods for sign_to_month
    
class TaskDuration(models.Model):
       duration = models.PositiveIntegerField()

       def __str__(self):
           return str(self.duration)