from rest_framework import serializers

from apps.todo.models import Task
from apps.users.serializers import UserSerializer


class TaskSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    author_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Task
        fields = '__all__'
        extra_kwargs = {
            'created_time': {
                'read_only': True,
                'required': False,
            },
            'updated_time': {
                'read_only': True,
                'required': False,
            }
        }

