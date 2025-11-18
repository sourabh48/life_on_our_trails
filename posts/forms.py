from django import forms
from django.forms import inlineformset_factory
from tinymce.widgets import TinyMCE

from .models import (
    Post,
    Comment,
    Profile,
    ProfileEducation,
    ProfileExperience,
    ProfileSkill
)


# =====================================================
# TinyMCE Widget (same as your current config)
# =====================================================
class TinyMCEWidget(TinyMCE):
    def use_required_attribute(self, *args):
        return False


# =====================================================
# Post Form
# =====================================================
class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=TinyMCEWidget(attrs={'cols': 30, 'rows': 10})
    )

    class Meta:
        model = Post
        fields = ['title', 'content', 'image']
        labels = {'image': 'Upload Image'}


# =====================================================
# Comment Form
# =====================================================
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Type your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Type your Email'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Type your Comment',
                'rows': 5,
            }),
        }


# =====================================================
# Profile Main Form
# =====================================================
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'avatar',
            'profile_picture',
            'full_name',
            'designation',
            'bio',
            'about_author',
            'linkedin_url',
            'git_url',
            'insta_url',
            'team_position',
            'date_of_birth',
            'phoneno',
            'address',
            'about_member',
            'github_userid',
            'main',
            'mainwork',
            'mainintro',
            'mainlocation',
            'show_in_team',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'class': 'account-textarea'}),
            'about_author': forms.Textarea(attrs={'rows': 3, 'class': 'account-textarea'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'account-textarea'}),
            'about_member': forms.Textarea(attrs={'rows': 3, 'class': 'account-textarea'}),

        }


# =====================================================
# INLINE FORMSET CUSTOM FORMS — ★ KEY IMPROVEMENT
# These make dynamic Education/Experience/Skill forms
# look like your main "account-input" styled fields.
# =====================================================

COMMON_INPUT = {"class": "account-input", "style": "margin-bottom:12px;"}
COMMON_SMALL = {"class": "account-input", "style": "margin-bottom:12px; max-width:200px;"}


class ProfileEducationForm(forms.ModelForm):
    class Meta:
        model = ProfileEducation
        fields = ["institution", "location", "from_year", "to_year"]
        widgets = {
            "institution": forms.TextInput(attrs=COMMON_INPUT),
            "location": forms.TextInput(attrs=COMMON_INPUT),
            "from_year": forms.TextInput(attrs=COMMON_SMALL),
            "to_year": forms.TextInput(attrs=COMMON_SMALL),
        }


class ProfileExperienceForm(forms.ModelForm):
    class Meta:
        model = ProfileExperience
        fields = ["institution", "position", "location", "from_year", "to_year"]
        widgets = {
            "institution": forms.TextInput(attrs=COMMON_INPUT),
            "position": forms.TextInput(attrs=COMMON_INPUT),
            "location": forms.TextInput(attrs=COMMON_INPUT),
            "from_year": forms.TextInput(attrs=COMMON_SMALL),
            "to_year": forms.TextInput(attrs=COMMON_SMALL),
        }


class ProfileSkillForm(forms.ModelForm):
    class Meta:
        model = ProfileSkill
        fields = ["skilltopic", "skillpercentage"]
        widgets = {
            "skilltopic": forms.TextInput(attrs=COMMON_INPUT),
            "skillpercentage": forms.NumberInput(attrs=COMMON_SMALL),
        }


# =====================================================
# INLINE FORMSETS USING CUSTOM FORMS
# =====================================================

EducationFormSet = inlineformset_factory(
    Profile,
    ProfileEducation,
    form=ProfileEducationForm,
    extra=1,
    can_delete=True,
)

ExperienceFormSet = inlineformset_factory(
    Profile,
    ProfileExperience,
    form=ProfileExperienceForm,
    extra=1,
    can_delete=True,
)

SkillFormSet = inlineformset_factory(
    Profile,
    ProfileSkill,
    form=ProfileSkillForm,
    extra=1,
    can_delete=True,
)
