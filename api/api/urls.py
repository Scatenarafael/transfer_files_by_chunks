from core import settings
from django.conf.urls.static import static
from django.urls import path

from api.views.receive_files import (
    AsyncChunkedFileUploadView,
    AsyncFileUploadView,
)
from api.views.task_view import TaskView

# from django.urls import path
# from rest_framework.routers import DefaultRouter


app_name = "api"
# router = DefaultRouter()
# router.register(r"task", TaskView)

urlpatterns = [
    path(r"task/", TaskView.as_view()),
    path(r"upload/", AsyncChunkedFileUploadView.as_view()),
    path(r"upload/standard/", AsyncFileUploadView.as_view()),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns += router.urls

if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
