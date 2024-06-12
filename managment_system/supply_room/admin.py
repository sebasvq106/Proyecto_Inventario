from django.contrib import admin
from .models import *


class ItemAdmin(admin.ModelAdmin):
    pass


class UserAdmin(admin.ModelAdmin):
    pass


class ClassAdmin(admin.ModelAdmin):
    pass


class GroupsAdmin(admin.ModelAdmin):
    pass


class OrderAdmin(admin.ModelAdmin):
    pass


class ItemOrderAdmin(admin.ModelAdmin):
    pass


class UserOrderAdmin(admin.ModelAdmin):
    pass


class StudentGroupsAdmin(admin.ModelAdmin):
    pass


admin.site.register(Item, ItemAdmin)
admin.site.register(Users, UserAdmin)
admin.site.register(Class, ClassAdmin)
admin.site.register(ClassGroups, GroupsAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(ItemOrder, ItemOrderAdmin)
admin.site.register(UserOrder, UserOrderAdmin)
admin.site.register(StudentGroups, StudentGroupsAdmin)
