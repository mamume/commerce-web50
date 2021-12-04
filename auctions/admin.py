from django.contrib import admin
from auctions.models import *


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "password", "is_superuser")


class AuctionAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "description", "highest_bid",
                    "created_by", "timestamp", "active", "winner", "category")


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")


class BidAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "owner")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "creator", "listing", "text")


# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Auction, AuctionAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Watchlist)
