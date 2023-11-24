from django.contrib import admin

# Register your models here.
from network.models import Post, UserProfile, Contact, User, Comment, Bookmarks, Notification


class ContactAdmin(admin.ModelAdmin):
    list_display = ('user_from', 'user_to', 'created')


admin.site.register(Post)
admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Comment)
admin.site.register(Bookmarks)
admin.site.register(Notification)