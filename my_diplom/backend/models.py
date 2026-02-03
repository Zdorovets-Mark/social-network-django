import os

from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

User = get_user_model()
# Create your models here.

class Publication(models.Model):
    class AccessLevel(models.TextChoices):
        PUBLIC = 'public', 'Public'
        FRIENDS = 'friends', 'Friends Only'
        PRIVATE = 'private', 'Private'

    id_user = models.ForeignKey(User, related_name='publications', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    accessibility = models.CharField(
        max_length=10,
        choices=AccessLevel.choices,
        default=AccessLevel.PUBLIC
    )
    time_created = models.DateTimeField(auto_now_add=True)

    # Sort publication from new to old
    class Meta:
        ordering = ['-time_created']

class Comment(models.Model):
    id_user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    id_publication = models.ForeignKey(Publication, related_name='comments', on_delete=models.CASCADE)
    text = models.TextField(blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['time_created']

class Like(models.Model):
    id_user = models.ForeignKey(User, related_name = 'likes', on_delete=models.CASCADE)
    id_publication = models.ForeignKey(Publication, related_name='likes', on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)

    # one user - one like
    class Meta:
        unique_together = ('id_user', 'id_publication')

class Photo(models.Model):
    id_user = models.ForeignKey(User, related_name='photos', on_delete=models.CASCADE)
    id_publication = models.ForeignKey(
        Publication,
        on_delete=models.CASCADE,
        related_name='photos',
        blank=True,
        null=True
    )
    image = models.ImageField(upload_to='photos/')
    caption = models.CharField(max_length=255, blank=True, null=True)
    time_created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-time_created']


@receiver(post_delete, sender=Photo)
def delete_photo_file(sender, instance, **kwargs):
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)