from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.db import models

import uuid

PAGE_STATUS_DRAFT = 'a'
PAGE_STATUS_PUBLIC = 'z'
PAGE_STATUS = [
    (PAGE_STATUS_DRAFT, 'esborrany'),
    (PAGE_STATUS_PUBLIC, 'publicada'),
]

class User(AbstractUser):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  email = models.EmailField(max_length=256, unique=True)

  name = models.CharField(max_length=256, blank=True, null=True, default='')

  def __str__(self):
    if self.name:
      return self.name
    else:
      return self.email

  class Meta:
    ordering = ['email']
    indexes = [
        models.Index(fields=['email']),
    ]

class Page(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
  slug = models.SlugField(max_length=256, default=None, blank=True, null=True, unique=True)

  title = models.CharField(max_length=256)  
  html_message = models.TextField(max_length=50000, default=None, blank=True, null=True)

  status = models.CharField(
    max_length=1,
    choices=PAGE_STATUS,
    default=PAGE_STATUS_DRAFT,
  )

  parent = models.ForeignKey('self', on_delete=models.CASCADE, default=None, blank=True, null=True, related_name='children_pages')

  def save(self, *args, **kwargs):
    self.full_clean()
    self.slug = slugify(self.title, allow_unicode=False)
    super().save(*args, **kwargs)

  class Meta:
    ordering = ['slug']
    indexes = [
        models.Index(fields=['parent', 'slug']),
    ]