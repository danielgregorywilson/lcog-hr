import datetime

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

from mainsite.helpers import (
    send_completed_email_to_hr_manager,
    send_signature_email_to_executive_director,
    send_signature_email_to_hr_manager
)

# SHOW_REVIEW_TO_MANAGER_DAYS_BEFORE_DUE = 60
SHOW_REVIEW_TO_MANAGER_DAYS_BEFORE_DUE = 360

class Division(models.Model):
    class Meta:
        verbose_name = _("Division")
        verbose_name_plural = _("Divisions")

    name = models.CharField(_("name"), max_length=100)

    def __str__(self):
        return self.name


class UnitOrProgram(models.Model):
    class Meta:
        verbose_name = _("Unit/Program")
        verbose_name_plural = _("Units/Programs")

    division = models.ForeignKey("people.Division", verbose_name=_("division"), on_delete=models.CASCADE)
    name = models.CharField(_("name"), max_length=100)

    def __str__(self):
        return f"{self.division.name} : {self.name}"


class JobTitle(models.Model):
    class Meta:
        verbose_name = _("Job Title")
        verbose_name_plural = _("Job Titles")

    name = models.CharField(_("name"), max_length=100)
    position_description_link = models.URLField(_("position description link"), blank=True, null=True)

    def __str__(self):
        return self.name


