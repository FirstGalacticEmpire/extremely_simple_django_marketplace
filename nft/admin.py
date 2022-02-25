from django.contrib import admin
from .models import ListedNFTs, Bids, User

# Register your models here.
admin.site.register(ListedNFTs)
admin.site.register(Bids)
admin.site.register(User)