from django.db import models
import uuid
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin, Group, Permission

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username=None, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        if not username:
            username = email.split('@')[0]
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username=None, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if 'mobile' in extra_fields:
            del extra_fields['mobile']
        return self.create_user(email, username, password=password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=200, unique=True)
    user_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    firstname = models.CharField(max_length=200, null=True)
    lastname = models.CharField(max_length=200, null=True)
    mobile = models.IntegerField(default=234)
    created = models.DateTimeField(auto_now_add=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # Override these fields to avoid clashes
    groups = models.ManyToManyField(
        Group,
        related_name='customuser_set',
        blank=True,
        help_text="The groups this user belongs to."
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='customuser_permissions_set',
        blank=True,
        help_text="Specific permissions for this user."
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'firstname', 'lastname']

    def __str__(self):
        return str(self.username)

# class Waterflow(models.Model):
#     user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
#     created = models.DateTimeField(auto_now_add=True)
#     title = models.CharField(max_length=200)

#     def __str__(self):
#         return self.title

#     class Meta:
#         order_with_respect_to = 'user'
