from rest_framework import serializers
from.models import Company, Employee, Meeting, Project, RoadMapItem, Sprint, Task, TaskComment, TaskFeedback
from django.contrib.auth.models import User

class ProjectRoadMapSprintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sprint
        fields = ['name','purpose','start_date','end_date','uuid','get_percentage']

class ProjectRoadMapSerializer(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    sprints = serializers.SerializerMethodField()
    class Meta:
        model = RoadMapItem
        fields = ['name','description','get_percentage','sprint','start_date','end_date','sprints',]

    def get_start_date(self,obj):
          try:
            return obj.sprint.all().order_by('start_date').first().start_date
          except:return None
    def get_end_date(self,obj):
          try:
            return obj.sprint.all().order_by('-start_date').first().end_date
          except:return None
    def get_sprints(self,obj):
          #name -date -uuid
          return ProjectRoadMapSprintSerializer(data = obj.sprint.all(),many= True).data
class ProjectDetailSerializer(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    road_map = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = ['name','get_percentage','start_date','end_date','road_map','uuid']
        
    def get_start_date(self,obj):
          try:
            roadMapITem =  RoadMapItem.objects.filter(project = obj.id).first()
            return roadMapITem.sprint.all().order_by('start_date').first().start_date
          except:return None
    def get_end_date(self,obj):
          try:
            roadMapITem =  RoadMapItem.objects.filter(project = obj.id).last()
            return roadMapITem.sprint.all().order_by('-start_date').first().end_date
          except:return None
    def get_road_map(self,obj):
          #name -date -uuid
          res = []
          try:
            roadMapITems =  RoadMapItem.objects.filter(project = obj.id)
            return ProjectRoadMapSerializer(roadMapITems,many=True).data
          except:return None
class ProjectSerializer(serializers.ModelSerializer):
    start_date = serializers.SerializerMethodField()
    end_date = serializers.SerializerMethodField()
    # road_map = serializers.SerializerMethodField()
    # road map 
    # time line
    class Meta:
        model = Project
        fields = ['name','uuid','start_date','end_date','get_percentage',"road_map"]
        
    def get_start_date(self,obj):
          try:
            roadMapITem =  RoadMapItem.objects.filter(project = obj.id).first()
            serialize = ProjectRoadMapSerializer(many= True,data=roadMapITem ) 
            return serialize.data
          except:return None
    def get_road_map(self,obj):
          try:
            roadMapITem =  RoadMapItem.objects.filter(project = obj.id).first()
            return roadMapITem.sprint.all().order_by('start_date').values()
          except:return None
    def get_end_date(self,obj):
          try:
            roadMapITem =  RoadMapItem.objects.filter(project = obj.id).last()
            return roadMapITem.sprint.all().order_by('-start_date').first().end_date
          except:return None
    
class CompanySerializer(serializers.ModelSerializer):
    projects = serializers.SerializerMethodField()
    class Meta:
        model = Company
        fields = ['name','is_active','projects']
    

    def get_projects(self,opj):
        projects = Project.objects.filter(company = opj.id)
        return ProjectSerializer(projects,many=True).data
        
class CompanyDetailSerializer(serializers.ModelSerializer):
    projects = serializers.SerializerMethodField()
    class Meta:
        model = Company
        fields = ['name','is_active','projects']
    

    def get_projects(self,opj):
        projects = Project.objects.filter(company = opj.id)
        return ProjectDetailSerializer(projects,many=True).data
        
class SprintSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    employee = serializers.SerializerMethodField()
    meeting_link = serializers.SerializerMethodField()
    class Meta:
        model = Sprint
        fields = ['id','meeting_link','purpose','start_date','members','employee']

    def get_meeting_link(self, obj):
        try:
            meeting = Meeting.objects.get(sprint = obj)
            return meeting.meeting_link
        except:
            return ""
    def get_members(self, obj):
        try:
            members = []
            for member  in obj.members.all():
                members.append(member.name)
            return members
        except:
            return ""
    def get_employee(self, obj):
        try:
            members = []
            for member  in obj.employee.all():
                members.append(member.user.username)
            return members
        except:
            return ""

class TaskSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SerializerMethodField()
    comments = serializers.SerializerMethodField()
    feedbacks = serializers.SerializerMethodField()
    company = serializers.SerializerMethodField()
    finish_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = ['id',
                   'title',
                     'memo',
                       'created',
                         'completed',
                         'comments',
                         'feedbacks',
                           'company',
                           'finish_percentage',
                             'assigned_to',
                               'assigned_at',
                                 'is_viewed',
                                   'date_viewed_at',
                                     'is_in_dev',
                                       'date_in_dev_at',
                                         'is_processing',
                                           'date_processing_at',
                                             'is_testing',
                                               'date_testing_at',
                                                 'is_reviewed',
                                                   'date_reviewed_at',
                                                     'is_finished',
                                                       'date_finished_at',
                                                         'uuid']
    
    def get_assigned_to(self, obj):
        res = []
        for user in obj.assigned_to.all().values():
            user_opj = User.objects.get(id = user['user_id'])
            company  = Company.objects.get(id = user['admin_company_id'])
            res.append({
                'user_name':user_opj.username,
                'company':company.get_name() 
            })
            # res.append(user)

        return res
    def get_feedbacks(self, obj):
        return TaskFeedback.objects.filter(task = obj ).values()
           

        return res
    def get_comments(self, obj):
        return TaskComment.objects.filter(task = obj ).values("employee__user__username",'feedback_text',"uuid")
    def get_company(self, obj):
        return obj.company.name
        
    def get_finish_percentage(self, obj):
        return obj.calculate_task_completion_percentage()
        