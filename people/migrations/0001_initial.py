# Generated by Django 3.1 on 2020-08-14 22:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hire_date', models.DateField(verbose_name='hire date')),
                ('salary', models.PositiveIntegerField(verbose_name='salary')),
                ('manager', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='direct_reports', to='people.employee', verbose_name='manager')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='user')),
            ],
            options={
                'verbose_name': 'Employee',
                'verbose_name_plural': 'Employees',
            },
        ),
        migrations.CreateModel(
            name='ReviewNote',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True, verbose_name='review note date')),
                ('note', models.TextField(verbose_name='review note')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes', to='people.employee', verbose_name='employee')),
                ('manager', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='notes_written', to='people.employee', verbose_name='manager')),
            ],
            options={
                'verbose_name': 'Performance Review Note',
                'verbose_name_plural': 'Performance Review Notes',
            },
        ),
        migrations.CreateModel(
            name='PerformanceReview',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(verbose_name='review date')),
                ('status', models.CharField(choices=[('N', 'Needs evaluation'), ('EW', 'Evaluation written and date for discussion set'), ('EC', 'Evaluation discussed with employee'), ('ED', 'Evaluation denied'), ('EA', 'Evaluation approved')], default='N', max_length=2, verbose_name='review status')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='people.employee', verbose_name='employee')),
            ],
            options={
                'verbose_name': 'Performance Review',
                'verbose_name_plural': 'Performance Reviews',
            },
        ),
        migrations.CreateModel(
            name='PerformanceEvaluation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('evaluation', models.TextField(verbose_name='performance evaluation')),
                ('discussion_date', models.DateField(null=True, verbose_name='discussion date')),
                ('employee_discussed', models.BooleanField(default=False, verbose_name='employee discussed the evaluation')),
                ('manager_discussed', models.BooleanField(default=False, verbose_name='manager discussed the evaluation')),
                ('upper_manager_accepted', models.BooleanField(default=False, verbose_name='upper manager accepted the evaluation')),
                ('review', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='people.performancereview', verbose_name='performance review')),
            ],
            options={
                'verbose_name': 'Performance Evaluation',
                'verbose_name_plural': 'Performance Evaluations',
            },
        ),
    ]
