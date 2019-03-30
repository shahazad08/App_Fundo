from django.contrib import admin
from django.urls import path,include
from django.conf.urls import url, include
from django.views.generic import TemplateView
from users import views
from django.contrib import auth
from django.conf import settings
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer
# from users.swagger_schema import SwaggerSchemaView


schema_view = get_schema_view(title='Fundoo Notes API', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])
if settings.DEBUG:
    urlpatterns = [
        url(r'^swagger/', schema_view, name="docs"),
        path('', TemplateView.as_view(template_name='home.html'), name='home'),  # for a home page
        path('admin/', admin.site.urls),  # for a admin login
        path('', include('users.urls')),
        path('', include('Notes.urls')),
        path('', include('label.urls')),
    ]
else:
    urlpatterns = [
        path('index/', views.logins, name='index'),
]