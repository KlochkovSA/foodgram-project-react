from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Follow(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User,
                             related_name='follower',
                             verbose_name='Подписчик',
                             on_delete=models.CASCADE
                             )
    author = models.ForeignKey(User,
                               related_name='following',
                               verbose_name='Автор',
                               on_delete=models.CASCADE
                               )
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if self.author == self.user:
            raise Exception('Author cannot follow himself')
        super(Follow, self).save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'user'],
                condition=~models.Q(user=models.F('author')),
                name='no_self_subscription'
            ),
        ]
        ordering = ['-created']
