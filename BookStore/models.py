from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
class Book(models.Model):
    id = models.IntegerField(null=False,primary_key=True)
    title = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    statue = models.CharField(max_length=1, choices=[('F', 'Free'), ('P', 'Paid')])
    price = models.DecimalField(null=False,max_digits=5, decimal_places=2,default=0.00)
    def __str__(self):
        return self.title

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.user.username
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        instance.profile.save()