from django import forms
from tinymce.widgets import TinyMCE

from .models import Post, Comment


class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False


class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCEWidget(
            attrs={'required': False, 'cols': 30, 'rows': 10}
        )
    )

    class Meta:
        model = Post
        fields = ('title', 'overview', 'content', 'thumbnail',
                  'categories', 'featured', 'previous_post', 'next_post')


class CommentForm(forms.ModelForm):
    name = forms.CharField(label="", help_text="", widget=forms.TextInput(attrs={
        'class': 'form-group col-lg-5 col-md-6 name form-control',
        'placeholder': 'Type your Name',
        'id': 'name',
        'rows': '1',
        'required': 'Required'
    }))

    email = forms.CharField(label="", help_text="", widget=forms.EmailInput(attrs={
        'class': 'form-group col-lg-5 col-md-6 email form-control',
        'placeholder': 'Type your Email',
        'id': 'email',
        'rows': '1',
        'required': 'Required'
    }))

    body = forms.CharField(label="", help_text="", widget=forms.Textarea(attrs={
        'class': 'form-group mb-10 form-control',
        'placeholder': 'Type your Comment',
        'id': 'body',
        'rows': '5',
        'required': 'Required'
    }))

    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
