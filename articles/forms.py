from django import forms
from models import Articles

class NewForm(forms.ModelForm):
    class Meta:
        model = Articles
        fields = ['title', 'category', 'source', 'sourceurl', 'team', 'label', 'content']

class TopicForm(forms.ModelForm):
    class Meta:
        model = Articles
        fields = ['title', 'category', 'category2', 'label', 'content']
