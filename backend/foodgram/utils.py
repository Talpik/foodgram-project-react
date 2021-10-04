import os
from uuid import uuid4

from django.conf import settings
from django.utils.deconstruct import deconstructible


@deconstructible
class ImageUploadToFactory(object):

    def __init__(self, parent):
        self.parent = parent

    def __call__(self, instance, filename):
        path = os.path.join(settings.MEDIA_ROOT, self.parent)
        if not os.path.exists(path):
            os.makedirs(path)
        ext = filename.split(".")[-1] if "." in filename else "unknown"
        path = os.path.join(str(instance.id or 0), "%s.%s" % (uuid4(), ext))
        return os.path.join(self.parent, path)
