from django.contrib import admin
from .models import Listing, User, Bid, Comment
from django.contrib.auth.admin import UserAdmin

class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "description", "starting_bid", "state", "create_user")

class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "listing")

class CommentAdmin(admin.ModelAdmin):
    list_display = ("user", "listing", "comment_content", "comment_rating")

admin.site.register(Listing, ListingAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(Comment, CommentAdmin)