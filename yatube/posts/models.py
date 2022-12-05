from django.db import models
from django.contrib.auth import get_user_model
# from django.db.models import TextField

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, unique=True, verbose_name='title')
    slug = models.SlugField(unique=True, verbose_name='slug')
    description = models.TextField(verbose_name='description')

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:15]
