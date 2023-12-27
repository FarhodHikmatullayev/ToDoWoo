from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.todo.serializers import TaskSerializer
from apps.todo.models import Task
from shared.pagination import CustomPagination


class CurrentTaskListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        tasks = Task.objects.filter(author=user, is_completed=False)
        pagination = CustomPagination()
        page_obj = pagination.paginate_queryset(tasks, request)
        serializer = TaskSerializer(page_obj, many=True)
        return pagination.get_paginated_response(data=serializer.data)


class CompletedTaskListAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        user = self.request.user
        tasks = Task.objects.filter(author=user, is_completed=True)
        pagination = CustomPagination()
        page_obj = pagination.paginate_queryset(tasks, request)
        serializer = TaskSerializer(page_obj, many=True)
        return pagination.get_paginated_response(data=serializer.data)


class TaskDetailAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk):
        task = get_object_or_404(Task.objects.all(), id=pk)
        user = self.request.user
        if not task.author == user:
            raise ValidationError(
                {
                    'success': False,
                    'detail': 'This task is not yours, you are not permission'
                }
            )
        serializer = TaskSerializer(task)
        return Response(
            {
                'success': True,
                'data': serializer.data,
                'status': status.HTTP_200_OK
            }
        )


class TaskCreateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request):
        data = self.request.data
        user = self.request.user
        data['author_id'] = user.id
        serializer = TaskSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'success': True,
                'data': serializer.data,
                'status': status.HTTP_200_OK
            }
        )


class ToCompleteAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, pk):
        task = get_object_or_404(Task.objects.all(), id=pk)
        user = self.request.user
        if not task.author == user:
            raise ValidationError(
                {
                    'success': False,
                    'detail': 'This task is not yours, you are not permission'
                }
            )
        task.is_completed = True
        task.save()
        return Response(
            {
                'success': True,
                'detail': 'Your task successfully completed',
                'status': status.HTTP_200_OK
            }
        )


class TaskUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk):
        task = get_object_or_404(Task.objects.all(), id=pk)
        user = self.request.user
        if not task.author == user:
            raise ValidationError(
                {
                    'success': False,
                    'detail': 'This task is not yours, you are not permission'
                }
            )
        data = self.request.data
        data['author_id'] = user.id
        serializer = TaskSerializer(data=data, instance=task)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'success': True,
                'data': serializer.data,
                'status': status.HTTP_200_OK
            }
        )

    def patch(self, request, pk):
        task = get_object_or_404(Task.objects.all(), id=pk)
        user = self.request.user
        if not task.author == user:
            raise ValidationError(
                {
                    'success': False,
                    'detail': 'This task is not yours, you are not permission'
                }
            )
        data = self.request.data
        data['author_id'] = user.id
        serializer = TaskSerializer(data=data, instance=task, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            {
                'success': True,
                'data': serializer.data,
                'status': status.HTTP_200_OK
            }
        )


class TaskDeleteAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk):
        task = get_object_or_404(Task.objects.all(), id=pk)
        user = self.request.user
        if task.author == user:
            task.delete()
            return Response(
                {
                    'success': True,
                    'detail': 'You successfully deleted your task',
                    'status': status.HTTP_200_OK
                }
            )
        else:
            raise ValidationError(
                {
                    'success': False,
                    'detail': 'This task is not yours, you are not permission'
                }
            )
