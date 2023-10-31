import calendar
import datetime
import uuid 
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

class AdminCompany(models.Model):
    name = models.CharField(max_length=100)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    # Add other fields specific to the admin company

    def __str__(self):
        return self.name

    def get_name(self):
        return self.name

    def set_name(self, name):
        self.name = name

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
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
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    
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
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
    def get_all_tasks(self):
        return Task.objects.filter(company=self)
   
    def get_all_completed_tasks(self):
        return Task.objects.filter(company=self, completed=True)

    def get_all_non_completed_tasks(self):
        return Task.objects.filter(company=self, completed=False) 
class Project(models.Model):
    name = models.CharField(max_length=100)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.name
    @property
    def road_map(self):
        # months
        # weeks
        # days
        # actions
        all_items = RoadMapItem.objects.filter(project=self).values()
        res = []
        for item in  all_items:
            sprints = RoadMapItem.objects.get(id = item['id']).sprint.values()
            new_sprints = []
            for sprint in sprints:
                new_start_date = datetime.datetime.strptime(str(sprint['start_date']), "%Y-%m-%d")
                sprint['week_number_in_month'] =(new_start_date.day - 1) // 7 + 1
                sprint['week_number_in_year'] =new_start_date.isocalendar()[1]
                sprint['day_name'] =new_start_date.strftime("%A")
                new_tasks = []
                tasks = Task.objects.filter(sprints = sprint['id']).values('id')
                for task in tasks:
                    task = Task.objects.get(id= task['id'])
                    FeedBacks = TaskFeedback.objects.filter(task=task).values("uuid","feedback_text","created_at")
                    new_task = {
                        "title":task.title,
                        "descriptions":task.memo,
                        "percentage":task.calculate_task_completion_percentage(),
                        "FeedBacks":FeedBacks,
                        "uuid":task.uuid,
                    }
                    new_tasks.append(new_task)
                meetings= Meeting.objects.filter(sprint=sprint['id']).values('start_time','end_time','meeting_link')
                new_meetings = []
                for meeting in meetings:
                    date = meeting["start_time"]
                    # start_time = datetime.datetime.strptime(str(date), "%Y-%m-%dT%H:%M:%S")

                    time = date.strftime("%H:%M:%S")
                    day_name = date.strftime("%A")
                    day_date = date.strftime("%Y-%m-%d")
                    meeting['time'] =time
                    meeting['day_name'] =day_name
                    meeting['day_date'] =day_date
                    new_meetings.append(meeting)
                sprint['tasks'] = new_tasks
                sprint['meetings'] = meetings
                new_sprints.append(sprint)
            item["sprints"] = new_sprints
            res.append(item)

        return res

    @property
    def get_percentage(self):
        total_conditions = RoadMapItem.objects.filter(project=self).all().count()
        completed_conditions  = 0
        # print(total_conditions)
        for sprint in RoadMapItem.objects.filter(project=self).all():
            if float(sprint.get_percentage()) > 90:
                completed_conditions += 1
            else:
              completed_conditions += float(sprint.get_percentage())/100
        return  "{:.2f}".format((completed_conditions / total_conditions) * 100 )

    # def is_finished(self):
    #     return self.sprints.filter(task__is_finished=False).count() == 0
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
class RoadMapItem(models.Model):
    name = models.CharField( max_length=50,null=True,blank=True)
    description = models.TextField( null=True,blank=True)
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    sprint = models.ManyToManyField('Sprint')
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
# starts while first sprint starts and ends while last sprint ends
    
    def __str__(self):
        return f"{self.project} - {self.name}"#- {self.get_finished_tasks_percentage()}%"
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super(RoadMapItem, self).save(*args, **kwargs)
    @property
    def get_percentage(self):
        total_conditions = self.sprint.all().count()
        completed_conditions  = 0
        # print(total_conditions)
        for sprint in self.sprint.all():
            if float(sprint.get_percentage()) > 90:
                completed_conditions += 1
            else:
              completed_conditions += float(sprint.get_percentage())/100
        return  "{:.2f}".format((completed_conditions / total_conditions) * 100 )
    def get_percentage(self):
        total_conditions = self.sprint.all().count()
        completed_conditions  = 0
        # print(total_conditions)
        for sprint in self.sprint.all():
            if float(sprint.get_percentage()) > 90:
                completed_conditions += 1
            else:
              completed_conditions += float(sprint.get_percentage())/100
        return  "{:.2f}".format((completed_conditions / total_conditions) * 100 )

    # def get_finished_tasks_percentage(self):
    #     total_tasks = self.tasks.count()
    #     finished_tasks = self.tasks.filter(is_finished=True).count()
    #     return finished_tasks / total_tasks * 100

