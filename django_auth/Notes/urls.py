#
from django.conf.urls import url   # A function that takes a prefix, and an arbitrary number of URL patterns,
# and returns a list of URL patterns in the format Django needs.
from django.urls import path

from . import views

urlpatterns = [
    path('api/note/create/', views.create.as_view(), name='create'),  # For Create
    path('api/note/get/', views.get.as_view(), name='get'),
    path('api/note/<int:pk>/deletenote/', views.deletenote.as_view(), name='deletenote'),  # Delete with PK
    path('api/note/<int:pk>/delete/', views.delete.as_view(), name='delete'),  # Delete with PK
    path('api/note/<int:pk>/restore/', views.restore.as_view(), name='restore'),  # Update with Pk
    path('api/note/<int:pk>/update/', views.update.as_view(), name='update'),  # Update with Pk
    path('api/note/<int:pk>/archive/', views.archive.as_view(), name='archive'),  # Update with Pk
    path('api/note/<int:pk>/isarchive/', views.isarchive.as_view(), name='isarchive'),  # Update with Pk
    path('api/note/<int:pk>/color/', views.color.as_view(), name='color'),  # Update with Pk
    path('api/note/<int:pk>/pinned/', views.pinned.as_view(), name='pinned'),  # Update with Pk
    path('api/note/<int:pk>/ispinned/', views.ispinned.as_view(), name='ispinned'),  # Update with Pk
    path('api/note/<int:pk>/copy/', views.copy.as_view(), name='copy'),  # Update with Pk
    path('api/note/remainder/', views.remainder.as_view(), name='remainder'),
    path('api/note/<int:pk>/collaborate/', views.collaborator.as_view(), name='collaborator'),
    path('api/note/<int:note_id>/<int:user_id>collaborator/delete/', views.deletecollaborator.as_view(), name='deletecollaborator'),
    path('api/note/<int:pk>/set_remainder/', views.create_remainder.as_view(),name='set_remainder'),
    path('api/note/pages/', views.PostListAPIView.as_view(), name='pages'),  # Paginate
]