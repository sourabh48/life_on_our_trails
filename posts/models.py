from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from hitcount.models import HitCount

User = get_user_model()


def avatar_path(instance, filename):
    return f'avatars/{instance.user.username}/{filename}'

class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )

    # Main avatar
    avatar = models.ImageField(
        upload_to=avatar_path,
        default='avatars/default.png',
        blank=True
    )

    # Merged fields from Profile + Author
    full_name = models.CharField(max_length=70, blank=True, null=True)
    designation = models.CharField(max_length=50, blank=True, null=True)

    bio = models.TextField(blank=True, null=True)
    about_author = models.TextField(blank=True, null=True)

    linkedin_url = models.URLField(blank=True, null=True)
    git_url = models.URLField(blank=True, null=True)
    insta_url = models.URLField(blank=True, null=True)

    # Optional secondary image
    profile_picture = models.ImageField(
        upload_to=avatar_path,
        blank=True,
        null=True
    )

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


class Category(models.Model):
    title = models.CharField(max_length=50)

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments')
    # NEW: optional link to registered user, for timeline
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_comments')

    name = models.CharField(max_length=80)
    email = models.EmailField()
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_on']

    def __str__(self):
        return 'Comment {} by {}'.format(self.body, self.name)


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    image = models.ImageField(upload_to='posts/', blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Team(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField()
    designation = models.CharField(max_length=50)
    team_position = models.CharField(max_length=50)
    full_name = models.TextField(max_length=70)
    date_of_birth = models.CharField(max_length=11)
    email = models.EmailField()
    phoneno = models.CharField(max_length=13)
    address = models.TextField()
    about_member = models.TextField()
    linkedin_url = models.URLField()
    git_url = models.URLField()
    facebook_url = models.URLField()
    twiter_url = models.URLField()
    github_userid = models.CharField(max_length=30)
    main = models.BooleanField(default=False)
    mainwork = models.CharField(max_length=170, blank=True)
    mainintro = models.CharField(max_length=570, blank=True)
    mainlocation = models.CharField(max_length=570, blank=True)
    main_profile_picture = models.ImageField(blank=True)

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse('member-detail', kwargs={
            'id': self.id
        })


class Skill(models.Model):
    member = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='skill')
    skilltopic = models.CharField(max_length=50)
    skillpercentage = models.IntegerField()

    def __str__(self):
        return self.skilltopic


class Education(models.Model):
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='education')
    institution = models.CharField(max_length=36)
    location = models.CharField(max_length=100)
    from_year = models.CharField(max_length=50)
    to_year = models.CharField(max_length=50)

    def __str__(self):
        return self.institution


class Experience(models.Model):
    team = models.ForeignKey('Team', on_delete=models.CASCADE, related_name='experience')
    institution = models.CharField(max_length=36)
    position = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    from_year = models.CharField(max_length=50)
    to_year = models.CharField(max_length=50)

    def __str__(self):
        return self.institution
