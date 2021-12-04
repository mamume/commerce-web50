from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
from django.db.models.deletion import CASCADE


class User(AbstractUser):
    pass


class Category(models.Model):
    name = models.CharField(max_length=32, null=True, default='', unique=True)


class Auction(models.Model):
    title = models.CharField(max_length=32)
    description = models.CharField(max_length=500)
    highest_bid = models.FloatField(validators=[MinValueValidator(0)])
    image = models.ImageField(upload_to='listing_imgs', null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='creator', default=None)
    active = models.BooleanField(default=True, null=True)
    winner = models.ForeignKey(
        User, on_delete=CASCADE, default=None, related_name='winner', null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=CASCADE, null=True, default=None)


class Bid(models.Model):
    listing = models.ForeignKey(Auction, on_delete=CASCADE, null=True)
    value = models.FloatField(null=True)
    owner = models.ForeignKey(User, on_delete=CASCADE, null=True)


class Comment(models.Model):
    text = models.CharField(max_length=100, null=True)
    creator = models.ForeignKey(User, on_delete=CASCADE, null=True)
    listing = models.ForeignKey(Auction, on_delete=CASCADE, null=True)


class Watchlist(models.Model):
    listing = models.OneToOneField(Auction, on_delete=CASCADE,
                                   primary_key=True)
    user = models.ManyToManyField(User)
