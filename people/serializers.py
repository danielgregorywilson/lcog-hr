import datetime

from django.contrib.auth.models import Group, User

from rest_framework import serializers

from people.models import (
    Employee, PerformanceReview, ReviewNote, Signature, TimeOffRequest
)


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='get_full_name')
    
    class Meta:
        model = User
        fields = ['pk', 'url', 'username', 'email', 'name', 'groups', 'is_staff']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Group
        fields = ['pk', 'url']


class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='user.get_full_name')
    email = serializers.EmailField(source='user.email')
    is_manager = serializers.SerializerMethodField()
    is_upper_manager = serializers.SerializerMethodField()
    prs_can_view = serializers.SerializerMethodField()
    notes_can_view = serializers.SerializerMethodField()
    next_to_sign_prs = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = ['url', 'pk', 'name', 'user', 'email', 'manager', 'is_manager', 'is_upper_manager', 'is_hr_manager', 'is_executive_director', 'prs_can_view', 'notes_can_view', 'next_to_sign_prs']

    @staticmethod
    def get_is_manager(employee):
        return employee.get_direct_reports().count() != 0

    @staticmethod
    def get_is_upper_manager(employee):
        return employee.get_direct_reports_descendants().count() != 0
    
    @staticmethod
    def get_prs_can_view(employee):
        return employee.prs_can_view()

    @staticmethod
    def get_notes_can_view(employee):
        return employee.notes_can_view()

    @staticmethod
    def get_next_to_sign_prs(employee):
        """
        Returns the name of the next employee who will sign the PR.
        """
        if employee.is_executive_director:
            return ""
        elif employee.is_hr_manager:
            return Employee.objects.filter(is_executive_director=True).first().user.get_full_name()
        elif employee.is_division_director:
            return Employee.objects.filter(is_hr_manager=True).first().user.get_full_name()
        elif employee.manager:
            return employee.manager.user.get_full_name()
        else:
            return ""



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
    all_required_signatures = serializers.SerializerMethodField()
    position_description_link = serializers.SerializerMethodField()
    signed_position_description = serializers.FileField()
 
    class Meta:
        model = PerformanceReview
        fields = [
            'url', 'pk', 'employee_pk', 'employee_name', 'employee_division',
            'employee_unit_or_program', 'employee_job_title', 'manager_pk',
            'manager_name', 'days_until_review', 'status', 'period_start_date', 
            'period_end_date', 'effective_date', 'evaluation_type',
            'probationary_evaluation_type', 'step_increase', 'top_step_bonus',
            'action_other',

            'factor_job_knowledge', 'factor_work_quality',
            'factor_work_quantity', 'factor_work_habits', 'factor_analysis',
            'factor_initiative', 'factor_interpersonal',
            'factor_communication', 'factor_dependability',
            'factor_professionalism', 'factor_management',
            'factor_supervision', 'evaluation_successes',
            'evaluation_opportunities', 'evaluation_goals_manager',
            'evaluation_goals_employee','evaluation_comments_employee',

            'position_description_link', 'description_reviewed_employee',
            'signed_position_description', 'all_required_signatures'
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
    def get_position_description_link(pr):
        return pr.employee.position_description_link()

    @staticmethod
    def get_discussion_took_place(pr):
        if hasattr(pr, 'performanceevaluation'):
            return "Yes" if pr.performanceevaluation.manager_discussed else "No"
        else:
            return "No"
    
    @staticmethod
    def get_all_required_signatures(pr):
        return pr.all_required_signatures()


class PerformanceReviewFileUploadSerializer(serializers.HyperlinkedModelSerializer):
    signed_position_description = serializers.FileField()

    class Meta:
        model = PerformanceReview
        fields = [
            'url', 'signed_position_description'
        ]


class FileUploadSerializer(serializers.Serializer):
    file_upload = serializers.FileField()

    class Meta:
        fields = ['file_upload']


class TimeOffRequestSerializer(serializers.HyperlinkedModelSerializer):
    employee_pk = serializers.IntegerField(source='employee.pk') #TODO: Make IntegerField
    employee_name = serializers.CharField(source='employee.user.get_full_name')
    manager_pk = serializers.IntegerField(source='employee.manager.pk')
 
    class Meta:
        model = TimeOffRequest
        fields = [
            'url', 'pk', 'employee_pk', 'employee_name', 'manager_pk',
            'date_start', 'date_end', 'approved'
        ]


class SignatureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Signature
        fields = [
            'url', 'pk', 'review', 'employee', 'date'
        ]


class ReviewNoteSerializer(serializers.HyperlinkedModelSerializer):
    pk = serializers.IntegerField()
    employee_pk = serializers.IntegerField(source='employee.pk')
    employee_name = serializers.CharField(source='employee.user.get_full_name')
    date = serializers.DateField()
    note = serializers.CharField()
    
    class Meta:
        model = ReviewNote
        fields = ['url', 'pk', 'employee_pk', 'employee_name', 'date', 'note']
