from django.contrib.auth.models import AbstractUser
from django.db import models

# Inherits from AbstractUser,, already have fields for a username, email, password,...
class User(AbstractUser):
    pass


# models to represent details about auction listings, bids, comments, and auction categories
# thay đổi xg nhớ makemigrations + migrate

class Listing(models.Model):
    title = models.CharField(max_length = 64)
    category = models.CharField(max_length = 32)
    description = models.CharField(max_length = 256)
    starting_bid = models.FloatField()
    image = models.CharField(max_length = 2048, null = True)

    state = models.CharField(max_length= 12, default = "Active")
    create_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_listings")

    watchlist = models.ManyToManyField(User, blank = True, related_name="watchlist")

    def __str__(self):
        return f"{self.id}: {self.title} - {self.starting_bid}"
        

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="biddings")
    user    = models.ForeignKey(User, on_delete=models.CASCADE, related_name="biddings")
    money   = models.FloatField()

    def __str__(self):
        return f"{self.user.username}: {self.listing.title} - {self.money}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="comments")
    comment_content = models.CharField(max_length = 512)
    comment_rating = models.IntegerField()

