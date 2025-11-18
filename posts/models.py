import math
import re
import uuid

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils.text import slugify

User = get_user_model()


# ==========================
# PATH HELPERS
# ==========================

def avatar_path(instance, filename):
    return f'avatars/{instance.user.username}/{filename}'


def post_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    return f"posts/uploads/{uuid.uuid4()}.{ext}"


# ==========================
# PROFILE MODEL
# ==========================

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    avatar = models.ImageField(
        upload_to=avatar_path,
        default='avatars/default.png',
        blank=True
    )

    full_name = models.CharField(max_length=70, blank=True, null=True)
    designation = models.CharField(max_length=50, blank=True, null=True)

    bio = models.TextField(blank=True, null=True)
    about_author = models.TextField(blank=True, null=True)

    linkedin_url = models.URLField(blank=True, null=True)
    git_url = models.URLField(blank=True, null=True)
    insta_url = models.URLField(blank=True, null=True)

    profile_picture = models.ImageField(
        upload_to=avatar_path,
        blank=True,
        null=True
    )

    # ================================
    # NEW FIELDS ADDED FROM TEAM MODEL
    # ================================

    team_position = models.CharField(max_length=50, blank=True, null=True)
    date_of_birth = models.CharField(max_length=11, blank=True, null=True)
    phoneno = models.CharField(max_length=13, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    about_member = models.TextField(blank=True, null=True)
    github_userid = models.CharField(max_length=30, blank=True, null=True)

    main = models.BooleanField(default=False)
    mainwork = models.CharField(max_length=170, blank=True, null=True)
    mainintro = models.CharField(max_length=570, blank=True, null=True)
    mainlocation = models.CharField(max_length=570, blank=True, null=True)

    show_in_team = models.BooleanField(default=False)

    # ================================

    def __str__(self):
        return self.user.username

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return "/static/defaults/avatar.png"

    def get_absolute_url(self):
        return reverse('resume', kwargs={'id': self.id})


@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


# ==========================
# CATEGORY + TAG MODELS
# ==========================

class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=30, unique=True)

    def __str__(self):
        return self.name


# ==========================
# POST MODEL (UPGRADED)
# ==========================

class Post(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=260, unique=True, blank=True)

    content = models.TextField()  # Quill HTML
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    # New fields
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    read_time = models.IntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="published")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("singleblog", kwargs={"id": self.id})

    @property
    def estimated_read_time(self):
        return f"{self.read_time} min read"


# ==========================
# AUTO SLUG + READ-TIME GENERATOR
# ==========================

@receiver(pre_save, sender=Post)
def auto_generate_post_meta(sender, instance, *args, **kwargs):
    # Slug generation
    if not instance.slug:
        base = slugify(instance.title)
        slug = base
        counter = 1

        while Post.objects.filter(slug=slug).exists():
            slug = f"{base}-{counter}"
            counter += 1

        instance.slug = slug

    # Calculate read time: remove HTML -> count words -> divide 200 wpm
    text_only = re.sub("<[^<]+?>", "", instance.content)
    words = len(text_only.split())
    instance.read_time = max(1, math.ceil(words / 200))


# ==========================
# COMMENT MODEL
# ==========================

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_comments')

    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return f"Comment {self.body} by {self.name}"


# ==========================
# USER PROFILE DETAILS (WORKS WITH FORMSETS)
# ==========================

class ProfileSkill(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    skilltopic = models.CharField(max_length=50)
    skillpercentage = models.IntegerField()

    def __str__(self):
        return self.skilltopic


class ProfileEducation(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    institution = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    from_year = models.CharField(max_length=50)
    to_year = models.CharField(max_length=50)

    def __str__(self):
        return self.institution


class ProfileExperience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experiences')
    institution = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    from_year = models.CharField(max_length=50)
    to_year = models.CharField(max_length=50)

    def __str__(self):
        return self.position
