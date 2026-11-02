from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from apps.core import views

admin.site.site_header = 'مدیریت استادان فناوری پویا'
admin.site.site_title = 'Dynamic Tech Experts'
urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('', views.home, name='home'),
    path('products/', views.product_list, name='product_list'),
    path('products/<str:slug>/', views.product_detail, name='product_detail'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<str:slug>/', views.project_detail, name='project_detail'),
    path('engineering/', views.engineering, name='engineering'),
    path('company/', views.company, name='company'),
    path('contact/', views.contact, name='contact'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
