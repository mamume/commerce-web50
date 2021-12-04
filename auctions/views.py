from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import requests
from .models import *
from django.shortcuts import redirect


# Function to return the number of items in watchlist
def get_watchlist_num(request):
    if request.user.is_authenticated:
        return Watchlist.objects.filter(user=request.user).count()
    else:
        return None


def index(request):
    return render(request, "auctions/index.html", {
        # Pass only active auctions
        'auctions': Auction.objects.filter(active=True),
        'watchlist_num': get_watchlist_num(request)
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


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


# Create a new listing
@ login_required
def create_listing(request):
    if request.method == 'POST':
        # Get data from the post request
        title = request.POST['title']
        description = request.POST['desc']
        highest_bid = request.POST['highest_bid']

        # Check if the listing has image url
        if request.POST['img_url']:
            img_url = request.POST['img_url']
            image_request = requests.get(img_url)

            # Download image to media path
            if image_request.status_code == 200:
                with open(f"media/listing_imgs/{title}.jpg", 'wb') as f:
                    f.write(image_request.content)
                image = f"listing_imgs/{title}.jpg"
            else:
                image = None
        else:
            image = None

        # Check if category is provied in request
        if 'cat_id' in request.POST:
            # Get category by id
            category = Category.objects.get(pk=request.POST['cat_id'])
        else:
            category = None

        # Create auctions with provided data
        Auction.objects.create(title=title, description=description,
                               highest_bid=highest_bid, image=image, created_by=request.user, category=category)

        # Redirect to listing page of the created listing with success message
        return redirect('listing', title=title, message='Listing Created Successfully')

    # if request method is get render create_list.html
    return render(request, "auctions/create_list.html", {
        'categories': Category.objects.all(),
        'watchlist_num': get_watchlist_num(request)
    })


# View exsisting listing
def listing(request, title, message=''):
    # Get auction by title
    auction = Auction.objects.get(title=title)

    # Get highest bid for the auction
    highest_bid = Bid.objects.filter(
        listing=auction, value=auction.highest_bid).first()

    # Get the number of bid for the auction
    bids_num = Bid.objects.filter(listing=auction).count()

    # Check if the owner of the highest bid is the current user
    if highest_bid:
        is_max_bid = (highest_bid.owner == request.user)
    else:
        is_max_bid = False

    # Check if the item is in watchlist
    if request.user.is_authenticated:
        in_watchlist = bool(Watchlist.objects.filter(
            user=request.user, listing=auction))
    else:
        in_watchlist = False

    creator = auction.created_by

    # Check if the user is the creator of the item
    owner = True if request.user == creator else False

    return render(request, "auctions/listing.html", {
        'auction': auction,
        'creator': creator,
        'highest_bid': highest_bid,
        'bids_num': bids_num,
        'is_max_bid': is_max_bid,
        'in_watchlist': in_watchlist,
        'message': message,
        'owner': owner,
        'comments': Comment.objects.filter(listing=auction),
        'watchlist_num': get_watchlist_num(request)
    })


# Add new bid
def place_bid(request, title):
    # Redirect to login page if not loged in
    if not request.user.is_authenticated:
        request.method = "GET"
        return redirect('login')

    # Get auction by title and declare an empty message for later usage
    auction = Auction.objects.get(title=title)
    message = ''

    if request.method == 'POST' and request.POST['bid']:
        # Get bid from request
        bid = float(request.POST['bid'])

        # Check if the bid is higher than the highest bid
        if bid > auction.highest_bid:
            # if yes modifiy the highest bid
            auction.highest_bid = bid
            auction.save()
            # Create a new bid for current auction
            Bid.objects.create(listing=auction, value=bid, owner=request.user)
            message = 'Bid placed successfully'
        else:
            message = f'Bid must be higher than ${auction.highest_bid}'

    return redirect('listing', title=auction.title, message=message)


# To add or remove an item from the watchlist
def watchlist(request, title):
    # Redirect to login page if not loged in
    if not request.user.is_authenticated:
        request.method = "GET"
        return redirect('login')

    if request.method == 'POST':
        # Get the action: add or remove
        action = request.POST['action']
        auction = Auction.objects.get(title=title)

        # Add to watchlist
        if action == 'add-watchlist':
            watchlist = Watchlist(listing=auction)
            watchlist.save()
            watchlist.user.add(request.user)
        # Remove from watchlist
        else:
            Watchlist.objects.filter(
                listing=auction, user=request.user).delete()

    return redirect('listing', title=title)


@ login_required
def close_auction(request, auction_id):
    # Select the auction and inactivate it
    auction = Auction.objects.get(pk=auction_id)
    auction.active = False

    # Check if at least one bid
    # If yes get the winner_id which referes to the id for the user with th highest bid
    if 'winner_id' in request.POST:
        # Get user with winner_id
        winner_id = request.POST['winner_id']

        # Add the winner
        auction.winner = User.objects.get(pk=winner_id)

    auction.save()

    return redirect('listing', auction.title)


# Add Comments
def add_comment(request, auction_id, username):
    # Redirect to login page if not loged in
    if not request.user.is_authenticated:
        request.method = "GET"
        return redirect('login')

    # Get the current auction
    auction = Auction.objects.get(pk=auction_id)
    # Get the user who added the comment
    user = User.objects.get(username=username)
    # Get comment text from request
    comment = request.POST['comment']

    # Create new comment
    Comment.objects.create(text=comment, creator=user, listing=auction)

    return redirect('listing', auction.title)


# View watchlist page
@ login_required
def watchlist_page(request):
    # Get the current user and watchlist items
    user = User.objects.get(username=request.user)
    watchlist = Watchlist.objects.filter(user=user)

    # Create auctions list to add auctions in the watchlist
    auctions = []
    for auction in watchlist:
        auctions.append(auction.listing)

    return render(request, 'auctions/watchlist.html', {
        'auctions': auctions,
        'watchlist_num': get_watchlist_num(request)
    })


# View categories list
def categories_list(request):
    # Get only categorie ids of created listings
    category_ids = Auction.objects.exclude(
        category=None).values_list('category', flat=True).distinct()

    # Create new list to add used categories
    category_names = []
    for id in category_ids:
        category_names.append(Category.objects.get(pk=id))

    return render(request, "auctions/categories_list.html", {
        'categories': category_names,
        'watchlist_num': get_watchlist_num(request)
    })


# View items of a spacific category
def category_page(request, category_id):
    category = Category.objects.get(pk=category_id)

    return render(request, 'auctions/category_page.html', {
        'auctions': Auction.objects.filter(category=category, active=True),
        'category_name': category.name,
        'watchlist_num': get_watchlist_num(request)
    })
