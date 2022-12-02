from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel
from django.conf import settings


User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='текст поста',
        help_text='Введите текст поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        help_text='Автор поста',
        related_name='posts',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        verbose_name='группа',
        help_text='Группа, к которой будет относиться пост',
        related_name='posts',
    )
    image = models.ImageField(
        verbose_name='картинка',
        help_text='Картинка поста',
        upload_to='posts/',
        blank=True,
    )

    def __str__(self) -> str:
        return self.text[:settings.POST_CHARS_VIEWED]


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='пост',
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='автор',
        related_name='comments'
    )
    text = models.TextField(
        verbose_name='текст комментария'
    )

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.text[:settings.POST_CHARS_VIEWED]


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='отслеживаемый автор',
        related_name='following',
        on_delete=models.CASCADE,
    )

    class Meta:
        constraints = [
            models.constraints.UniqueConstraint(
                name='subscription_unique',
                fields=['user', 'author']
            ),
        ]
