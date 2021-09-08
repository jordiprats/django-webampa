from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from django.views.decorators.http import require_GET
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q

from www.models import *
from www.forms import *

import datetime
import time
import sys
import os

def login_builtin_user(request):
    if request.method == 'POST':
        next = request.POST.get('next', None)
        if next and '://' in next:
            next = None
        user = authenticate(username=request.POST['login'].lower(), password=request.POST['password'])
        if user is not None:
            login(request, user)
            if next:
                return redirect(next)
            else:
                return redirect('home')
        else:
            return render(request, 'login.html', {'message': 'User not found or password invalid'})
    else:
        next = request.GET.get('next', None)
        if next and '://' in next:
            next = None
        return render(request, 'login.html', { 'next': next })

def logout_builtin_user(request):
    logout(request)
    return redirect('home')

def attachment_to_url(request, attachment_id):
  try:
    instance_attachment = FileAttachment.objects.filter(id=attachment_id).first()
    return redirect(instance_attachment.static_url)
  except:
    raise Http404("Aquesta pàgina no existeix")

@require_GET
def robots_txt(request):
  lines = [
      "User-Agent: *",
      "Disallow: /admin/",
  ]
  return HttpResponse("\n".join(lines), content_type="text/plain")

def get_main_nav():
  list_root_pages = Page.objects.filter(is_post=False, parent=None, status=PAGE_STATUS_PUBLIC).filter(~Q(slug=settings.ROOT_PAGE_SLUG))

  nav = {}
  for page in list_root_pages:
    nav[page.title] = page.getURL()

  return nav

#
# vistes
#

def view_page_by_slug(request, parent_slug=None, page_slug=None, post_slug=None):
  if os.getenv('DEBUG', False):
    print('view_page_by_slug '+str(parent_slug)+' '+str(page_slug))
  if parent_slug:
    url = parent_slug+'/'+page_slug
  else:
    url = page_slug

  if post_slug:
    url += '/' + post_slug

  return view_page(request, url)

def view_page(request, url=None):
  if os.getenv('DEBUG', False):
    print('view_page '+str(url))
  parent_slug=None
  if not url:
    page_slug=settings.ROOT_PAGE_SLUG
    post_slug = None
    parent_slug = None
  else:
    if '/' in url:
      components = url.split('/')
      parent_slug = components[0]
      page_slug = components[1]
      try:
        post_slug = components[2]
      except:
        post_slug = None
    else:
      page_slug = url
      post_slug = None
      parent_slug = None
  
  if os.getenv('DEBUG', False):
    print(str(parent_slug))
    print(str(page_slug))
    print(str(post_slug))

  if post_slug:
    parent_page = Page.objects.filter(parent__slug=parent_slug, slug=page_slug, status=PAGE_STATUS_PUBLIC).first()
    page_instance = Page.objects.filter(parent=parent_page, slug=post_slug).first()
  else:
    page_instance = Page.objects.filter(parent__slug=parent_slug, slug=page_slug, status=PAGE_STATUS_PUBLIC).first()
    if not page_instance:
      post_slug = page_slug
      page_slug = None
      parent_page = Page.objects.filter(slug=parent_slug, status=PAGE_STATUS_PUBLIC).first()
      page_instance = Page.objects.filter(parent=parent_page, slug=page_slug).first()

  if not page_instance:
    print()
    raise Http404("Aquesta URL no existeix")

  attachments = {}
  for attachment in page_instance.attachments.all():
    if attachment.name:
      attachments[attachment.name] = attachment.static_url
    else:
      attachments[attachment.filename] = attachment.static_url

  internal_nav = {}
  if page_instance.children_pages.filter(is_post=False, status=PAGE_STATUS_PUBLIC).count() > 0:
    nav_obj = page_instance
    current_subpage = page_instance.title
    internal_nav[page_instance.title] = page_instance.getURL()
  else:
    if page_instance.parent:
      current_subpage = page_instance.title
      nav_obj = page_instance.parent
      internal_nav[page_instance.parent.title] = page_instance.parent.getURL()
    else:
      internal_nav = None
      current_subpage = None

  if current_subpage:
    for page in nav_obj.children_pages.filter(is_post=False, status=PAGE_STATUS_PUBLIC).all():
      internal_nav[page.title] = page.getURL()
  
  if internal_nav:
    if len(internal_nav) == 1:
      internal_nav = {}

  list_posts_raw = Page.objects.filter(is_post=True, parent=page_instance, status=PAGE_STATUS_PUBLIC).order_by('-post_date')

  page = request.GET.get('page', 1)
  paginator = Paginator(list_posts_raw, 10)
  try:
      list_posts = paginator.page(page)
  except PageNotAnInteger:
      list_posts = paginator.page(1)
  except EmptyPage:
      list_posts = paginator.page(paginator.num_pages)

  if page_instance.is_post:
    return render(request, 'pages/view.html', { 
                                            'page': page_instance,
                                            'root_nav': get_main_nav(),
                                            'attachments': attachments,
                                            'list_posts': list_posts
                                          })
  else:
    return render(request, 'pages/view.html', { 
                                                'page': page_instance,
                                                'root_nav': get_main_nav(),
                                                'internal_nav': internal_nav,
                                                'current_page': current_subpage,
                                                'attachments': attachments,
                                                'list_posts': list_posts
                                              })

