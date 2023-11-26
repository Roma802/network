import datetime

from django.contrib.sessions.backends.db import SessionStore
from django.utils import timezone

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.urls import reverse
from taggit.managers import TaggableManager
from django.dispatch import receiver
from django.contrib import messages


class User(AbstractUser):
    following = models.ManyToManyField('self', through='Contact', related_name='followers',
                                        symmetrical=False)
    # photo = models.ImageField(upload_to='images/', null=True, blank=True)

    def get_absolute_url(self):
        return reverse('user_profile', args=[str(self.username)])


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='uploads/', null=True, blank=True, help_text='Choose a file to upload')
    file_media_type = models.CharField(max_length=32, null=True, blank=True)
    tags = TaggableManager(blank=True)
    like = models.ManyToManyField(User, default=None, blank=True, related_name='like')

    class Meta:
        indexes = [
            models.Index(fields=['-created_at']),
        ]
        ordering = ['-created_at']

    def get_absolute_url(self):
        return reverse('post_detail', args=(str(self.pk), ))

    def save(self, *args, **kwargs):
        if '.' + self.file.path.split('.')[-1] == '.mp4':
            self.file_media_type = 'video'
        elif '.' + self.file.path.split('.')[-1].lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp',
                '.tiff', '.tif', '.webp', '.svg', '.heif,' '.heic',  '.raw']:
            self.file_media_type = 'image'
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.author} post: {self.text[:20]}...'


@receiver(post_save, sender=Post)
def handler_post_tags(sender, instance, **kwargs):
    new_text = instance.text.replace('\n', ' ')
    if '#' in instance.text:
        for i in new_text.split(' '):
            if i.startswith('#'):
                instance.tags.add(i)
    for tag in instance.tags.all():
        if tag.name not in new_text.split(' '):
            instance.tags.remove(tag)


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    profile_image = models.ImageField(upload_to='profile_images', null=True, blank=True)

    def __str__(self):
        return str(self.user)


class Contact(models.Model):
    user_from = models.ForeignKey(User, related_name='rel_from_set', on_delete=models.CASCADE)
    user_to = models.ForeignKey(User, related_name='rel_to_set', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return f'{self.user_from} follows {self.user_to}'


class Comment(models.Model):
    auction = models.ForeignKey(Post, on_delete=models.CASCADE)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment of {self.commenter}'


class Bookmarks(models.Model):  # список сохраненных постов пользователя
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True)
    post = models.ManyToManyField(Post)

    def __str__(self):
        return f'{str(self.user)} save this post - {self.post}'


class Notification(models.Model):
    is_seen = models.BooleanField(default=False)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        now = timezone.now()
        last_minute = now - datetime.timedelta(seconds=60)
        duplicated_actions = Notification.objects.filter(is_seen=self.is_seen, message=self.message,
                                                         user=self.user, timestamp__gte=last_minute)
        if not duplicated_actions:
            super().save(*args, **kwargs)




