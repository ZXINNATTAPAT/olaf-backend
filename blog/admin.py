from django.contrib import admin
from blog.models import  Post, Comment, PostLike, CommentLike

# UserAdmin for custom User model
# class UserAdmin(admin.ModelAdmin):
#     list_display = ('username', 'first_name', 'last_name', 'phone', 'email')
#     search_fields = ('username', 'first_name', 'last_name', 'email')

# PostAdmin
class PostAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'user', 'post_text', 'post_datetime')
    search_fields = ('post_text', 'user__username')
    list_filter = ('user', 'post_datetime')

# CommentAdmin
class CommentAdmin(admin.ModelAdmin):
    list_display = ('comment_id', 'post', 'user', 'comment_datetime', 'comment_text')
    search_fields = ('comment_text', 'user__username', 'post__post_text')
    list_filter = ('post', 'user', 'comment_datetime')

# PostLikeAdmin
class PostLikeAdmin(admin.ModelAdmin):
    list_display = ('post', 'user')
    search_fields = ('post__post_text', 'user__username')

# CommentLikeAdmin
class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user')
    search_fields = ('comment__comment_text', 'user__username')

# Register models with the admin site
# admin.site.register(User, UserAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PostLike, PostLikeAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)