@login_required
def home_admin(request, url=None):
  return redirect('list.pages')

#
# gestió pages
#

@login_required
def edit_page(request, parent_slug=None, page_slug=None):
  attachments = {}
  try:
    if parent_slug:
      parent_instance = Page.objects.filter(is_post=False, slug=parent_slug).first()
    try:
      page_instance = Page.objects.filter(is_post=False, parent__slug=parent_slug, slug=page_slug).first()
      for attachment in page_instance.attachments.all():
        if attachment.name:
          attachments[attachment.name] = attachment.static_url
        else:
          attachments[attachment.filename] = attachment.static_url
    except:
      if parent_slug:
        page_instance = Page(is_post=False, parent=parent_instance)
      else:
        page_instance = Page(is_post=False)

    if request.method == 'POST':
      form = PageForm(request.POST, instance=page_instance)
      if form.is_valid():
        page_instance = form.save(commit=False)
        if parent_slug:
          page_instance.parent = parent_instance
        page_instance.save()

        try:
          boto_apretat = str(form.data['guardar'])
          messages.info(request, 'Pàgina guardada correctament')
          if parent_slug:
            return redirect('list.subpages', parent_slug=parent_slug)
          else:
            return redirect('list.pages')
        except:
          if parent_slug:
            return redirect('subpage.attachments', parent_slug=parent_slug, page_slug=page_slug)
          else:
            return redirect('page.attachments', page_slug=page_slug)


      else:
        messages.error(request, 'Formulari incorrecte')
        return render(request, 'pages/edit.html', { 
                                                    'form': form, 
                                                    'page': page_instance, 
                                                    'parent_slug': parent_slug,
                                                    'attachments': attachments
                                                 })
    else:
      form = PageForm(instance=page_instance)
      return render(request, 'pages/edit.html', { 
                                                  'form': form, 
                                                  'page': page_instance, 
                                                  'parent_slug': parent_slug,
                                                  'attachments': attachments
                                                })

  except Exception as e:
    if os.getenv('DEBUG', False):
      print(str(e))
    if request.user.is_superuser:
      messages.error(request, str(e))
    if parent_slug:
      return redirect('list.subpages', parent_slug=parent_slug)
    else:
      return redirect('list.pages')

