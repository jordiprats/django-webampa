from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Q

from www.models import *
from www.forms import *

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

@require_GET
def robots_txt(request):
  lines = [
      "User-Agent: *",
      "Disallow: /admin/",
  ]
  return HttpResponse("\n".join(lines), content_type="text/plain")

def get_main_nav():
  list_root_pages = Page.objects.filter(parent=None, status=PAGE_STATUS_PUBLIC).filter(~Q(slug="ampa"))

  nav = {}
  for page in list_root_pages:
    nav[page.title] = page.slug

  return nav

def view_page(request, url=None):
  print('view_page')
  parent_slug=None
  if not url:
    page_slug='ampa'
  else:
    #TODO: aqui separar page de page
    page_slug=url
  
  page_instance = Page.objects.filter(parent__slug=parent_slug, slug=page_slug, status=PAGE_STATUS_PUBLIC).first()

  if not page_instance:
    raise Http404("Aquesta pàgina no existeix")

  return render(request, 'pages/view.html', { 
                                              'page': page_instance,
                                              'root_nav': get_main_nav()
                                            })

@login_required
def home_admin(request, url=None):
  return redirect('list.pages')

@login_required
def edit_page(request, parent_slug=None, page_slug=None):
  try:
    if parent_slug:
      parent_instance = Page.objects.filter(slug=parent_slug).first()
    try:
      page_instance = Page.objects.filter(parent__slug=parent_slug, slug=page_slug).first()
    except:
      if parent_slug:
        page_instance = Page(parent=parent_instance)
      else:
        page_instance = Page()

    if request.method == 'POST':
      form = PageForm(request.POST, instance=page_instance)
      if form.is_valid():
        page_instance = form.save(commit=False)
        if parent_slug:
          page_instance.parent = parent_instance
        page_instance.save()
        messages.info(request, 'Pàgina guardada correctament')
        if parent_slug:
          return redirect('list.subpages', parent_slug=parent_slug)
        else:
          return redirect('list.pages')
      else:
        messages.error(request, 'Formulari incorrecte')
        return render(request, 'pages/edit.html', { 
                                                    'form': form, 
                                                    'page': page_instance, 
                                                    'parent_slug': parent_slug,
                                                 })
    else:
      form = PageForm(instance=page_instance)
      return render(request, 'pages/edit.html', { 
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
                                              'parent_slug': parent_slug
                                            })