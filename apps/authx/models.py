from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

class MyUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, username, email, password=None, **extra_fields):
        if not username or not email:
            raise ValueError("Must set both username and email")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff",   True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)
    
class User(AbstractBaseUser, PermissionsMixin):
    users_id    = models.AutoField(primary_key=True, db_column='UsersID')
    first_name  = models.CharField(max_length=150, db_column='FirstName')
    last_name   = models.CharField(max_length=150, db_column='LastName')
    email       = models.EmailField(unique=True, db_column='Email')
    username    = models.CharField(max_length=150, unique=True, db_column='Username')
    password    = models.CharField(max_length=128, db_column='Password')
    status      = models.CharField(max_length=50, db_column='Status')
    is_active   = models.BooleanField(default=False, db_column='is_active')
    is_staff    = models.BooleanField(default=False, db_column='is_staff')
    created_at  = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at  = models.DateTimeField(auto_now=True,     db_column='updated_at')
    soft_delete = models.BooleanField(default=False,      db_column='Soft_delete')
    deleted_at  = models.DateTimeField(null=True, blank=True, db_column='deleted_at')

       # Required for Django’s auth:
    #objects = MyUserManager()
    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    # Admin/UI flags
    is_active = models.BooleanField(default=True, db_column='is_active')
    is_staff  = models.BooleanField(default=False, db_column='is_staff')

    class Meta:
        db_table = 'Users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username


class Role(models.Model):
    role_id         = models.AutoField(primary_key=True, db_column='RoleID')
    role_name       = models.CharField(max_length=100, db_column='RoleName')
    role_description= models.TextField(db_column='RoleDescription')
    created_at      = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at      = models.DateTimeField(auto_now=True,     db_column='updated_at')

    class Meta:
        db_table = 'Roles'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.role_name


class Permission(models.Model):
    permission_id   = models.AutoField(primary_key=True, db_column='PermissionID')
    permission_name = models.CharField(max_length=100, db_column='PermissionName')
    created_at      = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at      = models.DateTimeField(auto_now=True,     db_column='updated_at')

    class Meta:
        db_table = 'Permission'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'

    def __str__(self):
        return self.permission_name


class RolePermission(models.Model):
    role_permission_id = models.AutoField(primary_key=True, db_column='RolePermissionID')
    role               = models.ForeignKey(Role,       on_delete=models.CASCADE, db_column='RoleID')
    permission         = models.ForeignKey(Permission, on_delete=models.CASCADE, db_column='PermissionID')

    class Meta:
        db_table = 'RolePermission'
        verbose_name = 'Role Permission'
        verbose_name_plural = 'Role Permissions'
        unique_together = (('role', 'permission'),)

    def __str__(self):
        return f"{self.role.role_name} → {self.permission.permission_name}"


class UsersRole(models.Model):
    user_role_id = models.AutoField(primary_key=True, db_column='UserRoleID')
    user         = models.ForeignKey(User, on_delete=models.CASCADE, db_column='UserID')
    role         = models.ForeignKey(Role, on_delete=models.CASCADE, db_column='RoleID')

    class Meta:
        db_table = 'UsersRole'
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        unique_together = (('user', 'role'),)

    def __str__(self):
        return f"{self.user.username} → {self.role.role_name}"

class Company(models.Model):
    id         = models.AutoField(primary_key=True, db_column='id')
    name       = models.CharField(max_length=255, db_column='name')
    address    = models.TextField(db_column='address')
    website    = models.CharField(max_length=255, db_column='website')
    created_at = models.DateTimeField(auto_now_add=True, db_column='created_at')
    updated_at = models.DateTimeField(auto_now=True,     db_column='updated_at')

    class Meta:
        db_table = 'Company'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'

    def __str__(self):
        return self.name


class CompanyUser(models.Model):
    id         = models.AutoField(primary_key=True, db_column='id')
    user       = models.ForeignKey(
                    User,
                    on_delete=models.CASCADE,
                    db_column='user_id',
                    related_name='company_memberships'
                )
    company    = models.ForeignKey(
                    Company,
                    on_delete=models.CASCADE,
                    db_column='company_id',
                    related_name='users'
                )

    class Meta:
        db_table = 'CompanyUser'
        verbose_name = 'Company User'
        verbose_name_plural = 'Company Users'
        unique_together = (('user', 'company'),)

    def __str__(self):
        return f"{self.user.username} → {self.company.name}"


class UserProfile(models.Model):
    id = models.AutoField(
        primary_key=True,
        db_column='id'
    )
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        db_column='user_id',
        related_name='profile'
    )
    phone = models.CharField(
        max_length=50,
        db_column='phone',
        null=True,
        blank=True
    )
    location = models.CharField(
        max_length=255,
        db_column='location',
        null=True,
        blank=True
    )
    avatar = models.CharField(
        max_length=255,
        db_column='avatar',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'UserProfile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} Profile"