@login_required
def delete_page(request, parent_slug=None, page_slug=None, page_id=None):
  try:
    if page_id:
      page_instance = Page.objects.filter(id=page_id, slug=page_slug).first()
    else:
      if parent_slug:
        page_instance = Page.objects.filter(is_post=False, parent__slug=parent_slug, slug=page_slug).first()
      else:
        page_instance = Page.objects.filter(is_post=False, slug=page_slug).first()

    if request.method == 'POST':
      form = AreYouSureForm(request.POST)
      if form.is_valid():
        page_instance.delete()
        messages.info(request, 'Pàgina eliminada')
        if parent_slug:
          return redirect('list.subpages', parent_slug=parent_slug)
        else:
          return redirect('list.pages')
      else:
        messages.error(request, 'Formulari incorrecte')
        return render(request, 'pages/delete.html', { 
                                                    'form': form, 
                                                    'page': page_instance, 
                                                    'parent_slug': parent_slug,
                                                 })
    else:
      form = AreYouSureForm()
      return render(request, 'pages/delete.html', { 
                                                  'form': form, 
                                                  'page': page_instance, 
                                                  'parent_slug': parent_slug,
                                                })

  except Exception as e:
    if os.getenv('DEBUG', False):
      print(str(e))
    if request.user.is_superuser:
      messages.error(request, str(e))
    if parent_slug:
      return redirect('list.subpages', parent_slug=parent_slug)
    else:
      return redirect('list.pages')

@login_required
def list_pages(request, parent_slug=None):

  if parent_slug:
    list_pages_raw = Page.objects.filter(parent__slug=parent_slug)
  else:
    list_pages_raw = Page.objects.filter(parent=None)

  page = request.GET.get('page', 1)
  paginator = Paginator(list_pages_raw, 10)
  try:
      list_pages = paginator.page(page)
  except PageNotAnInteger:
      list_pages = paginator.page(1)
  except EmptyPage:
      list_pages = paginator.page(paginator.num_pages)

  return render(request, 'pages/list.html', {
                                              'list_pages': list_pages,
                                              'page_posts': False,
                                              'parent_slug': parent_slug,
                                            })

#
# gestió attachments
#
                               
@login_required
def remove_page_attachment(request, attachment_id=None):
    if not attachment_id:
      raise Http404("Aquesta pàgina no existeix")
    try:
      instance_attachment = FileAttachment.objects.filter(id=attachment_id).first()
      page_instance = instance_attachment.page
      
      if request.method == 'POST':
        form = AreYouSureForm(request.POST)
        if form.is_valid():
          instance_attachment.delete()
          messages.info(request, 'Fitxer adjunt eliminat')

          if page_instance.parent:
            return redirect('edit.subpage', parent_slug=page_instance.parent.slug, page_slug=page_instance.slug)
          else:
            return redirect('edit.page', page_slug=page_instance.slug)
        else:
          messages.error(request, 'Error eliminant l\'alumne')
      else:
          form = AreYouSureForm(request.GET)
      return render(request, 'pages/attachments/delete.html', { 'attachment': instance_attachment })

    except Exception as e:
      if settings.DEBUG:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print(exc_type, fname, exc_tb.tb_lineno)
        print(str(e))
    if page_instance.parent:
      return redirect('edit.subpage', parent_slug=page_instance.parent.slug, page_slug=page_instance.slug)
    else:
      return redirect('edit.page', page_slug=page_instance.slug)


@login_required
def page_attachments(request, parent_slug=None, page_slug=None, post_slug=None):
  try:
    if post_slug:
      parent_page_instance = Page.objects.filter(is_post=False, parent__slug=parent_slug, slug=page_slug).first()
      page_instance = Page.objects.filter(is_post=True, parent=parent_page_instance).first()
    else:
      page_instance = Page.objects.filter(is_post=False, parent__slug=parent_slug, slug=page_slug).first()

    attachments = {}
    for attachment in page_instance.attachments.all():
      if attachment.name:
        attachments[attachment.id] = attachment.name
      else:
        attachments[attachment.id] = attachment.filename

    if request.method == 'POST' and request.FILES['attachment']:
      myfile = request.FILES['attachment']
      upload_subdir = str(int(time.time()))
      fs = FileSystemStorage(location=settings.UPLOADS_ROOT+'/'+upload_subdir)
      filename = fs.save(myfile.name, myfile)

      upload = FileAttachment(filename=myfile.name, filepath=fs.location+'/'+filename, upload_path=upload_subdir, page=page_instance)
      upload.save()

      messages.info(request, 'Fitxer pujat correctament')
      if parent_slug:
        return redirect('edit.subpage', parent_slug=parent_slug, page_slug=page_slug)
      else:
        return redirect('edit.page', page_slug=page_slug)
    else:
      return render(request, 'pages/upload.html', { 'page': page_instance, 'attachments': attachments })
  except Exception as e:
    messages.error(request, 'Error pujant arxiu')
    if request.user.is_superuser:
      messages.error(request, str(e))
  
  if parent_slug:
    return redirect('edit.subpage', parent_slug=parent_slug, page_slug=page_slug)
  else:
    return redirect('edit.page', page_slug=page_slug)

