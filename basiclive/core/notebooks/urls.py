from django.urls import path

from . import views

app_name = "notebooks"

urlpatterns = [
    path('', views.NotebookList.as_view(), name='notebook-list'),
    path('new/', views.CreateNotebook.as_view(), name='create-notebook'),
    path('<uuid:pk>/', views.NotebookDetail.as_view(), name='notebook-detail'),
    path('<uuid:pk>/edit/', views.UpdateNotebook.as_view(), name='notebook-edit'),
    path('<uuid:pk>/add/', views.SaveEntry.as_view(), name='create-entry'),
    path('<uuid:book>/delete/<int:pk>/', views.DeleteEntry.as_view(), name='delete-entry'),
    path('<uuid:pk>/dates/', views.NotebookDates.as_view(), name='notebook-dates'),
    path('<uuid:pk>/annotate/', views.AnnotateEntry.as_view(), name='annotate-notebook'),
    path('<uuid:pk>/tag/', views.TagEntry.as_view(), name='tag-notebook'),
    path('entry/<int:pk>/', views.EntryData.as_view(), name='entry-data'),
]
