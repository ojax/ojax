from django.contrib import admin
from activity.models import Activity, ActivityComment

class ActivityAdmin(admin.ModelAdmin):
    date_hierarchy = 'created'
    list_filter = ('source', 'user')

admin.site.register(Activity, ActivityAdmin)
admin.site.register(ActivityComment)