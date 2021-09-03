from django.urls import include, path
from . import views

urlpatterns = [
  # potser treure per evitar login al public?
  path('admin/login/', views.login_builtin_user, name='login'),
  path('admin/logout/', views.logout_builtin_user, name='logout'),

  # objectes
  path('admin/', views.home_admin, name='list.pages'),
  path('admin/pages/', views.list_pages, name='list.pages'),
  path('admin/pages/<parent_slug>/pages', views.list_pages, name='list.pages'),

  path('admin/pages/add', views.edit_page, name='add.page'),
  path('admin/pages/edit/<page_slug>', views.edit_page, name='edit.page'),
  path('admin/pages/edit/<parent_slug>/<page_slug>', views.edit_page, name='edit.subpage'),

  path('admin/pages/<parent_slug>/add', views.edit_page, name='add.subpage'),

  # altres
  path("robots.txt", views.robots_txt),
  path('<url>', views.view_page, name='view.page'),
  path('', views.view_page, name='view.page'),
]
