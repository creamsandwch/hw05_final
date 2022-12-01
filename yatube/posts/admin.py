from django.contrib import admin

from .models import Post, Group, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'text',
        'created',
        'author',
        'group',
    )
    search_fields = ('text',)
    list_filter = ('created',)
    list_editable = ('group',)
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', )


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'post',
        'author',
        'created',
        'text'
    )
    empty_value_display = '-пусто-'
    search_fields = ('text',)


class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')


admin.site.register(Group, GroupAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
