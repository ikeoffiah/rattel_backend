from rest_framework import serializers
from .models import Project


class WebLinkSerializer(serializers.ModelSerializer):
    link = serializers.CharField()
    class Meta:
        model = Project
        fields = ['link','project_name']

    def validate(self, attrs):
        project_name = attrs.get('project_name')

        if Project.objects.filter(project_name=project_name).exists():
            raise serializers.ValidationError('project with this name already exist')
        return attrs



class QuerySerializer(serializers.Serializer):
    query_data = serializers.CharField()
    project_name = serializers.CharField()

    def validate(self, attrs):
        project_name = attrs.get('project_name')

        if not Project.objects.filter(project_name=project_name).exists():
            raise serializers.ValidationError('Project does not exist')
        return attrs


class ProjectsSerializer(serializers.Serializer):
    project_name = serializers.CharField()


class FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    project_name = serializers.CharField()
