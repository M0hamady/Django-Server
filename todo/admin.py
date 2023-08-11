from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from todo.forms import TaskAdminForm
from .models import AdminCompany, Duration,Employee, Company, Member, Project, RoadMapItem, Section, Task, TaskComment, TaskFeedback
from django.utils import timezone

# admin.site.register(Task)
admin.site.site_title = "CodeOCean tasks"
admin.site.site_header = "CodeOCean tasks"
class TaskInline(admin.TabularInline):
    model = Task
    extra = 0
    fields = ('title', 'created', 'completed', 'durations', 'durations__week_of_month', 'assigned_to', 'assigned_at')
    readonly_fields = ('created', 'assigned_to', 'assigned_at')
    can_delete = False

   

class CompanyAdmin(admin.ModelAdmin):
    # inlines = (TaskInline,)
    list_display = ('name', 'tasks_count','uuid','none_completed_tasks_count','completed_tasks_count' )
    list_filter = ('name',)
    search_fields = ('name',)

    def tasks_count(self, obj):
        return obj.get_all_tasks().count()
    def completed_tasks_count(self, obj):
        return obj.get_all_completed_tasks().count()
    def none_completed_tasks_count(self, obj):
        return obj.get_all_non_completed_tasks().count()

    


admin.site.register(Company, CompanyAdmin)



class FeedbackAdmin(admin.TabularInline):
    model = TaskFeedback
    list_display = ('employee',"feedback_text")
    extra = 0
class CommentAdminInline(admin.TabularInline):
    model = TaskComment
    list_display = ("feedback_text", "company")
    extra = 0
class DurationAdmin(admin.TabularInline):
    model = Duration         
    list_display = ("duration","start_time","end_time", "assigned_to",'week_of_month')
    extra = 0

class TaskAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    form = TaskAdminForm
    list_display = ('title', 'company',  'calculate_task_completion_percentage','calculate_task_durations', 'completed', )
    readonly_fields = ('id',)
    list_filter = ('company', 'assigned_at', 'completed', 'assigned_to','duration__week_of_month', 'assigned_to__section')
    search_fields = ('title', 'company__name', 'assigned_to__user__username')

    def calculate_task_completion_percentage(self, obj):
        return f"{obj.calculate_task_completion_percentage()}%"
    calculate_task_completion_percentage.short_description = "Percentage"
    def calculate_task_durations(self, obj):
        return f"{obj.calculate_task_durations()}-hours"
    calculate_task_durations.short_description = "Durations"

    inlines = [FeedbackAdmin,DurationAdmin,CommentAdminInline]

admin.site.register(Task, TaskAdmin)


class DurationsAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('task','calculate_duration' )
    # list_filter = ('name', 'address', 'phone_number')
    # search_fields = ('name', 'address', 'phone_number')
admin.site.register(Duration, DurationsAdmin)
class AdminCompanyAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    inlines = (TaskInline,)
    list_display = ('name', 'get_all_tasks_count', 'get_all_completed_tasks_count', 'get_all_non_completed_tasks_count', 'address', 'phone_number')
    list_filter = ('name', 'address', 'phone_number')
    search_fields = ('name', 'address', 'phone_number')

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.filter(admin_company=request.user.employee.admin_company)
        return queryset

    def get_all_tasks_count(self, obj):
        return obj.get_all_tasks().count()

    def get_all_completed_tasks_count(self, obj):
        return obj.get_all_completed_tasks().count()

    def get_all_non_completed_tasks_count(self, obj):
        return obj.get_all_non_completed_tasks().count()
admin.site.register(AdminCompany, )


class TaskCommentAdmin(ImportExportModelAdmin,admin.ModelAdmin):
    list_display = ('task', 'employee',
                    'feedback_text',
                      )
    list_filter = ( 'employee',)
admin.site.register(TaskComment,TaskCommentAdmin)


class TaskFeedbackAdmin(admin.ModelAdmin):
    list_display = ('task', 'company',
                    
                    'feedback_text',
                    'is_viewed',
                    'calculate_feedback_completion_percentage',
                    'is_in_dev',
                    'is_processing',
                    'is_testing',
                    'is_reviewed',
                    'is_finished',
                      )
    list_filter = ( 'company','is_viewed',
                    'is_in_dev',
                    'is_processing',
                    'is_testing',
                    'is_reviewed',
                    'is_finished')
    list_editable = (
                    'is_viewed',
                    'is_in_dev',
                    'is_processing',
                    'is_testing',
                    'is_reviewed',
                    'is_finished',
                      )
class EmployeeAdmin(admin.ModelAdmin):
    # inlines = (TaskInline,)
    list_display = ('user','uuid', 'admin_company','tasks_count','section','completed_tasks_count','none_completed_tasks_count' )
    list_filter = ('user','admin_company','section')
    search_fields = ('user','section')

    def tasks_count(self, obj):
        return obj.get_all_tasks().count()
    def completed_tasks_count(self, obj):
        return obj.get_all_completed_tasks().count()
    def none_completed_tasks_count(self, obj):
        return obj.get_all_non_completed_tasks().count()

    


admin.site.register(Employee, EmployeeAdmin)



from django.contrib import admin
from.models import TaskDuration

class TaskDurationAdmin(admin.ModelAdmin):
    list_display = ('duration',)
    ordering = ('duration',)

admin.site.register(TaskDuration, TaskDurationAdmin)
admin.site.register(TaskFeedback, TaskFeedbackAdmin)
admin.site.register(Section)

# ________________ seconde update
from .models import Meeting ,Sprint

class MeetingInline(admin.TabularInline):
    model = Meeting
    extra = 1

class SprintAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date')
    list_filter = ('name',)
    search_fields = ('name',)
    date_hierarchy = 'start_date'
    inlines = [MeetingInline]

admin.site.register(Sprint, SprintAdmin)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('sprint', 'start_time', 'end_time')
    list_filter = ('sprint',)
    search_fields = ('sprint__name',)
    date_hierarchy = 'start_time'

admin.site.register(Meeting, MeetingAdmin)
admin.site.register(Member)
admin.site.register(Project)
admin.site.register(RoadMapItem)