class Employee(models.Model):
    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("employee_detail", kwargs={"pk": self.pk})

    def username(self):
        return self.user.username

    user = models.OneToOneField("auth.User", verbose_name=_("user"), on_delete=models.CASCADE)
    manager = models.ForeignKey("self", related_name="direct_reports", blank=True, null=True, verbose_name=_("manager"), on_delete=models.SET_NULL)
    unit_or_program = models.ForeignKey("people.UnitOrProgram", verbose_name=_("unit/program"), on_delete=models.SET_NULL, blank=True, null=True)
    job_title = models.ForeignKey("people.JobTitle", verbose_name=_("job title"), on_delete=models.SET_NULL, blank=True, null=True)
    position_description_link_override = models.URLField(_("position description link override"), blank=True, null=True)

    is_division_director = models.BooleanField(_("is a division director"), default=False)
    
    # These are UNIQUELY TRUE, enforced in model save
    is_hr_manager = models.BooleanField(_("is the HR manager"), default=False)
    is_executive_director = models.BooleanField(_("is the executive director"), default=False)

    def save(self, *args, **kwargs):
        # is_hr_manager can only apply to ONE Employee
        if self.is_hr_manager:
            try:
                old_manager = Employee.objects.get(is_hr_manager=True)
                if self != old_manager:
                    old_manager.is_hr_manager = False
                    old_manager.save()
            except Employee.DoesNotExist:
                pass
        # is_executive_director can only apply to ONE Employee
        if self.is_executive_director:
            try:
                old_director = Employee.objects.get(is_executive_director=True)
                if self != old_director:
                    old_director.is_executive_director = False
                    old_director.save()
            except Employee.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def employee_next_review(self):
        return self.performancereview_set.all().order_by("period_end_date").first()

    def get_direct_reports(self):
        return self.direct_reports.all()
    
    def get_descendants_of_employee(self, employee):
        employee_and_descendants = [employee]
        descendants = employee.direct_reports.all()
        for descendant in descendants:
            employee_and_descendants += self.get_descendants_of_employee(descendant)
        return employee_and_descendants

    def get_direct_reports_descendants(self, include_self=False):
        # Return all descendant direct reports, including the user's direct
        # reports.
        direct_reports_descendants = [self.get_descendants_of_employee(employee) for employee in self.get_direct_reports()]
        flat_list = [item for sublist in direct_reports_descendants for item in sublist] # Flatten the 2-D list
        pk_list = [item.pk for item in flat_list]
        if include_self:
            pk_list.append(self.pk)
        unique_descendant_pks = list(set(pk_list))
        return Employee.objects.filter(pk__in=unique_descendant_pks)

    def manager_upcoming_reviews(self):
        reviews = []
        for employee in self.get_direct_reports():
            employee_reviews = employee.performancereview_set.all()
            for review in employee_reviews:
                if review.days_until_due() < SHOW_REVIEW_TO_MANAGER_DAYS_BEFORE_DUE:
                    reviews.append(review)
        return sorted(reviews, key=lambda review: review.period_end_date)
    
    def manager_upcoming_reviews_action_required(self):
        reviews = []
        for review in self.manager_upcoming_reviews():
            if review.status == PerformanceReview.NEEDS_EVALUATION:
                reviews.append(review)
        return reviews
    
    def manager_upcoming_reviews_no_action_required(self):
        reviews = []
        for review in self.manager_upcoming_reviews():
            if review.status != PerformanceReview.NEEDS_EVALUATION:
                reviews.append(review)
        return reviews

    def signature_all_relevant_upcoming_reviews(self):
        # Returns all upcoming reviews for a manager's direct reports and their
        # descendants. For detail views.
        reviews = []
        for employee in self.get_direct_reports():
            employee_reviews = employee.performancereview_set.all()
            for review in employee_reviews:
                if review.days_until_due() < SHOW_REVIEW_TO_MANAGER_DAYS_BEFORE_DUE:
                    reviews.append(review)
        for employee in self.get_direct_reports_descendants():
            employee_reviews = employee.performancereview_set.all()
            for review in employee_reviews:
                if review.days_until_due() < SHOW_REVIEW_TO_MANAGER_DAYS_BEFORE_DUE:
                    reviews.append(review)
        return sorted(reviews, key=lambda review: review.period_end_date)
    
    def signature_upcoming_reviews(self):
        # Returns all upcoming reviews for a manager's direct reports.
        # HR Manager and Executive Director should see upcoming reviews for all
        # Employees.
        reviews = []
        if self.is_hr_manager:
            employees = Employee.objects.all()
        elif self.is_hr_manager:
            employees = Employee.objects.all()
        else:
            employees = self.get_direct_reports_descendants()
        for employee in employees:
            employee_reviews = employee.performancereview_set.all()
            for review in employee_reviews:
                if review.days_until_due() < SHOW_REVIEW_TO_MANAGER_DAYS_BEFORE_DUE:
                    reviews.append(review)
        return sorted(reviews, key=lambda review: review.period_end_date)
    
    def signature_upcoming_reviews_action_required(self):
        # Returns all upcoming reviews for a manager's direct reports which
        # require action from the manager to proceed. For list views.
        reviews = []
        for review in self.signature_upcoming_reviews():
            if self.is_executive_director:
                if (
                    review.status == PerformanceReview.EVALUATION_HR_PROCESSED and
                    review.signature_set.filter(employee=self).count() == 0
                ):
                    reviews.append(review)
            elif self.is_hr_manager:
                if (
                    review.status == PerformanceReview.EVALUATION_APPROVED and
                    review.signature_set.filter(employee=self).count() == 0
                ):
                    reviews.append(review)
            else:
                direct_report = review.employee
                while direct_report.manager != self:
                    direct_report = direct_report.manager
                if (
                    review.status == PerformanceReview.EVALUATION_WRITTEN and
                    review.signature_set.filter(employee=direct_report).count() == 1 and
                    review.signature_set.filter(employee=self).count() == 0
                ):
                    reviews.append(review)
        return reviews
    
    def signature_upcoming_reviews_no_action_required(self):
        # Returns all upcoming reviews for a manager's direct reports which do
        # not require action from the manager to proceed. For list views.
        reviews = []
        for review in self.signature_upcoming_reviews():
            if review.signature_set.filter(employee=self.pk).count() > 0:
                reviews.append(review)
        return reviews

    def prs_can_view(self):
        # You can view all PRs for which either you are the employee or the
        # employee is your direct report or a descendant direct report.
        if self.is_hr_manager or self.is_executive_director:
            return map(lambda pr: pr.id, PerformanceReview.objects.all())
        self_and_direct_reports = self.get_direct_reports_descendants(include_self=True)
        pr_ids = []
        for employee in self_and_direct_reports:
            employee_pr_ids = map(lambda pr: pr.id, PerformanceReview.objects.filter(employee=employee))
            pr_ids += employee_pr_ids
        return list(pr_ids)
    
    def notes_can_view(self):
        # You can view all notes you wrote.
        note_ids = map(lambda note: note.id, ReviewNote.objects.filter(manager=self))
        return list(note_ids)

    def position_description_link(self):
        # Returns override link if provided, otherwise the link from job title if there is a job title
        if self.position_description_link_override:
            return self.position_description_link_override
        elif self.job_title and self.job_title.position_description_link:
            return self.job_title.position_description_link
        return None


