# This file previously contained the CustomUser and CustomUserManager.
# They have been moved to accounts/models.py.

from django.db import models
from django.utils.translation import gettext_lazy as _

class News(models.Model):
    title = models.CharField(_('title'), max_length=200)
    content = models.TextField(_('content'))
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    is_dummy = models.BooleanField(_('is dummy data'), default=False, help_text=_('Mark as dummy for easy removal'))

    class Meta:
        verbose_name = _('news item')
        verbose_name_plural = _('news items')
        ordering = ['-created_at']

    def __str__(self):
        return self.title
