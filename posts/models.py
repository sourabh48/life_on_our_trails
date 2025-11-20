import re
import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
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
# CATEGORY + TAG MODELS + post
# ==========================

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            slug = base
            counter = 1
            while Category.objects.filter(slug=slug).exclude(id=self.id).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:100]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_CHOICES = (
        ("draft", "Draft"),
        ("published", "Published"),
        ("scheduled", "Scheduled"),
    )

    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=260, unique=True, blank=True)

    content = models.TextField(blank=True)  # Quill HTML
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    tags = models.ManyToManyField(Tag, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    publish_at = models.DateTimeField(null=True, blank=True)

    read_time = models.PositiveIntegerField(default=1)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="draft")

    # SEO
    meta_title = models.CharField(max_length=70, blank=True, default="")
    meta_description = models.CharField(max_length=180, blank=True, default="")

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("singleblog", kwargs={"id": self.id})

    @property
    def estimated_read_time(self):
        return f"{self.read_time} min read"

    def _plain_text(self):
        """Strip HTML to estimate words & SEO snippets."""
        return re.sub(r"<[^>]+>", " ", self.content or "").strip()

    def _word_count(self):
        if not self.content:
            return 0
        return len(re.findall(r"\w+", self._plain_text()))

    def save(self, *args, **kwargs):
        # Slug
        if not self.slug:
            base_slug = slugify(self.title)[:240]
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug

        # Read time
        words = self._word_count()
        self.read_time = max(1, round(words / 200)) if words else 1

        # SEO fallbacks
        if not self.meta_title:
            self.meta_title = (self.title or "")[:70]

        if not self.meta_description:
            pt = self._plain_text()
            self.meta_description = pt[:175]

        super().save(*args, **kwargs)


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
