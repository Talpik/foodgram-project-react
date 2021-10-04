from django.contrib.auth.models import BaseUserManager


class AppUserManager(BaseUserManager):
    """
    AppUser model instantiation manager.
    Allows you to separate the logic for creating
    regular users and superusers.
    """
    def create_user(self, email: str, username: str,
                    first_name: str, last_name: str,
                    password: str = None):
        if not email:
            raise ValueError("Email address for AppUser object is not found")
        user = self.model(
            email=self.normalize_email(email),
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email: str, username: str,
                         first_name: str, last_name: str,
                         password: str = None):
        user = self.create_user(
            email=email,
            password=password,
            username=username,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_active = True
        user.is_admin = True
        user.is_staff = True
        user.save(using=self._db)
        return user