#
# posts
#

@login_required
def edit_post(request, parent_slug=None, page_slug=None, post_slug=None, post_id=None):
  attachments = {}
  if not post_id:
    parent_page = Page.objects.filter(is_post=False, parent__slug=parent_slug, slug=page_slug).first()

    if not parent_page:
      raise Http404("Aquesta pàgina no existeix")
  
  try:
    if post_id:
      # editar existent
      post_instance = Page.objects.filter(is_post=True, slug=post_slug, id=post_id).first()
      parent_page = post_instance.parent

      for attachment in post_instance.attachments.all():
        if attachment.name:
          attachments[attachment.name] = attachment.static_url
        else:
          attachments[attachment.filename] = attachment.static_url
    else:
      # nou post
      post_instance = Page(is_post=True, parent=parent_page, post_date=datetime.datetime.now())

    if request.method == 'POST':
      form = BlogForm(request.POST, instance=post_instance)
      if form.is_valid():
        post_instance = form.save(commit=False)
        if parent_slug:
          post_instance.parent = parent_page
        post_instance.is_post = True
        post_instance.save()

        try:
          boto_apretat = str(form.data['guardar'])
          messages.info(request, 'Pàgina guardada correctament')
          return redirect('list.subpages', parent_slug=post_instance.parent.slug)
        except:
          if parent_slug:
            return redirect('subpage.post.attachments', parent_slug=parent_slug, page_slug=page_slug)
          else:
            return redirect('page.post.attachments', page_slug=page_slug)


      else:
        messages.error(request, 'Formulari incorrecte')
        return render(request, 'pages/edit.html', { 
                                                    'form': form, 
                                                    'page': post_instance, 
                                                    'parent_slug': parent_slug,
                                                    'page_slug': page_slug,
                                                    'attachments': attachments
                                                })
    else:
      form = BlogForm(instance=post_instance)
      return render(request, 'pages/edit.html', { 
                                                  'form': form, 
                                                  'page': post_instance, 
                                                  'parent_slug': parent_slug,
                                                  'page_slug': page_slug,
                                                  'attachments': attachments
                                                })

  except Exception as e:
    if os.getenv('DEBUG', False):
      print(str(e))
    if request.user.is_superuser:
      messages.error(request, str(e))
    if parent_slug:
      return redirect('list.subpages', parent_slug=parent_slug)
    else:
      return redirect('list.pages')

@login_required
def list_posts(request, parent_slug=None, page_slug=None):

  parent_page = Page.objects.filter(is_post=False, parent__slug=parent_slug, slug=page_slug).first()

  if not parent_page:
    raise Http404("Aquesta pàgina no existeix")

  list_posts_raw = Page.objects.filter(is_post=True, parent=parent_page)

  page = request.GET.get('page', 1)
  paginator = Paginator(list_posts_raw, 10)
  try:
      list_posts = paginator.page(page)
  except PageNotAnInteger:
      list_posts = paginator.page(1)
  except EmptyPage:
      list_posts = paginator.page(paginator.num_pages)

  return render(request, 'pages/list.html', {
                                              'list_pages': list_posts,
                                              'page_posts': True,
                                              'parent_slug': parent_slug,
                                              'page_slug': page_slug
                                            })