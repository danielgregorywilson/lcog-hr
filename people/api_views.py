from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import (
    BasePermission, DjangoModelPermissionsOrAnonReadOnly, IsAuthenticated,
    IsAuthenticatedOrReadOnly, SAFE_METHODS
)
from rest_framework.response import Response

from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404

from mainsite.helpers import (
    is_true_string, send_evaluation_written_email_to_employee,
    send_signature_email_to_manager
)

from people.models import (
    Employee, PerformanceReview, ReviewNote, Signature, TimeOffRequest
)
from people.serializers import (
    EmployeeSerializer, FileUploadSerializer, GroupSerializer,
    PerformanceReviewFileUploadSerializer, PerformanceReviewSerializer,
    ReviewNoteSerializer, SignatureSerializer, TimeOffRequestSerializer,
    UserSerializer
)


class IsAdminOrReadOnly(BasePermission):
    """
    The request is an authenticated admin user, or is a read-only request.
    """

    def has_permission(self, request, view):
        import pdb; pdb.set_trace()
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_staff
        )


class CurrentUserView(RetrieveAPIView):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_object(self):
        return getattr(self.request.user, 'employee', None)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    # permission_classes = [IsAdminOrReadOnly]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    # permission_classes = [IsAdminOrReadOnly]


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        Return a list of all employees. Optionally filter by direct reports
        """
        queryset = Employee.objects.all() # Default queryset

        # Optionally filter by direct reports
        user = self.request.user
        direct_reports = self.request.query_params.get('direct-reports', None)
        if direct_reports is not None and direct_reports == "True":
            queryset = Employee.objects.filter(manager__user=user)
        return queryset
    
    @action(detail=True, methods=['get'])
    def employee_next_performance_review(self, request, pk=None):
        next_review = request.user.employee.employee_next_review()
        serialized_review = PerformanceReviewSerializer(next_review,
            context={'request': request})
        return Response(serialized_review.data)


class PerformanceReviewPermission(BasePermission):
    """
    Manager or employee may update the Performance Review.
    Others may read only.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return request.user in [obj.employee.manager.user, obj.employee.user]


