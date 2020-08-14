from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    followers=models.ManyToManyField('self',related_name='followed_to',blank=True, symmetrical=False)
    image = models.ImageField(upload_to='images/',default='default_user.jpg')


class NewPost(models.Model):
    author = models.ForeignKey(User,on_delete=models.CASCADE,related_name = "my_posts")
    content = models.TextField()
    likers = models.ManyToManyField(User,related_name ='liked_posts',blank= True)
    created_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"({self.id})Post by-{self.author.username}"