class ManagerUpcomingReviewsManager(models.Manager):
    def get_queryset(self, user):
        queryset = super().get_queryset()
        if hasattr(user, 'employee'):
            desired_pks = [pr.pk for pr in user.employee.manager_upcoming_reviews()]
            queryset = queryset.filter(pk__in=desired_pks)
        return queryset


class ManagerUpcomingReviewsActionRequiredManager(models.Manager):
    def get_queryset(self, user):
        queryset = super().get_queryset()
        desired_pks = [pr.pk for pr in user.employee.manager_upcoming_reviews_action_required()]
        queryset = queryset.filter(pk__in=desired_pks)
        return queryset


class ManagerUpcomingReviewsNoActionRequiredManager(models.Manager):
    def get_queryset(self, user):
        queryset = super().get_queryset()
        desired_pks = [pr.pk for pr in user.employee.manager_upcoming_reviews_no_action_required()]
        queryset = queryset.filter(pk__in=desired_pks)
        return queryset


class SignatureAllRelevantUpcomingReviewsManager(models.Manager):
    def get_queryset(self, user):
        queryset = super().get_queryset()
        desired_pks = [pr.pk for pr in user.employee.signature_all_relevant_upcoming_reviews()]
        queryset = queryset.filter(pk__in=desired_pks)
        return queryset


class SignatureUpcomingReviewsActionRequiredManager(models.Manager):
    def get_queryset(self, user):
        queryset = super().get_queryset()
        desired_pks = [pr.pk for pr in user.employee.signature_upcoming_reviews_action_required()]
        queryset = queryset.filter(pk__in=desired_pks)
        return queryset


class SignatureUpcomingReviewsNoActionRequiredManager(models.Manager):
    def get_queryset(self, user):
        queryset = super().get_queryset()
        desired_pks = [pr.pk for pr in user.employee.signature_upcoming_reviews_no_action_required()]
        queryset = queryset.filter(pk__in=desired_pks)
        return queryset


