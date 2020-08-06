from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# Import models
from .models import User, Listing, Bid, Comment

# Import form
from .form import ListingForm, BidForm, CommentForm

# Import to use max query 
from django.db.models import Max, Avg

def get_highest_bid(listing):
    highest_bid = Bid.objects.filter(listing = listing)

"""Home Page"""
def index(request):
    user_listings = None
    listings = Listing.objects.filter(state="Active")
    if request.user.is_authenticated:
        user_listings = request.user.user_listings.filter(state="Active")
        listings = Listing.objects.filter(state="Active").exclude(create_user = request.user)

    # Active listing 
    return render(request, "auctions/index.html", {
        "user_listings":user_listings,
        "listings":listings
    })
    
#==========================================================================================================

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        print(username, password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        if not request.user.is_authenticated:
            return render(request, "auctions/login.html")
        return HttpResponseRedirect(reverse("index"))


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")

#==========================================================================================================

def create_new_listing(request):
    # Phải đăng nhập mới tạo listing mới đc 
    if not request.user.is_authenticated:
        messages.info(request, "Login Required")
        return HttpResponseRedirect(reverse('login'))

    if request.method == "POST":
        # Tạo html form bằng Django
        form = ListingForm(request.POST)

        if form.is_valid():
            listing = Listing()
            # Có thể dùng request.POST.get(...) cx đc 
            listing.title        = form.cleaned_data["title"]
            listing.category     = form.cleaned_data["category"] 
            listing.description  = form.cleaned_data["description"]
            listing.starting_bid = form.cleaned_data["starting_bid"]
            listing.image        = form.cleaned_data["image"]
            listing.create_user = request.user

            # No image url provided
            if listing.image == "https://bom.to/79jrla": 
                listing.description += "(no image provided)"

            # Add vào db
            listing.save()
            return HttpResponseRedirect(reverse('index'))

    return render(request, "auctions/new.html", {
        "form":ListingForm()
    })

#==========================================================================================================

def specific_category_list(request, type):
    type_list = Listing.objects.filter(category = type.capitalize(), state = "Active").all()
    return render(request, "auctions/category.html",{
        "listings":type_list
    })


#==========================================================================================================


def listing_detail(request, listing_id):
    listing = Listing.objects.get(id = listing_id)
    highest_bid = Bid.objects.filter(listing = listing).aggregate(Max('money'))["money__max"]
    winning_user = None

    comments = Comment.objects.filter(listing = listing).all()
    if not comments:
        average_rating = 5
    else: 
        average_rating = round(float(Comment.objects.filter(listing = listing).aggregate(Avg('comment_rating'))["comment_rating__avg"]), 2)
    
    # No one has bidded
    if highest_bid == None: 
        highest_bid = 0 
    else :
        winning_user = (Bid.objects.get(listing = listing, money = highest_bid)).user

    if not request.user.is_authenticated:
        in_watchlist = True
    else:
        in_watchlist = listing in request.user.watchlist.all()

    return render(request, "auctions/detail.html",{
        "listing":listing,
        "highest_bid":highest_bid,
        "winning_user":winning_user,
        "bid_form":BidForm(),
        "comment_form":CommentForm(), 
        "comments":comments,
        "average_rating":average_rating,
        "in_watchlist": in_watchlist
    })


def listing_bid(request, listing_id):
    if request.method == "POST":
        # Phải đăng nhập mới bid dc 
        if not request.user.is_authenticated:
            messages.info(request, "Login Required")
            return HttpResponseRedirect(reverse('login'))

        

        # Get data
        listing = Listing.objects.get(id = listing_id)
        highest_bid = Bid.objects.filter(listing = listing).aggregate(Max('money'))["money__max"] 
        if highest_bid == None: 
            highest_bid = 0
        bid_price = float(request.POST["money"])

        # Ko tự bid hàng của mình đc 
        if listing.create_user == request.user:
            messages.error(request, "You can't bid your own listing")

        # Xử lí khi giá bid thấp hơn highest bid or starting price
        elif bid_price < listing.starting_bid:
            messages.error(request, "Bid must not lower than starting price")
        elif highest_bid != None and bid_price <= highest_bid:
            messages.error(request, "Bid must be higher than current highest bid")
        else:
            new_bid = Bid(listing = listing, user = request.user, money = bid_price)
            new_bid.save()
            messages.success(request, "Successfully bid")

            # Ai bid thì tự thêm vào watchlist
            listing.watchlist.add(request.user)

        return HttpResponseRedirect(reverse('detail', args = (listing_id,)))
    

def listing_comment(request, listing_id):
    # Handle user's comment
    if request.method == "POST":
        # Login required
        if not request.user.is_authenticated:
            messages.info(request, "Login Required")
            return HttpResponseRedirect(reverse('login'))
    
        # Form content
        listing = Listing.objects.get(pk = listing_id)
        comment_content = request.POST["comment_content"]
        comment_rating = int(request.POST["comment_rating"])

        # Each user can cmt only once
        new_comment = Comment(listing = listing, user = request.user, comment_content = comment_content, comment_rating = comment_rating)
        if not Comment.objects.filter(user = request.user, listing = listing):
            new_comment.save()
        else: 
            print(Comment.objects.filter(user = request.user, listing = listing).all())
            messages.warning(request, "You have added another comment")

    return HttpResponseRedirect(reverse('detail', args = (listing_id,)))

def modify_watchlist(request, listing_id):
    if not request.user.is_authenticated:
        messages.info(request, "Login Required")
        return HttpResponseRedirect(reverse('login'))

    listing = Listing.objects.get(pk = listing_id)
    watchlist = request.user.watchlist.all()

    if listing not in watchlist: 
        listing.watchlist.add(request.user)
        messages.success(request, "Added to watchlist")
    else:
        listing.watchlist.remove(request.user)
        messages.error(request, "Removed from watchlist")

    return HttpResponseRedirect(reverse('detail', args=(listing_id,)))

def listing_close(request, listing_id):
    listing = Listing.objects.filter(pk = listing_id).update(state = "Close")
    return HttpResponseRedirect(reverse('detail', args=(listing_id, )))

#==========================================================================================================

def watchlist_page(request):
    if not request.user.is_authenticated:
        messages.info(request, "Login Required")
        return HttpResponseRedirect(reverse('login')) 

    return render(request, "auctions/watchlist.html", {
        "listings": request.user.watchlist.all()
    })
