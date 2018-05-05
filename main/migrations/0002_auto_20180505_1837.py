# Generated by Django 2.0.5 on 2018-05-05 18:37

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProblemStep',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('number', models.IntegerField(default=-1)),
                ('description', models.CharField(max_length=10000)),
                ('task', models.CharField(max_length=10000)),
            ],
        ),
        migrations.CreateModel(
            name='StepTracker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('todoist_task_id', models.IntegerField(default=0)),
                ('related_problem_prob', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps_trackers', to='main.ProblemProbability')),
                ('step', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps_trackers', to='main.ProblemStep')),
            ],
        ),
        migrations.RemoveField(
            model_name='suggestedproblem',
            name='steps',
        ),
        migrations.AddField(
            model_name='problemstep',
            name='related_problem',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='steps', to='main.SuggestedProblem'),
        ),
    ]