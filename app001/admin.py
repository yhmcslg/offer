from django.contrib import admin
import models


# Register your models here.


admin.site.register(models.AdminInfo)
admin.site.register(models.ExecuteType)
admin.site.register(models.Host)
admin.site.register(models.HostGroup)
admin.site.register(models.HostStatus)
admin.site.register(models.Task)
admin.site.register(models.TaskHostStatus)
admin.site.register(models.TaskLog)
admin.site.register(models.TaskTemplate)
admin.site.register(models.TaskType)
admin.site.register(models.UserGroup)
admin.site.register(models.UserProfile)
admin.site.register(models.UserType)