from django.urls import path
from . import views
app_name = 'qa_app'

urlpatterns = [
    path('',views.upload_document, name="upload_document")
]
