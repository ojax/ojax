from django.contrib import admin
from activity.models import Activity, ActivityComment


admin.site.register(Activity)
admin.site.register(ActivityComment)