class PerformanceReviewViewSet(viewsets.ModelViewSet):
    queryset = PerformanceReview.objects.all()
    serializer_class = PerformanceReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly, PerformanceReviewPermission
    ]

    def get_queryset(self):
        """
        This view should return a list of all performance reviews for which
        the currently authenticated user is the manager.
        """
        user = self.request.user
        if user.is_authenticated:
            manager_prs = PerformanceReview.objects.filter(
                employee__manager__user=user)
            employee_prs = PerformanceReview.objects.filter(
                employee__user=user)
            queryset = manager_prs | employee_prs # Default queryset
            signature = self.request.query_params.get('signature', None)
            action_required = self.request.query_params.get('action_required',
                None)
            if is_true_string(signature):
                if action_required is not None:
                    if is_true_string(action_required):
                        queryset = PerformanceReview.signature_upcoming_reviews_action_required.get_queryset(user)
                    else:
                        queryset = PerformanceReview.signature_upcoming_reviews_no_action_required.get_queryset(user)    
                else:
                    queryset = PerformanceReview.signature_all_relevant_upcoming_reviews.get_queryset(user)
            elif action_required is not None:
                if is_true_string(action_required):
                    queryset = PerformanceReview.manager_upcoming_reviews_action_required.get_queryset(user)
                else:
                    queryset = PerformanceReview.manager_upcoming_reviews_no_action_required.get_queryset(user)
            else:
                queryset = PerformanceReview.manager_upcoming_reviews.get_queryset(user)
        else:
            queryset = PerformanceReview.objects.all()
        return queryset

    def retrieve(self, request, pk=None):
        queryset = PerformanceReview.objects.all()
        pr = get_object_or_404(queryset, pk=pk)
        serializer = PerformanceReviewSerializer(pr, 
            context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        pr = PerformanceReview.objects.get(pk=pk)
        pr.evaluation_type = request.data['evaluation_type']
        pr.probationary_evaluation_type = \
            request.data['probationary_evaluation_type']
        pr.step_increase = request.data['step_increase']
        pr.top_step_bonus = request.data['top_step_bonus']
        pr.action_other = request.data['action_other']
        pr.factor_job_knowledge = request.data['factor_job_knowledge']
        pr.factor_work_quality = request.data['factor_work_quality']
        pr.factor_work_quantity = request.data['factor_work_quantity']
        pr.factor_work_habits = request.data['factor_work_habits']
        pr.factor_analysis = request.data['factor_analysis']
        pr.factor_initiative = request.data['factor_initiative']
        pr.factor_interpersonal = request.data['factor_interpersonal']
        pr.factor_communication = request.data['factor_communication']
        pr.factor_dependability = request.data['factor_dependability']
        pr.factor_professionalism = request.data['factor_professionalism']
        pr.factor_management = request.data['factor_management']
        pr.factor_supervision = request.data['factor_supervision']
        pr.evaluation_successes = request.data['evaluation_successes']
        pr.evaluation_opportunities = request.data['evaluation_opportunities']
        pr.evaluation_goals_manager = request.data['evaluation_goals_manager']
        pr.evaluation_comments_employee = \
            request.data['evaluation_comments_employee']
        pr.description_reviewed_employee = \
            request.data['description_reviewed_employee']
        if pr.status == PerformanceReview.NEEDS_EVALUATION and all([
            (pr.evaluation_type == 'A' or
                (pr.evaluation_type == 'P' and
                    pr.probationary_evaluation_type != None
                )
            ),
            pr.step_increase != None,
            pr.top_step_bonus != None,
            pr.factor_job_knowledge != None,
            pr.factor_work_quality != None,
            pr.factor_work_quantity != None,
            pr.factor_work_habits != None,
            pr.factor_analysis != None,
            pr.factor_initiative != None,
            pr.factor_interpersonal != None,
            pr.factor_communication != None,
            pr.factor_dependability != None,
            pr.factor_professionalism != None,
            pr.factor_management != None,
            pr.factor_supervision != None,
            len(pr.evaluation_successes) > 0,
            len(pr.evaluation_opportunities) > 0,
            len(pr.evaluation_goals_manager) > 0,
            pr.description_reviewed_employee,
            pr.signed_position_description.name != ''
        ]):
            pr.status = PerformanceReview.EVALUATION_WRITTEN
            send_evaluation_written_email_to_employee(pr.employee, pr)
        pr.save()
        serialized_review = PerformanceReviewSerializer(pr,
            context={'request': request})
        return Response(serialized_review.data)
    
    def partial_update(self, request, pk=None):
        """
        Currently just updates the employee's comments. This might need to be
        more general to accept any partial updates.
        """
        pr = PerformanceReview.objects.get(pk=pk)
        pr.evaluation_comments_employee = \
            request.data['evaluation_comments_employee']
        pr.save()
        serialized_review = PerformanceReviewSerializer(pr,
            context={'request': request})
        return Response(serialized_review.data)

    # TODO: Don't use this - use the ModelViewSet get
    @action(detail=True, methods=['get'])
    def get_a_performance_review(self, request, pk=None):
        review = PerformanceReview.objects.get(pk=pk)
        serialized_review = PerformanceReviewSerializer(review,
            context={'request': request})
        return Response(serialized_review.data)


class FileUploadViewSet(viewsets.ViewSet):
    serializer_class = FileUploadSerializer

    def list(self, request):
        queryset = PerformanceReview.objects.all()
        serializer = PerformanceReviewFileUploadSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        queryset = PerformanceReview.objects.all()
        pr = get_object_or_404(queryset, pk=pk)
        serializer = PerformanceReviewFileUploadSerializer(pr, context={'request': request})
        return Response(serializer.data)
    
    def create(self, request):
        file_upload = request.FILES.get('file')
        if not file_upload:
            return Response(data="Missing file", status=400)
        pr_pk = request.data.get('pk')
        if not pr_pk:
            return Response(data="Missing PR PK", status=400)
        try:
            pr = PerformanceReview.objects.get(pk=pr_pk)
        except PerformanceReview.DoesNotExist:
            return Response(data="Invalid PR PK", status=400)
        pr.signed_position_description = file_upload
        pr.save()
        return Response(data=request.build_absolute_uri(pr.signed_position_description.url), status=200)


class SignatureViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows signatures to be created.
    """
    queryset = Signature.objects.all()
    serializer_class = SignatureSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        This view should return a list of all signatures made by this user.
        """
        user = self.request.user
        # TODO: Don't do this. There is an issue where the detail view doesn't have the user
        if user.is_anonymous:
            return Signature.objects.all()
        else:
            return Signature.objects.filter(employee__user=user)
    
    def create(self, request):
        pr = PerformanceReview.objects.get(pk=request.data['review_pk'])
        employee = Employee.objects.get(pk=request.data['employee_pk'])
        new_signature = Signature.objects.create(review=pr, employee=employee)
        
        # Send notification to next manager in the chain
        pr_employee_has_signed = Signature.objects.filter(employee=pr.employee).count() == 1
        pr_manager_has_signed = Signature.objects.filter(employee=pr.employee.manager).count() == 1
        if pr_employee_has_signed and pr_manager_has_signed and pr.status == PerformanceReview.EVALUATION_WRITTEN:
            if employee == pr.employee:
                send_signature_email_to_manager(employee.manager.manager, pr)
            else:
                send_signature_email_to_manager(employee.manager, pr)
        
        serialized_signature = SignatureSerializer(new_signature,
            context={'request': request})
        return Response(serialized_signature.data)


class ReviewNoteViewSet(viewsets.ModelViewSet):
    queryset = ReviewNote.objects.all()
    serializer_class = ReviewNoteSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        """
        This view should return a list of all review notes written by this user.
        """
        user = self.request.user
        # TODO: Don't do this. There is an issue where the detail view doesn't have the user
        if user.is_anonymous:
            return ReviewNote.objects.all()
        else:
            return ReviewNote.objects.filter(manager__user=user)

    def create(self, request):
        employee = Employee.objects.get(pk=request.data['employee_pk'])
        manager = employee.manager
        note = request.data['note']
        new_review_note = ReviewNote.objects.create(manager=manager,
            employee=employee, note=note)
        serialized_note = ReviewNoteSerializer(new_review_note,
            context={'request': request})
        return Response(serialized_note.data)
    
    def update(self, request, pk=None):
        employee = Employee.objects.get(pk=request.data['employee_pk'])
        review_note = ReviewNote.objects.get(pk=pk)
        review_note.employeee = employee
        review_note.note = request.data['note']
        review_note.save()
        serialized_note = ReviewNoteSerializer(review_note,
            context={'request': request})
        return Response(serialized_note.data)
      
    # TODO: Detail false?
    @action(detail=True, methods=['get'])
    def notes_for_employee(self, request, pk=None):
        review_notes = ReviewNote.objects.filter(
            manager=request.user.employee.pk, employee=pk)
        serialized_notes = [ReviewNoteSerializer(note,
            context={'request': request}).data for note in review_notes]
        return Response(serialized_notes)


class TimeOffRequestViewSet(viewsets.ModelViewSet):
    queryset = TimeOffRequest.objects.all().order_by('-id')
    serializer_class = TimeOffRequestSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly, PerformanceReviewPermission
    ]

    # def get_queryset(self):
    #     """
    #     This view should return a list of all performance reviews for which
    #     the currently authenticated user is the manager.
    #     """
    #     user = self.request.user
    #     if user.is_authenticated:
    #         manager_prs = PerformanceReview.objects.filter(
    #             employee__manager__user=user)
    #         employee_prs = PerformanceReview.objects.filter(
    #             employee__user=user)
    #         queryset = manager_prs | employee_prs # Default queryset
    #         signature = self.request.query_params.get('signature', None)
    #         action_required = self.request.query_params.get('action_required',
    #             None)
    #         if is_true_string(signature):
    #             if action_required is not None:
    #                 if is_true_string(action_required):
    #                     queryset = PerformanceReview.signature_upcoming_reviews_action_required.get_queryset(user)
    #                 else:
    #                     queryset = PerformanceReview.signature_upcoming_reviews_no_action_required.get_queryset(user)    
    #             else:
    #                 queryset = PerformanceReview.signature_all_relevant_upcoming_reviews.get_queryset(user)
    #         elif action_required is not None:
    #             if is_true_string(action_required):
    #                 queryset = PerformanceReview.manager_upcoming_reviews_action_required.get_queryset(user)
    #             else:
    #                 queryset = PerformanceReview.manager_upcoming_reviews_no_action_required.get_queryset(user)
    #         else:
    #             queryset = PerformanceReview.manager_upcoming_reviews.get_queryset(user)
    #     else:
    #         queryset = PerformanceReview.objects.all()
    #     return queryset

    # def retrieve(self, request, pk=None):
    #     queryset = PerformanceReview.objects.all()
    #     pr = get_object_or_404(queryset, pk=pk)
    #     serializer = PerformanceReviewSerializer(pr, 
    #         context={'request': request})
    #     return Response(serializer.data)

    # def update(self, request, pk=None):
    #     pr = PerformanceReview.objects.get(pk=pk)
    #     pr.evaluation_type = request.data['evaluation_type']
    #     pr.probationary_evaluation_type = \
    #         request.data['probationary_evaluation_type']
    #     pr.step_increase = request.data['step_increase']
    #     pr.top_step_bonus = request.data['top_step_bonus']
    #     pr.action_other = request.data['action_other']
    #     pr.factor_job_knowledge = request.data['factor_job_knowledge']
    #     pr.factor_work_quality = request.data['factor_work_quality']
    #     pr.factor_work_quantity = request.data['factor_work_quantity']
    #     pr.factor_work_habits = request.data['factor_work_habits']
    #     pr.factor_analysis = request.data['factor_analysis']
    #     pr.factor_initiative = request.data['factor_initiative']
    #     pr.factor_interpersonal = request.data['factor_interpersonal']
    #     pr.factor_communication = request.data['factor_communication']
    #     pr.factor_dependability = request.data['factor_dependability']
    #     pr.factor_professionalism = request.data['factor_professionalism']
    #     pr.factor_management = request.data['factor_management']
    #     pr.factor_supervision = request.data['factor_supervision']
    #     pr.evaluation_successes = request.data['evaluation_successes']
    #     pr.evaluation_opportunities = request.data['evaluation_opportunities']
    #     pr.evaluation_goals_manager = request.data['evaluation_goals_manager']
    #     pr.evaluation_comments_employee = \
    #         request.data['evaluation_comments_employee']
    #     pr.description_reviewed_employee = \
    #         request.data['description_reviewed_employee']
    #     if pr.status == PerformanceReview.NEEDS_EVALUATION and all([
    #         (pr.evaluation_type == 'A' or
    #             (pr.evaluation_type == 'P' and
    #                 pr.probationary_evaluation_type != None
    #             )
    #         ),
    #         pr.step_increase != None,
    #         pr.top_step_bonus != None,
    #         pr.factor_job_knowledge != None,
    #         pr.factor_work_quality != None,
    #         pr.factor_work_quantity != None,
    #         pr.factor_work_habits != None,
    #         pr.factor_analysis != None,
    #         pr.factor_initiative != None,
    #         pr.factor_interpersonal != None,
    #         pr.factor_communication != None,
    #         pr.factor_dependability != None,
    #         pr.factor_professionalism != None,
    #         pr.factor_management != None,
    #         pr.factor_supervision != None,
    #         len(pr.evaluation_successes) > 0,
    #         len(pr.evaluation_opportunities) > 0,
    #         len(pr.evaluation_goals_manager) > 0,
    #         pr.description_reviewed_employee
    #     ]):
    #         pr.status = PerformanceReview.EVALUATION_WRITTEN
    #         send_evaluation_written_email_to_employee(pr.employee, pr)
    #     pr.save()
    #     serialized_review = PerformanceReviewSerializer(pr,
    #         context={'request': request})
    #     return Response(serialized_review.data)
    
    # def partial_update(self, request, pk=None):
    #     """
    #     Currently just updates the employee's comments. This might need to be
    #     more general to accept any partial updates.
    #     """
    #     pr = PerformanceReview.objects.get(pk=pk)
    #     pr.evaluation_comments_employee = \
    #         request.data['evaluation_comments_employee']
    #     pr.save()
    #     serialized_review = PerformanceReviewSerializer(pr,
    #         context={'request': request})
    #     return Response(serialized_review.data)

    # # TODO: Don't use this - use the ModelViewSet get
    # @action(detail=True, methods=['get'])
    # def get_a_performance_review(self, request, pk=None):
    #     review = PerformanceReview.objects.get(pk=pk)
    #     serialized_review = PerformanceReviewSerializer(review,
    #         context={'request': request})
    #     return Response(serialized_review.data)