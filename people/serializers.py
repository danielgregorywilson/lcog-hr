import datetime

from django.contrib.auth.models import User

from rest_framework import serializers

from people.models import Employee, PerformanceReview, ReviewNote


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='get_full_name')
    
    class Meta:
        model = User
        fields = ['pk', 'url', 'username', 'email', 'name', 'groups', 'is_staff']


class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='user.get_full_name')
    email = serializers.EmailField(source='user.email')
    is_manager = serializers.SerializerMethodField()
    is_upper_manager = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = ['url', 'pk', 'name', 'user', 'email', 'manager', 'is_manager', 'is_upper_manager']

    @staticmethod
    def get_is_manager(employee):
        return employee.get_direct_reports().count() != 0

    @staticmethod
    def get_is_upper_manager(employee):
        return employee.get_direct_reports_descendants().count() != 0


class PerformanceReviewSerializer(serializers.HyperlinkedModelSerializer):
    employee_pk = serializers.CharField(source='employee.pk') #TODO: Make IntegerField
    employee_name = serializers.CharField(source='employee.user.get_full_name')
    employee_division = serializers.SerializerMethodField()
    employee_unit_or_program = serializers.SerializerMethodField()
    employee_job_title = serializers.CharField(source='employee.job_title.name')
    manager_pk = serializers.IntegerField(source='employee.manager.pk')
    manager_name = serializers.CharField(source='employee.manager.user.get_full_name')
    days_until_review = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display')
    
    class Meta:
        model = PerformanceReview
        fields = [
            'url', 'pk', 'employee_pk', 'employee_name', 'employee_division',
            'employee_unit_or_program', 'employee_job_title', 'manager_pk',
            'manager_name', 'days_until_review', 'status', 'period_start_date', 
            'period_end_date', 'effective_date', 'evaluation_type',
            'probationary_evaluation_type', 'step_increase', 'top_step_bonus',

            'factor_job_knowledge', 'factor_work_quality',
            'factor_work_quantity', 'factor_work_habits', 'factor_analysis',
            'factor_initiative', 'factor_interpersonal',
            'factor_communication', 'factor_dependability',
            'factor_professionalism', 'factor_management',
            'factor_supervision', 'evaluation_successes',
            'evaluation_opportunities', 'evaluation_goals_manager',
            'evaluation_goals_employee','evaluation_comments_employee',

            'description_reviewed_employee'
        ]
    
    @staticmethod
    def get_employee_division(pr):
        if pr.employee.unit_or_program and pr.employee.unit_or_program.division:
            return pr.employee.unit_or_program.division.name
        else:
            return ''
    
    @staticmethod
    def get_employee_unit_or_program(pr):
        if pr.employee.unit_or_program:
            return pr.employee.unit_or_program.name
        else:
            return ''

    @staticmethod
    def get_days_until_review(pr):
        today = datetime.date.today()
        delta = pr.period_end_date - today
        return delta.days
    
    @staticmethod
    def get_evaluation(pr):
        if hasattr(pr, 'performanceevaluation'):
            return pr.performanceevaluation.evaluation
        else:
            return ""

    @staticmethod
    def get_discussion_took_place(pr):
        if hasattr(pr, 'performanceevaluation'):
            return "Yes" if pr.performanceevaluation.manager_discussed else "No"
        else:
            return "No"


class ReviewNoteSerializer(serializers.HyperlinkedModelSerializer):
    pk = serializers.IntegerField()
    employee_pk = serializers.IntegerField(source='employee.pk')
    employee_name = serializers.CharField(source='employee.user.get_full_name')
    date = serializers.DateField()
    note = serializers.CharField()
    
    class Meta:
        model = ReviewNote
        fields = ['url', 'pk', 'employee_pk', 'employee_name', 'date', 'note']