class PerformanceReview(models.Model):
    class Meta:
        verbose_name = _("Performance Review")
        verbose_name_plural = _("Performance Reviews")

    def __str__(self):
        return f"Performance review for {self.employee.user.username} on {self.period_end_date}"

    def get_absolute_url(self):
        return reverse("performance_review_detail", kwargs={"pk": self.pk})

    # Managers for filtering PRs
    objects = models.Manager()
    manager_upcoming_reviews = ManagerUpcomingReviewsManager()
    manager_upcoming_reviews_action_required = ManagerUpcomingReviewsActionRequiredManager()
    manager_upcoming_reviews_no_action_required = ManagerUpcomingReviewsNoActionRequiredManager()
    signature_all_relevant_upcoming_reviews = SignatureAllRelevantUpcomingReviewsManager()
    signature_upcoming_reviews_action_required = SignatureUpcomingReviewsActionRequiredManager()
    signature_upcoming_reviews_no_action_required = SignatureUpcomingReviewsNoActionRequiredManager()

    NEEDS_EVALUATION = 'N'
    EVALUATION_WRITTEN = 'EW'
    EVALUATION_APPROVED = 'EA'
    EVALUATION_HR_PROCESSED = 'EP'
    EVALUATION_ED_APPROVED = 'ED'
    STATUS_CHOICE = [
        (NEEDS_EVALUATION, 'Needs evaluation'),
        (EVALUATION_WRITTEN, 'Evaluation written and reviewed with employee'),
        (EVALUATION_APPROVED, 'Evaluation approved up to division director'),
        (EVALUATION_HR_PROCESSED, 'Evaluation processed by HR'),
        (EVALUATION_ED_APPROVED, 'Evaluation approved by executive director'),
    ]

    PROBATIONARY_EVALUATION = 'P'
    ANNUAL_EVALUATION = 'A'
    EVALUATION_TYPE_CHOICE = [
        (PROBATIONARY_EVALUATION, 'Probationary evaluation'),
        (ANNUAL_EVALUATION, 'Annual evaluation'),
    ]

    SEIU_PROBATIONARY_EVALUATION = 'S'
    NON_SEIU_PROBATIONARY_EVALUATION = 'N'
    PROBATIONARY_EVALUATION_TYPE_CHOICE = [
        (NON_SEIU_PROBATIONARY_EVALUATION, 'SEIU (180 day)'),
        (NON_SEIU_PROBATIONARY_EVALUATION, 'Non-SEIU (6 month)'),
    ]

    YES = 'Y'
    NO = 'N'
    NULLABLE_BOOLEAN_CHOICE = [
        (YES, 'Yes'),
        (NO, 'No')
    ]

    NEEDS_IMPROVEMENT = 'N'
    MEETS_JOB_REQUIREMENTS = 'M'
    EXCEEDS_JOB_REQUIREMENTS = 'E'
    NOT_APPLICABLE = 'NA'
    PERFORMANCE_FACTOR_CHOICE = [
        (NEEDS_IMPROVEMENT, 'Needs Improvement'),
        (MEETS_JOB_REQUIREMENTS, 'Meets Job Requirements'),
        (EXCEEDS_JOB_REQUIREMENTS, 'Exceeds Job Requirements'),
        (NOT_APPLICABLE, 'Not Applicable'),
    ]

    status = models.CharField(_("review status"), max_length=2, choices=STATUS_CHOICE, default=NEEDS_EVALUATION)

    employee = models.ForeignKey("Employee", verbose_name=_("employee"), on_delete=models.CASCADE)
    period_start_date = models.DateField(_("performance period start date"), auto_now=False, auto_now_add=False)
    period_end_date = models.DateField(_("performance period end date"), auto_now=False, auto_now_add=False)
    effective_date = models.DateField(_("effective date"), auto_now=False, auto_now_add=False)

    evaluation_type = models.CharField(_("evaluation type"), max_length=1, choices=EVALUATION_TYPE_CHOICE, default=ANNUAL_EVALUATION, blank=True, null=True)
    probationary_evaluation_type = models.CharField(_("probationary evaluation type"), max_length=1, choices=PROBATIONARY_EVALUATION_TYPE_CHOICE, blank=True, null=True)

    step_increase = models.CharField(_("step increase"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    top_step_bonus = models.CharField(_("top step bonus"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    action_other = models.CharField(_("action other"), max_length=255, blank=True, null=True)
    
    factor_job_knowledge = models.CharField(_("job knowledge"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_work_quality = models.CharField(_("quality of work"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_work_quantity = models.CharField(_("quanitity of work"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_work_habits = models.CharField(_("work habits"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_analysis = models.CharField(_("analysis and decision-making"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_initiative = models.CharField(_("initiative and creativity"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_interpersonal = models.CharField(_("interpersonal relations"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_communication = models.CharField(_("communication"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_dependability = models.CharField(_("dependability and responsibility"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_professionalism = models.CharField(_("professionalism and customer service"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_management = models.CharField(_("project management"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_supervision = models.CharField(_("supervision"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)

    evaluation_successes = models.TextField(_("employee's successes"), blank=True, null=True)
    evaluation_opportunities = models.TextField(_("opportunities for growth"), blank=True, null=True)
    evaluation_goals_manager = models.TextField(_("goals for the comind year (manager)"), blank=True, null=True)
    evaluation_goals_employee = models.TextField(_("goals for the comind year (employee)"), blank=True, null=True)
    evaluation_comments_employee = models.TextField(_("employee comments"), blank=True, null=True)

    description_reviewed_employee = models.BooleanField(_("position description has been reviewed with employee"), default=False)
    signed_position_description = models.FileField(_("signed position description"), upload_to="uploads/signed-position-descriptions", blank=True, null=True)

    def username(self):
        return self.employee.user.username

    def days_until_due(self):
        timedelta = self.effective_date - datetime.date.today()
        return timedelta.days

    def overdue(self):
        if self.days_until_due() <= 0:
            return True
        return False

    def all_required_signatures(self):
        """
        Returns a list of lists of the form:
        (
            Employee Title, Employee Name, Signature Date, Employee PK,
            Whether the Employee is ready to sign and needs to sign
        )
        such that each tuple represents a signature required or already created
        for the Performance Review to be completed. Starts with the Employee
        and proceeds up the management chain until it gets to the Division
        Director. And then we add HR Manager and Executive Director.
        """
        signatures = []
        employee = self.employee
        employee_signature = Signature.objects.filter(review=self, employee=self.employee).first()
        last_employee_in_chain = employee # Keep track of the last employee so we can check if they signed
        added_hr_manager = False
        added_executive_director = False
        while True:
            # Try to get the current Employee's signature and add it to the signature list
            if len(signatures) == 0:
                title = "Employee"
            elif len(signatures) == 1:
                title = "Manager"
            else:
                if employee.job_title:
                    title = employee.job_title.name
                else:
                    title = None
            signature = Signature.objects.filter(review=self, employee=employee).first()
            if signature:
                signatures.append([title, signature.employee.user.get_full_name(), signature.date, None, False]) # Not ready to sign because there is a signature
            else:
                ready_to_sign = False
                if title in ["Employee", "Manager"]:
                    if self.status != PerformanceReview.NEEDS_EVALUATION:
                        ready_to_sign = True
                else:
                    # If direct report has signed, we are ready
                    direct_report_signature = Signature.objects.filter(review=self, employee=last_employee_in_chain).first()
                    if direct_report_signature and employee_signature:
                        ready_to_sign = True
                signatures.append([title, None, None, employee.pk, ready_to_sign])
            
            # Keep track of whether we're already adding HR manager and ED signatures
            if employee.is_hr_manager:
                added_hr_manager = True
            if employee.is_executive_director:
                added_executive_director = True

            # Get the next manager in the chain
            if employee.is_division_director:
                break
            if employee.manager:
                last_employee_in_chain = employee
                employee = employee.manager
            else:
                break
        
        # Finally, add the HR Manager and Executive Director Signatures if still needed
        if not added_hr_manager:
            hr_manager = Employee.objects.filter(is_hr_manager=True).first()
            hr_signature = Signature.objects.filter(review=self, employee=hr_manager).first()
            if hr_signature:
                signatures.append(["Human Resources Manager", hr_manager.user.get_full_name(), hr_signature.date, None, False]) # Not ready to sign because there is a signature
            else:
                # If last manager has signed, we are ready
                direct_report_signature = Signature.objects.filter(review=self, employee=last_employee_in_chain).first()
                ready_to_sign = False
                if direct_report_signature:
                    ready_to_sign = True
                signatures.append(["Human Resources Manager", None, None, hr_manager.pk, ready_to_sign])
        if not added_executive_director:
            ed = Employee.objects.filter(is_executive_director=True).first()
            ed_signature = Signature.objects.filter(review=self, employee=ed).first()
            if ed_signature:
                signatures.append(["Executive Director", ed.user.get_full_name(), ed_signature.date, None, False]) # Not ready to sign because there is a signature
            else:
                # If HR manager has signed, we are ready
                ready_to_sign = False
                if hr_signature:
                    ready_to_sign = True
                signatures.append(["Executive Director", None, None, ed.pk, ready_to_sign])
        return signatures

    def create_next_review_for_employee(self):
        PerformanceReview.objects.create(
            employee=self.employee,
            period_start_date=self.period_end_date + datetime.timedelta(days=1),
            period_end_date=self.period_end_date + datetime.timedelta(days=365),
            effective_date=self.effective_date + datetime.timedelta(days=365),
            evaluation_type=self.ANNUAL_EVALUATION
        )


class SignatureReminder(models.Model):
    """
    Represents the last time an employee was reminded to sign a Performance
    Evaluation. We can use this to remind them again a specific amount of time
    in the future.
    """
    
    class Meta:
        verbose_name = _("Signature Reminder")
        verbose_name_plural = _("Signature Reminders")
        get_latest_by = ("date")

    def __str__(self):
        if self.employee == self.review.employee:
            return f"Reminder for {self.employee.user.username} on {self.date} to sign their own review"
        elif self.employee == self.review.employee.manager:
            return f"Reminder for {self.employee.user.username} on {self.date} to sign a review for {self.review.employee.user.username} that they wrote"
        else:
            return f"Reminder for {self.employee.user.username} on {self.date} to sign a review for {self.review.employee.user.username}"

    review = models.ForeignKey("people.PerformanceReview", verbose_name=_("performance review"), on_delete=models.CASCADE)
    employee = models.ForeignKey("people.Employee", on_delete=models.CASCADE)
    date = models.DateField(_("reminder date"), auto_now=False, auto_now_add=True)
    next_date = models.DateField(_("planned next reminder date"))


class Signature(models.Model):    
    class Meta:
        verbose_name = _("Signature")
        verbose_name_plural = _("Signatures")

    def __str__(self):
        return f"{self.employee.user.get_full_name()}'s approval of {self.review.employee.user.get_full_name()}'s performance review"

    review = models.ForeignKey("people.PerformanceReview", verbose_name=_("performance review"), on_delete=models.CASCADE)
    employee = models.ForeignKey("people.Employee", on_delete=models.CASCADE)
    date = models.DateField(_("signature date"), auto_now=False, auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.employee.is_division_director:
            self.review.status = PerformanceReview.EVALUATION_APPROVED
            self.review.save()
            # Send notification to next manager in the chain (HR manager)
            send_signature_email_to_hr_manager(self.review)
        elif self.employee.is_hr_manager:
            self.review.status = PerformanceReview.EVALUATION_HR_PROCESSED
            self.review.save()
            # Send notification to next manager in the chain (executive director)
            send_signature_email_to_executive_director(self.review)
        elif self.employee.is_executive_director:
            self.review.status = PerformanceReview.EVALUATION_ED_APPROVED
            self.review.save()
            # Send notification to HR manager
            send_completed_email_to_hr_manager(self.review)
            # Create new Performance Review for employee
            self.review.create_next_review_for_employee()
        super().save(*args, **kwargs)


class ReviewNote(models.Model):
    class Meta:
        verbose_name = _("Review Note")
        verbose_name_plural = _("Review Notes")

    def get_absolute_url(self):
        return reverse("note-update", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if not hasattr(self, 'manager'):
            self.manager = self.employee.manager
        super().save(*args, **kwargs)

    manager = models.ForeignKey("Employee", related_name="notes_written", verbose_name=_("manager"), on_delete=models.CASCADE)
    employee = models.ForeignKey("Employee", related_name="notes", verbose_name=_("employee"), on_delete=models.CASCADE)
    date = models.DateField(_("review note date"), auto_now=False, auto_now_add=True)
    note = models.TextField(_("review note"))


class TimeOffRequest(models.Model):
    class Meta:
        verbose_name = _("Time Off Request")
        verbose_name_plural = _("Time Off Requests")
    
    employee = models.ForeignKey("Employee", related_name="time_off_requests", verbose_name=_("employee"), on_delete=models.CASCADE)
    date_start = models.DateField(_("time off start date"), auto_now=False, auto_now_add=False)
    date_end = models.DateField(_("time off start date"), auto_now=False, auto_now_add=False)

    approved = models.BooleanField(_("approved"), default=False)