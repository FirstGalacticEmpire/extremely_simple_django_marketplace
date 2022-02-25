from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class ListedNFTs(models.Model):
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=400)
    image = models.URLField(max_length=1000)
    price = models.IntegerField(default=0)
    bid_price = models.IntegerField(default=0)
    bid_user = models.CharField(default="", max_length=50)
    date_created = models.DateField(auto_now=True, auto_now_add=False)
    creator = models.CharField(max_length=30)
    closed = models.BooleanField(default=False)
    starting_bid_price = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.title}"


class Bids(models.Model):
    user = models.CharField(default="", max_length=50)
    item_id = models.IntegerField(default=0)
    bid = models.IntegerField(max_length=100, default=0)
