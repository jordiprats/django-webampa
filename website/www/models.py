from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
from django.conf import settings
from django.db import models

import uuid
import re
import os

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

  show_gallery = models.BooleanField(default=False)

  def getURL(self):
    if self.parent:
      return "/"+self.parent.slug+"/"+self.slug
    else:
      return "/"+self.slug

  def save(self, *args, **kwargs):
    self.full_clean()
    self.slug = slugify(self.title, allow_unicode=False)
    super().save(*args, **kwargs)

  class Meta:
    ordering = ['slug']
    indexes = [
        models.Index(fields=['parent', 'slug']),
    ]

class FileAttachment(models.Model):
  id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

  name = models.CharField(max_length=256, blank=True, null=True, default='')

  filename = models.CharField(max_length=256)
  upload_path = models.CharField(max_length=256)
  filepath = models.CharField(max_length=256)

  page = models.ForeignKey(Page, on_delete=models.CASCADE, default=None, blank=True, null=True, related_name='attachments')

  is_image = models.BooleanField(default=False)
  static_url = models.CharField(max_length=256, blank=True, null=True, default='')

  def save(self, *args, **kwargs):
    if re.search('\.jpg$', self.filename.lower()) or re.search('\.jpeg$', self.filename.lower()) or re.search('\.png$', self.filename.lower()):
      self.is_image = True
    self.static_url = settings.STATIC_DOMAIN+'uploads/'+self.upload_path+'/'+self.filename
    self.full_clean()
    super().save(*args, **kwargs)

  def __str__(self):
    return self.filename
  
  def delete(self, *args, **kwargs):
    try:
      os.remove(self.filepath)
    except:
      pass
    super(FileAttachment, self).delete(*args, **kwargs)

  class Meta:
    ordering = ['name', '-filename']
    indexes = [
      models.Index(fields=['name', '-filename']),
      models.Index(fields=['name']),
      models.Index(fields=['page', 'name']),
    ]