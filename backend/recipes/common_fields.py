import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from foodgram.utils import ImageUploadToFactory


class FieldSlug(models.Model):
    slug = models.SlugField(
        verbose_name=_('slug'),
        unique=True,
        max_length=100,
        default=uuid.uuid1
    )

    class Meta(object):
        abstract = True


class FieldVisible(models.Model):
    is_visible = models.BooleanField(
        verbose_name=_('is visible'),
        default=True
    )

    class Meta(object):
        abstract = True


class FieldCreated(models.Model):
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('created')
    )

    class Meta(object):
        abstract = True


class FieldUpdated(models.Model):
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_('updated')
    )

    class Meta(object):
        abstract = True


class FieldSorting(models.Model):
    sorting = models.PositiveIntegerField(
        verbose_name=_('sorting'),
        default=0
    )

    class Meta(object):
        abstract = True


class FieldImage(models.Model):
    image = models.ImageField(
        verbose_name=_('image'),
        help_text=_('image size no more than 1920х960px'),
        upload_to=ImageUploadToFactory('images')
    )

    class Meta(object):
        abstract = True


class FieldSEO(models.Model):
    title = models.CharField(
        verbose_name=_('title of page'),
        max_length=255,
        blank=True,
        null=True
    )
    descriptions = models.CharField(
        verbose_name=_('meta descriptions'),
        max_length=255,
        blank=True,
        null=True
    )
    keywords = models.CharField(
        verbose_name=_('meta keywords'),
        max_length=510,
        blank=True,
        null=True
    )

    class Meta(object):
        abstract = True


class FieldAuthor(models.Model):
    author = models.CharField(
        verbose_name=_('author'),
        max_length=255
    )

    class Meta(object):
        abstract = True
