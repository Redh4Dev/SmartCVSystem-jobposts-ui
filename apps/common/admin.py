from django.contrib import admin

# Register your models here.
from apps.authx.models    import User, Role, Permission, RolePermission


admin.site.register(User)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(RolePermission)