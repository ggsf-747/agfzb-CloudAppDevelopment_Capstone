from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404, render, redirect
from .models import CarModel
# from .restapis import related methods
from .restapis import get_dealers_from_cf, get_dealer_reviews_from_cf, get_dealer_from_cf_by_id, post_request
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.urls import reverse
from datetime import datetime
import logging
import json

# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.


# Create an `about` view to render a static about page
def about(request):
 return render(request, 'djangoapp/about.html')


# Create a `contact` view to return a static contact page
def contact(request):
 return render(request, 'djangoapp/contact.html')

# Create a `login_request` view to handle sign in request
def login_request(request):
    if request.method == "POST":
        username = request.POST['username1']
        password = request.POST['password1']
        user = authenticate(username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect(to=reverse('admin:index'))
            # return redirect("djangoapp:index")
        else:
            return redirect("djangoapp:index")

# Create a `logout_request` view to handle sign out request
def logout_request(request):
    logout(request)
    return redirect('djangoapp:index')

# Create a `registration_request` view to handle sign up request
def registration_request(request):
    if request.method == "GET":
        return render(request, 'djangoapp/registration.html')
    elif request.method == "POST":
        username = request.POST['username1']
        password = request.POST['password1']
        first_name = request.POST['firstname1']
        last_name = request.POST['lastname1']
        user_exist = False
        try:
            User.objects.get(username=username)
            user_exist = True
        except:
            logger.error("New user")
        if not user_exist:
            user = User.objects.create_user(username=username, first_name = first_name,
            last_name = last_name, password=password)
            login(request, user)
            return redirect("djangoapp:index")
        else:
            context['message'] = "User has already been made"
            return render(request, 'djangoapp/registration.html', context)

# Update the `get_dealerships` view to render the index page with a list of dealerships
# def get_dealerships(request):
#     context = {}
#     if request.method == "GET":
#         return render(request, 'djangoapp/index.html', context)

def get_dealerships(request):
    if request.method == "GET":
        context = {}
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/77623e3e-f0a9-4f78-8ee0-1436b05b6560/dealership-package/get-dealership"
        # Get dealers from the URL
        dealerships = get_dealers_from_cf(url)
        print("dealerships", dealerships)
        # Concat all dealer's short name
        dealer_names = ' '.join([dealer.short_name for dealer in dealerships])
        # Return a list of dealer short name
        context["dealership_list"] = dealerships
        # print("context", context, context["dealership_list"])
        print("context", context)
        # return HttpResponse(dealer_names)
        return render(request, 'djangoapp/index.html', context)


# Create a `get_dealer_details` view to render the reviews of a dealer
# def get_dealer_details(request, dealer_id):
# ...

def get_dealer_details(request, dealer_id):
    if request.method == "GET":
        context = {}
        print("step 1", dealer_id)
        dealer = get_dealer_from_cf_by_id(
            "https://us-south.functions.appdomain.cloud/api/v1/web/77623e3e-f0a9-4f78-8ee0-1436b05b6560/dealership-package/get-dealership", dealer_id)
        context["dealer"] = dealer
        print("context dealer", context["dealer"])
        # print("step 2")
        url2 = "https://us-south.functions.appdomain.cloud/api/v1/web/77623e3e-f0a9-4f78-8ee0-1436b05b6560/dealership-package/get-review"
        reviews = get_dealer_reviews_from_cf(url2, dealer_id)
        context["reviews"] = reviews
        # return HttpResponse(reviews)
        return render(request, 'djangoapp/dealer_details.html', context)

# Create a `add_review` view to submit a review
# def add_review(request, dealer_id):
# ...

def add_review(request, dealer_id):
    context = {}
    if request.method == "GET":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/77623e3e-f0a9-4f78-8ee0-1436b05b6560/dealership-package/get-dealership"
        dealer = get_dealer_from_cf_by_id(url, dealer_id)
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        print("Dealer", dealer, "Cars", cars)
        context["cars"] = cars
        context["dealer"] = dealer
        # return render(request, 'djangoapp/add_review.html', context)
        print("Done 1", context)
        # return HttpResponse(context)
        return render(request, 'djangoapp/add_review.html', context)

    if request.method == "POST":
        url = "https://us-south.functions.appdomain.cloud/api/v1/web/77623e3e-f0a9-4f78-8ee0-1436b05b6560/dealership-package/post-review"      
        if 'purchasecheck' in request.POST:
            was_purchased = True
        else:
            was_purchased = False
        cars = CarModel.objects.filter(dealer_id=dealer_id)
        for car in cars:
            if car.id == int(request.POST['car']):
                review_car = car  
        review = {}
        review["time"] = datetime.utcnow().isoformat()
        review["name"] = request.POST['name']
        review["dealership"] = dealer_id
        review["review"] = request.POST['content']
        review["purchase"] = was_purchased
        review["purchase_date"] = request.POST['purchasedate']
        review["car_make"] = review_car.make.name
        review["car_model"] = review_car.name
        review["car_year"] = review_car.year.strftime("%Y")
        json_payload = {}
        print("review4756", review)
        json_payload["review"] = review
        response = post_request(url, json_payload)
        print("Done")
        # return HttpResponse(review)
        return redirect("djangoapp:dealer_details", dealer_id=dealer_id)