from django.urls import path

from apps.todo.views import CurrentTaskListAPIView, TaskDeleteAPIView, TaskDetailAPIView, TaskUpdateAPIView, \
    TaskCreateAPIView, CompletedTaskListAPIView, ToCompleteAPIView

app_name = 'todo'

urlpatterns = [
    path('current/list/', CurrentTaskListAPIView.as_view()),
    path('completed/list/', CompletedTaskListAPIView.as_view()),
    path('create/', TaskCreateAPIView.as_view()),
    path('detail/<int:pk>/', TaskDetailAPIView.as_view()),
    path('delete/<int:pk>/', TaskDeleteAPIView.as_view()),
    path('update/<int:pk>/', TaskUpdateAPIView.as_view()),
    path('to_complete/<int:pk>/', ToCompleteAPIView.as_view()),
]
