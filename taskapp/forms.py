from django import forms
from .models import Task

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['task_type','description','deadline','responsible','status']
        widgets = {'deadline': forms.DateTimeInput(attrs={'type':'datetime-local'})}
        labels = {
            'task_type': 'Тип',
            'description': 'Описание',
            'deadline': 'Дедлайн',
            'responsible': 'Ответственный',
            'status': 'Статус',
        }
