from django.urls import include, path
from . import views

urlpatterns = [
  # potser treure per evitar login al public?
  path('admin/login', views.login_builtin_user, name='login'),
  path('admin/logout', views.logout_builtin_user, name='logout'),

  # objectes
  path('admin', views.home_admin, name='list.pages'),
  path('admin/', views.home_admin, name='list.pages'),

  # pages

  path('admin/pages/', views.list_pages, name='list.pages'),
  path('admin/pages/<parent_slug>/pages', views.list_pages, name='list.subpages'),

  path('admin/pages/add', views.edit_page, name='add.page'),
  path('admin/pages/<parent_slug>/add', views.edit_page, name='add.subpage'),

  path('admin/pages/<page_slug>/edit', views.edit_page, name='edit.page'),
  path('admin/pages/<parent_slug>/<page_slug>/edit', views.edit_page, name='edit.subpage'),

  path('admin/pages/<page_slug>/delete', views.delete_page, name='delete.page'),
  path('admin/pages/<parent_slug>/<page_slug>/delete', views.delete_page, name='delete.subpage'),

  # posts

  path('admin/pages/<page_slug>/posts/add', views.edit_post, name='add.page.post'),
  path('admin/pages/<parent_slug>/<page_slug>/posts/add', views.edit_post, name='add.subpage.post'),

  path('admin/pages/<page_slug>/posts', views.list_posts, name='list.page.posts'),
  path('admin/pages/<parent_slug>/<page_slug>/posts', views.list_posts, name='list.subpage.posts'),

  path('admin/posts/<post_id>/<post_slug>', views.edit_post, name='edit.post'),

  path('admin/posts/<page_id>/<page_slug>/delete', views.delete_page, name='delete.page'),

  # attachments

  path('admin/pages/<page_slug>/attachments', views.page_attachments, name='page.attachments'),
  path('admin/pages/<parent_slug>/<page_slug>/attachments', views.page_attachments, name='subpage.attachments'),
  
  path('admin/pages/<page_slug>/<post_slug>/attachments', views.page_attachments, name='page.post.attachments'),
  path('admin/pages/<parent_slug>/<page_slug>/<post_slug>/attachments', views.page_attachments, name='subpage.post.attachments'),

  path('admin/attachments/<attachment_id>/delete', views.remove_page_attachment, name='attachment.delete'),

  # altres
  path("robots.txt", views.robots_txt),

  # attachment redirector

  path('attachments/<attachment_id>', views.attachment_to_url, name='attachments.to.url'),

  # views

  path('<page_slug>', views.view_page_by_slug, name='view.page.by.slug'),
  path('<parent_slug>/<page_slug>', views.view_page_by_slug, name='view.subpage.by.slug'),
  path('<parent_slug>/<page_slug>/<post_slug>', views.view_page_by_slug, name='view.subpage.by.slug'),
  #path('<url>', views.view_page, name='view.page'),
  path('', views.view_page, name='view.page'),
]
