# Generated by Django 4.2.7 on 2023-11-23 11:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('is_staff', models.BooleanField(default=False)),
                ('is_active', models.BooleanField(default=True)),
                ('first_name', models.CharField(max_length=200)),
                ('last_name', models.CharField(max_length=200)),
                ('profession', models.CharField(max_length=200)),
                ('balance', models.IntegerField()),
                ('type', models.CharField(choices=[('Client', 'Client'), ('Contractor', 'Contractor')], default='Client', max_length=10)),
                ('username', models.CharField(max_length=200, unique=True)),
                ('password', models.CharField(max_length=200)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('terms', models.TextField(max_length=200)),
                ('status', models.CharField(choices=[('new', 'New'), ('in_progress', 'In progress'), ('terminated', 'Terminated')], default='new', max_length=15)),
                ('client', models.ForeignKey(limit_choices_to={'type': 'Client'}, on_delete=django.db.models.deletion.CASCADE, related_name='client_contracts', to=settings.AUTH_USER_MODEL)),
                ('contractor', models.ForeignKey(limit_choices_to={'type': 'Contractor'}, on_delete=django.db.models.deletion.CASCADE, related_name='contractor_contracts', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(max_length=200)),
                ('price', models.IntegerField()),
                ('paid', models.BooleanField()),
                ('payment_date', models.DateField()),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contract.contract')),
            ],
        ),
    ]