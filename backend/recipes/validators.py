from django.core.exceptions import ValidationError


def validate_image_size(image):
    size = image.file.size
    limit_mb = 1048576
    if size > limit_mb:
        raise ValidationError(f"Размер изображения составляет {size/limit_mb} МБайт,"
                              f"а должен не превышать 1 МБайта ")
