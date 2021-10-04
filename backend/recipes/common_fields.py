import uuid

from django.db import models
from foodgram.utils import ImageUploadToFactory


class AbstractSlug(models.Model):
    """
    Model with slug field for reuse.
    """
    slug = models.SlugField(
        verbose_name="slug",
        unique=True,
        max_length=100,
        default=uuid.uuid1
    )


class AbstractVisible(models.Model):
    """
    Model with boolean field for reuse.
    """
    is_visible = models.BooleanField(
        verbose_name="is visible",
        default=True
    )


class AbstractCreated(models.Model):
    """
    Model with data time field for reuse.
    """
    created = models.DateTimeField(
        auto_now_add=True,
        verbose_name="created"
    )


class AbstractUpdated(models.Model):
    """
    Model with data time field for reuse.
    """
    updated = models.DateTimeField(
        auto_now=True,
        verbose_name="updated"
    )


class AbstractSorting(models.Model):
    """
    Model with positive integer field for reuse.
    """
    sorting = models.PositiveIntegerField(
        verbose_name="sorting",
        default=0
    )


class AbstractImage(models.Model):
    """
    Model with image field for reuse.
    """
    image = models.ImageField(
        verbose_name="image",
        help_text="image size no more than 1MB",
        upload_to=ImageUploadToFactory("images")
    )


class AbstractAuthor(models.Model):
    """
    Model with author field for reuse.
    """
    author = models.CharField(
        verbose_name="author",
        max_length=255
    )
