from django.core.exceptions import ValidationError


def validate_image_size(image):
    size = image.file.size
    limit_mb = 1048576
    if size > limit_mb:
        raise ValidationError(f"Image size is {size/limit_mb} MB,"
                              f"but should not exceed 1 MB")
