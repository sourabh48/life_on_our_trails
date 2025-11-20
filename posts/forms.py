import re

from django import forms
from django.forms import inlineformset_factory
from django.utils import timezone
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
class PostCreateForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )

    new_category = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Add new category",
            }
        ),
    )

    new_tags = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    tags = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )

    publish_at = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control",
            }
        ),
    )

    class Meta:
        model = Post
        fields = [
            "title",
            "content",
            "category",
            "tags",
            "image",
            "status",
            "publish_at",
            "meta_title",
            "meta_description",
        ]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Catchy post title…",
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control", "id": "id_image"}),
            "status": forms.Select(attrs={"class": "form-control"}),
            "meta_title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Meta title (optional)",
                    "maxlength": "70",
                }
            ),
            "meta_description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 2,
                    "placeholder": "Short SEO description for search results…",
                    "maxlength": "160",
                }
            ),
        }

    # helpers
    def _plain_text(self, html):
        return re.sub(r"<[^>]+>", " ", html or "").strip()

    def _word_count(self, html):
        if not html:
            return 0
        return len(re.findall(r"\w+", self._plain_text(html)))

    def clean_publish_at(self):
        publish_at = self.cleaned_data.get("publish_at")
        status = self.cleaned_data.get("status")

        if status == "scheduled":
            if not publish_at:
                raise forms.ValidationError("Please pick a publish date & time for scheduled posts.")
            if publish_at <= timezone.now():
                raise forms.ValidationError("Scheduled time must be in the future.")
        return publish_at

    def clean(self):
        cleaned = super().clean()
        title = (cleaned.get("title") or "").strip()
        content_html = cleaned.get("content") or ""
        image = cleaned.get("image")
        status = cleaned.get("status")
        category = cleaned.get("category")
        new_category = (cleaned.get("new_category") or "").strip()
        tags_raw = (cleaned.get("tags") or "").strip()
        new_tags = (cleaned.get("new_tags") or "").strip()

        words = self._word_count(content_html)

        if words == 0:
            self.add_error("content", "Please write some content before saving.")

        existing_tag_ids = [t.strip() for t in tags_raw.split(",") if t.strip()]
        has_existing = bool(existing_tag_ids)
        has_new = bool(new_tags)

        strict = status in ("published", "scheduled")
        if strict:
            if not title or len(title) < 10:
                self.add_error("title", "Title must be at least 10 characters to publish.")
            if not image:
                self.add_error("image", "Featured image is required to publish.")
            if not category and not new_category:
                self.add_error("category", "Pick a category or create a new one to publish.")
            if not has_existing and not has_new:
                self.add_error("tags", "Select at least one tag or add new tags to publish.")
            if words < 500:
                self.add_error("content", "To publish, please write at least 500 words.")

        return cleaned

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
