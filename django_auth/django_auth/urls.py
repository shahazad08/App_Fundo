from django.contrib import admin
from django.urls import path,include
from django.conf.urls import url, include
from django.views.generic import TemplateView
# admin.autodiscover()
from users import views
from django.contrib import auth
from rest_framework.schemas import get_schema_view
from rest_framework_swagger.renderers import SwaggerUIRenderer, OpenAPIRenderer
# from users.swagger_schema import SwaggerSchemaView
# from django_auth import settings


schema_view = get_schema_view(title='Fundoo Notes API', renderer_classes=[OpenAPIRenderer, SwaggerUIRenderer])
urlpatterns = [
    path('', TemplateView.as_view(template_name='home.html'), name='home'),  # for a home page
    path('admin/', admin.site.urls),  # for a admin login
    path('', include('users.urls')),
    path('', include('Notes.urls')),
    path('', include('label.urls')),
    # url(r'^swagger/', SwaggerSchemaView.as_view()),


    url(r'^swagger/', schema_view, name="docs"),
]

# if DEBUG:
#     urlpatterns = [
#         url(r'^docs/', schema_view),
#     ]
# else:
#     urlpatterns = [
#         path('', TemplateView.as_view(template_name='home.html'), name='home'),  # for a home page
#         path('admin/', admin.site.urls),  # for a admin login
#         path('', include('users.urls')),
#         path('', include('Notes.urls')),
#         path('', include('label.urls')),
#     # url(r'^swagger/', SwaggerSchemaView.as_view()),

