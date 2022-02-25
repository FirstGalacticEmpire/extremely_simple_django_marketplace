from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from .forms import CreateForm, BidForm
from .models import ListedNFTs, User
from .tokens import account_activation_token


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))

    return HttpResponseRedirect(reverse("all_nfts"))


def success(request):
    return render(request, "success.html")


def error(request):
    return render(request, "error.html")


def login_view(request):
    if request.method == "POST":
        user = authenticate(request, username=request.POST["username"], password=request.POST["password"])
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "login.html", {
                "message": "Invalid username and/or password, or your account hasn't been activated"
            })
    else:
        return render(request, "login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("login"))


@login_required
def create_nft(request):
    if request.method == "POST":
        # get all form data
        form = CreateForm(request.POST or None)
        if form.is_valid():
            user = request.user
            # save to ListedNFTs table
            auc = ListedNFTs(title=form.cleaned_data["title"],
                             description=form.cleaned_data["description"],
                             image=form.cleaned_data["image"], price=form.cleaned_data["price"],
                             date_created=form.cleaned_data["date_created"],
                             creator=user,
                             starting_bid_price=form.cleaned_data["starting_price"])

            auc.save()
            return HttpResponseRedirect(reverse('success'))

    return render(request, "mint_nft.html", {"form": CreateForm})


@login_required
def item_details(request, auc_id):
    if request.method == "POST":
        form = BidForm(request.POST or None)
        if form.is_valid():
            bid = form.cleaned_data["bid"]
            listed_object = get_object_or_404(ListedNFTs, pk=auc_id)

            if listed_object.bid_user:
                if listed_object.bid_price > bid:
                    message = "Bid must be more than current highest bid."
                    object_ = get_object_or_404(ListedNFTs, pk=auc_id)
                    return render(request, "item_details.html", {"message": message,
                                                                          "object": object_,
                                                                          "bform": BidForm})
                else:
                    listed_object.bid_price = bid
                    listed_object.bid_user = request.user.username
                    listed_object.save()
                    message = "Bid was made succesfully."
                    return render(request, "item_details.html", {"message": message,
                                                                          "object": listed_object,
                                                                          "bform": BidForm})

            else:
                if listed_object.starting_bid_price > bid:
                    message = "Bid must be more than starting bid price"
                    object_ = get_object_or_404(ListedNFTs, pk=auc_id)
                    return render(request, "item_details.html", {"message": message,
                                                                          "object": object_,
                                                                          "bform": BidForm})
                else:
                    listed_object.bid_price = bid
                    listed_object.bid_user = request.user.username
                    listed_object.save()
                    message = "Bid was made succesfully."
                    return render(request, "item_details.html", {"message": message,
                                                                          "object": listed_object,
                                                                          "bform": BidForm})

    if request.method == "GET":
        object_ = get_object_or_404(ListedNFTs, pk=auc_id)
        return render(request, "item_details.html",
                      {"object": object_, "bform": BidForm})


@login_required
def all_nfts(request):
    my_listings = ListedNFTs.objects.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(my_listings, 3)
    try:
        my_listings_ = paginator.page(page)
    except PageNotAnInteger:
        my_listings_ = paginator.page(1)
    except EmptyPage:
        my_listings_ = paginator.page(paginator.num_pages)
    return render(request, 'nft_list.html', {"listings": my_listings_})


@login_required
def close(request, auc_id):
    if request.method == "POST":
        object_ = ListedNFTs(pk=auc_id)
        object_.closed = True
        object_.save(update_fields=['closed'])
        return redirect("item_details", auc_id)


@login_required
def delete_auction(request, auc_id):
    if request.method == "POST":
        object_ = ListedNFTs(pk=auc_id)
        object_.delete()
        return redirect("all_nfts")


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password, is_active=0)
            user.save()
            # https://stackoverflow.com/questions/65863640/email-activation-link-issue-in-django-3-1-3
            current_site = get_current_site(request)
            mail_subject = 'Activate your blog account.'
            message = render_to_string('activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': account_activation_token.make_token(user=user),
            })
            to_email = email
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send()
            return HttpResponse('Please confirm your email address to complete the registration')

        except IntegrityError:
            return render(request, "register.html", {
                "message": "Username already taken."
            })

        # login(request, user)
        # return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "register.html")


# https://stackoverflow.com/questions/65863640/email-activation-link-issue-in-django-3-1-3
def activate_account(request, uidb64, token):
    try:
        uid = force_bytes(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return HttpResponse('Your account has been activated successfully')
    else:
        return HttpResponse('Activation link is invalid!')