class Section(models.Model):
    name= models.CharField( max_length=15)
    shortcut = models.CharField( max_length=5,null=True,blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        self.shortcut = "".join([word[0] for word in self.name.title().split(" ")])
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super(Section, self).save(*args, **kwargs)
    def __unicode__(self):
        return 
from django.utils import timezone
class Employee(models.Model):
    admin_company = models.ForeignKey(AdminCompany, on_delete=models.CASCADE)
    section = models.ForeignKey(Section, on_delete=models.SET_NULL,null=True,blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_active = models.BooleanField(default=True)
    # Add other fields specific to an employee

    def __str__(self):
        return self.user.username

    def get_admin_company(self):
        return self.admin_company

    def set_admin_company(self, admin_company):
        self.admin_company = admin_company
    def get_future_sprints(self):
        current_date = timezone.now().date()
        future_sprints = Sprint.objects.filter(employee = self, start_date__gte=current_date)
        return future_sprints
    def get_user(self):
        print(self.user.username)
        return self.user.username

    def set_user(self, user):
        self.user = user

    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
    def get_all_tasks(self):
        return Task.objects.filter(assigned_to=self)
    def get_all_companies(self):
        tasks = Task.objects.filter(assigned_to=self).values()
        companies = []
        for task in tasks:
            if task['company_id'] not in companies:
                companies.append(task['company_id'])
        return companies
        return Task.objects.filter(assigned_to=self)
    def get_all_completed_tasks(self):
        return Task.objects.filter(assigned_to=self, completed=True)

    def get_all_non_completed_tasks(self):
        return Task.objects.filter(assigned_to=self, completed=True) 
    # @property
    # def count_completed_tasks_hours(self):
    #     hours = Task.objects.filter(completed =True,)


class Duration(models.Model):
    duration = models.PositiveIntegerField(default=0)
    week_of_month = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(4)], null=True)
    assigned_to = models.ManyToManyField(Employee, blank=True)
    task  = models.ForeignKey("Task",  on_delete=models.CASCADE,null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    at = models.DateField(auto_now=False, auto_now_add=False,null=True, blank=True)
    start_time = models.DateTimeField(null=True,blank=True)
    end_time = models.DateTimeField(null=True,blank=True)
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.task.title
    def calculate_duration(self):
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            return float("{:.2f}".format(duration.total_seconds()/60/60))
        return 0
    # def clean(self):  
        # print(self,555555555555555,self.end_time,self.start_time)
        # print(self,555555555555555,self.as)
        # try:
        #     if self.start_time and self.end_time and self.assigned_to.exists():
        #         overlapping_durations = Duration.objects.filter(
        #             assigned_to__in=self.assigned_to.all(),
        #             start_time__lt=self.end_time,
        #             end_time__gt=self.start_time,
        #         ).exclude(pk=self.pk)

        #         if overlapping_durations.exists():
        #             raise ValidationError("There is an overlapping task with the same assigned employee in same time.")
        # except:raise ValidationError("There is an overlapping task with the same assigned employee in same time.")
    

class Task(models.Model):
    title = models.CharField(max_length=100)
    memo = models.TextField(blank=True)
    sprints = models.ManyToManyField('Sprint', related_name='tasks_sprints')
    created = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    assigned_to = models.ManyToManyField(Employee, blank=True)
    assigned_at = models.CharField(max_length=100, null=True, choices=[(month, month) for month in calendar.month_name[1:]])
    is_viewed = models.BooleanField(default=False)
    date_viewed_at = models.DateTimeField(null=True,blank=True)
    is_in_dev = models.BooleanField(default=False)
    date_in_dev_at = models.DateTimeField(null=True,blank=True)
    is_processing = models.BooleanField(default=False)
    date_processing_at = models.DateTimeField(null=True,blank=True)
    is_testing = models.BooleanField(default=False)
    date_testing_at = models.DateTimeField(null=True,blank=True)
    is_reviewed = models.BooleanField(default=False)
    date_reviewed_at = models.DateTimeField(null=True,blank=True)
    is_finished = models.BooleanField(default=False)
    date_finished_at = models.DateTimeField(null=True,blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.title
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        
        if not self.assigned_at:
            self.assigned_at = datetime.datetime.now().strftime('%B')
        
        super().save(*args, **kwargs)
    def calculate_task_durations(self):
        durations = Duration.objects.filter(task=self)
        total_duration = sum(duration.calculate_duration() for duration in durations)
        return total_duration
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
    def is_any_opened_feedback(self):
        completed_conditions  = 0
        for feed in TaskFeedback.objects.filter(task= self):
            if feed.is_viewed :
                completed_conditions += 1
            if feed.is_in_dev:
                completed_conditions += 1
            if feed.is_processing:
                completed_conditions += 1
            if feed.is_testing:
                completed_conditions += 1
            if feed.is_reviewed:
                completed_conditions += 1
            if feed.is_finished:
                completed_conditions += 1 
        return completed_conditions
# Additional methods for sign_to_month
    def calculate_task_completion_percentage(self):
        total_conditions = 9
        completed_conditions = 0
        if self.is_viewed:
            completed_conditions += 1
        if self.is_in_dev:
            completed_conditions += 1
        if self.is_processing:
            completed_conditions += 1
        if self.is_testing:
            completed_conditions += 1
        if self.is_reviewed:
            completed_conditions += 1
        if self.is_finished:
            completed_conditions += 1
        if self.completed:
            completed_conditions += 1
        if self.is_any_opened_feedback() > 0:
            if self.is_any_opened_feedback() <=3:
                completed_conditions += 1
            elif self.is_any_opened_feedback() >3:
                completed_conditions += 2
        elif self.is_any_opened_feedback() == 0:
            completed_conditions += 2
        return "{:.2f}".format((completed_conditions / total_conditions) * 100 )
        
class TaskDuration(models.Model):
    duration = models.PositiveIntegerField()
    start_time = models.DateTimeField(null=True,blank=True)
    end_time = models.DateTimeField(null=True,blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return str(self.duration) + str(self.calculate_duration)
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
    def calculate_duration(self):
        if self.start_time and self.end_time:
            duration = self.end_time - self.start_time
            return duration.total_seconds()
        return 0
       
class TaskComment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    def __str__(self):
        return self.task.title
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
class TaskFeedback(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_viewed = models.BooleanField(default=False)
    date_viewed_at = models.DateTimeField(null=True, blank=True)
    is_in_dev = models.BooleanField(default=False)
    date_in_dev_at = models.DateTimeField(null=True, blank=True)
    is_processing = models.BooleanField(default=False)
    date_processing_at = models.DateTimeField(null=True, blank=True)
    is_testing = models.BooleanField(default=False)
    date_testing_at = models.DateTimeField(null=True, blank=True)
    is_reviewed = models.BooleanField(default=False)
    date_reviewed_at = models.DateTimeField(null=True, blank=True)
    is_finished = models.BooleanField(default=False)
    date_finished_at = models.DateTimeField(null=True, blank=True)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
# seconed update
    def __str__(self):
        return self.task.title
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
    def __unicode__(self):
        return 
    def calculate_feedback_completion_percentage(self):
        total_conditions = 6
        completed_conditions = 0
        if self.is_viewed:
            completed_conditions += 1
        if self.is_in_dev:
            completed_conditions += 1
        if self.is_processing:
            completed_conditions += 1
        if self.is_testing:
            completed_conditions += 1
        if self.is_reviewed:
            completed_conditions += 1
        if self.is_finished:
            completed_conditions += 1
        return "{:.2f}".format((completed_conditions / total_conditions) * 100 )
    

    # ++++++++++++++ seconed update
class Member(models.Model):
    name = models.CharField(max_length=100)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=False,null=True,blank=True)

    def __str__(self):
        return self.name
    def save(self, *args, **kwargs):
        if not self.uuid:
            self.uuid = uuid.uuid4()
        super().save(*args, **kwargs)
class Sprint(models.Model):
    name = models.CharField(max_length=100)
    purpose = models.TextField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    members = models.ManyToManyField(Member, related_name="sprint")
    employee = models.ManyToManyField(Employee, related_name="sprints")
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=False,null=True,blank=True)
    
    def __str__(self):
        return self.name
    def tasks(self):
        res = []
        print(1)
        tasks = Task.objects.filter(sprints = self)
        for task in tasks:
            res.append({
                task.calculate_task_completion_percentage
            })
        print(tasks)
        return res
    @property
    def get_percentage(self):
        total_conditions = Task.objects.filter(sprints = self).count()
        completed_conditions  = 0
        # print(total_conditions)
        for task in Task.objects.filter(sprints = self):
            if float(task.calculate_task_completion_percentage()) > 90:
                completed_conditions += 1
            else:
              completed_conditions += float(task.calculate_task_completion_percentage())/100
        return  "{:.2f}".format((completed_conditions / total_conditions) * 100 )
    def get_percentage(self):
        total_conditions = Task.objects.filter(sprints = self).count()
        completed_conditions  = 0
        # print(total_conditions)
        for task in Task.objects.filter(sprints = self):
            if float(task.calculate_task_completion_percentage()) > 90:
                completed_conditions += 1
            else:
              completed_conditions += float(task.calculate_task_completion_percentage())/100
        print((completed_conditions / total_conditions) * 100 )
        return  "{:.2f}".format((completed_conditions / total_conditions) * 100 )

from django.core.exceptions import ValidationError

class Meeting(models.Model):
    sprint = models.ForeignKey(Sprint, on_delete=models.SET_NULL,null=True,blank=True) 
    task = models.ForeignKey(Task, on_delete=models.SET_NULL,null=True,blank=True) # updated need to add to live
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    meeting_link = models.CharField(max_length = 300,null=True,blank=True)
   
    def __str__(self):
        return f"Meeting for {self.sprint} ({self.start_time} - {self.end_time})"
    def clean(self):
        super().clean()

        if self.start_time >= self.end_time:
            raise ValidationError("Start time should be before end time.")

        overlapping_meetings = Meeting.objects.filter(
            sprint=self.sprint,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )

        if self.pk:
            overlapping_meetings = overlapping_meetings.exclude(pk=self.pk)
        overlapping_meetings2 = Meeting.objects.filter(
            task=self.task,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time
        )

        if self.pk:
            overlapping_meetings2 = overlapping_meetings.exclude(pk=self.pk)

        if overlapping_meetings.exists() or overlapping_meetings2.exists():
            raise ValidationError("Overlapping meetings detected within the same sprint/task.")
        