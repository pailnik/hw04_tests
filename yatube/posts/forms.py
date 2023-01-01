from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        labels = {
            'group': 'группа',
            'text': 'пост',
        }
        fields = ('text', 'group', 'image')


class CommentForm(forms.ModelForm):
    pass
