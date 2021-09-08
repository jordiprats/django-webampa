# Generated by Django 3.1.5 on 2021-09-07 12:59

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('slug', models.SlugField(blank=True, default=None, max_length=256, null=True, unique=True)),
                ('title', models.CharField(max_length=256)),
                ('html_message', models.TextField(blank=True, default=None, max_length=50000, null=True)),
                ('status', models.CharField(choices=[('a', 'esborrany'), ('z', 'publicada')], default='a', max_length=1)),
                ('show_blog', models.BooleanField(default=False)),
                ('show_gallery', models.BooleanField(default=False)),
                ('is_post', models.BooleanField(default=False)),
                ('post_date', models.DateTimeField(blank=True, default=None, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children_pages', to='www.page')),
            ],
            options={
                'ordering': ['slug'],
            },
        ),
        migrations.CreateModel(
            name='FileAttachment',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, default='', max_length=256, null=True)),
                ('filename', models.CharField(max_length=256)),
                ('upload_path', models.CharField(max_length=256)),
                ('filepath', models.CharField(max_length=256)),
                ('is_image', models.BooleanField(default=False)),
                ('static_url', models.CharField(blank=True, default='', max_length=256, null=True)),
                ('page', models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='www.page')),
            ],
            options={
                'ordering': ['name', '-filename'],
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('email', models.EmailField(max_length=256, unique=True)),
                ('name', models.CharField(blank=True, default='', max_length=256, null=True)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ['email'],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.AddIndex(
            model_name='page',
            index=models.Index(fields=['parent', 'slug'], name='www_page_parent__ee31b8_idx'),
        ),
        migrations.AddIndex(
            model_name='page',
            index=models.Index(fields=['is_post', '-post_date'], name='www_page_is_post_b5be60_idx'),
        ),
        migrations.AddIndex(
            model_name='fileattachment',
            index=models.Index(fields=['name', '-filename'], name='www_fileatt_name_04c143_idx'),
        ),
        migrations.AddIndex(
            model_name='fileattachment',
            index=models.Index(fields=['name'], name='www_fileatt_name_738569_idx'),
        ),
        migrations.AddIndex(
            model_name='fileattachment',
            index=models.Index(fields=['page', 'name'], name='www_fileatt_page_id_a731ec_idx'),
        ),
        migrations.AddIndex(
            model_name='user',
            index=models.Index(fields=['email'], name='www_user_email_d85671_idx'),
        ),
    ]
