from django.shortcuts import render, redirect
from .models import Product, Category, Profile, Testimonial, VisitorCount
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.forms import UserCreationForm
from .forms import SignUpForm, UpdateUserForm, ChangePasswordForm, UserInfoForm
from django import forms
from payment.forms import ShippingForm
from payment.models import ShippingAddress
from django.db.models import Q
import json
from cart.cart import Cart


# Create your views here.

def blog(request):
    return render(request, 'blog.html')
def testimonials(request):
    total_customers = Testimonial.objects.count()
    happy_customers = Testimonial.objects.filter(rating__gte=4).count()
    reviews = Testimonial.objects.all()[:5]

    context = {
        'total_customers': total_customers,
        'happy_customers': happy_customers,
        'reviews': reviews,
    }
    return render(request, 'index.html', context)


def search(request):
    query = request.GET.get('searched', '')  # Get the search query from the GET request
    sort_by = request.GET.get('sort', 'name')  # Default sorting by 'name'
    if query:
        # Query the Product model to find matches
        searched = Product.objects.filter(Q(name__icontains=query) | Q(description__icontains=query))

        # Order the results based on the 'sort' parameter
        searched = searched.order_by(sort_by)

        # Pagination logic
        paginator = Paginator(searched, 8)  # Show 12 products per page
        page_number = request.GET.get('page')  # Get the page number from query parameters
        page_obj = paginator.get_page(page_number)

        # Check if any products were found
        if page_obj:
            return render(request, 'search.html', {'searched': page_obj, 'query': query})
        else:
            messages.error(request, "That product does not exist. Please try again.")
            return render(request, 'search.html', {'query': query})
    else:
        return render(request, 'search.html', {})


def update_info(request):
    if request.user.is_authenticated:
        # Get current user's profile
        try:
            current_user = Profile.objects.get(user_id=request.user.id)
        except Profile.DoesNotExist:
            messages.error(request, "Profile does not exist.")
            return redirect('index')

        # Get current user's shipping info, or handle if it doesn't exist
        try:
            shipping_user = ShippingAddress.objects.get(user_id=request.user.id)
        except ShippingAddress.DoesNotExist:
            shipping_user = None

        # Instantiate forms
        form = UserInfoForm(request.POST or None, instance=current_user)
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)

        if form.is_valid() and shipping_form.is_valid():
            form.save()
            shipping_form.save()
            messages.success(request, 'Your info has been updated!')
            return redirect('index')

        return render(request, "update_info.html", {
            'form': form,
            'shipping_form': shipping_form
        })

    else:
        messages.error(request, "Please login to update your account.")
        return redirect('index')


def update_password(request):
    if request.user.is_authenticated:
        current_user = request.user
        # did the form is filled?
        if request.method == 'POST':
            #proceed with it
            form = ChangePasswordForm(current_user, request.POST)
            # is the form valid
            if form.is_valid():
                form.save()
                messages.success(request, 'Your password has been updated!')
                #login(request, current_user)
                return redirect('update_user')
            else:
                for error in list(form.errors.values()):
                    messages.error(request, error)
                    return redirect('update_password')

        else:
            form = ChangePasswordForm(current_user)
            return render(request, 'update_password.html', {'form': form})
    else:
        messages.success(request, 'Please login to Proceed')
        return redirect('index')


def update_user(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    if request.user.is_authenticated:
        current_user = User.objects.get(id=request.user.id)
        if request.method == 'POST':
            user_form = UpdateUserForm(request.POST, request.FILES, instance=current_user)
            if user_form.is_valid():
                user_form.save()

                # Save profile picture if available
                if 'profile_picture' in request.FILES:
                    profile.profile_picture = request.FILES['profile_picture']
                    profile.save()
                messages.success(request, 'Your account has been updated!')
                return redirect('index')
        else:
            user_form = UpdateUserForm(instance=current_user)
        return render(request, "update_user.html", {'user_form': user_form})
    else:
        messages.success(request, "Please Login to Update Your Account ")
        return redirect('index')


def category(request, foo):
    foo = foo.replace('-', '')
    try:
        category = Category.objects.get(name=foo)

        # Get the sorting option from the GET request, default to 'name'
        sort_by = request.GET.get('sort', 'name')  # Can be 'price', 'name', 'created_at', etc.
        products = Product.objects.filter(category=category).order_by(sort_by)

        # Add pagination here
        paginator = Paginator(products, 8)  # Adjust the number of products per page as needed
        page_number = request.GET.get('page')

        try:
            products = paginator.page(page_number)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)
        return render(request, 'category.html', {'products': products, 'category': category})

    except:
        messages.error(request, 'That Category does not exist')
        return redirect('index')


def index(request):
    products = Product.objects.all()
    # visitor count increment by 1
    visitor_count, created = VisitorCount.objects.get_or_create(id=1)
    # visitor_count.count = 0
    # visitor_count.save()
    visitor_count.increment() # Increment the visit count
    testimonials = Testimonial.objects.all()
    total_customers_deafult = 2000
    total_customers = testimonials.count() + visitor_count.count + total_customers_deafult
    # Set default count for happy customers if no testimonials are present
    happy_customers_default = 1500  # Example default value
    happy_customers = testimonials.filter(rating__gte=4).count() + visitor_count.count + happy_customers_default
    # Format counts with commas
    formatted_total_customers = "{:,}".format(total_customers)
    formatted_happy_customers = "{:,}".format(happy_customers)

    # happy_customers = testimonials.filter(rating__gte=4).count() + visitor_count.count
    reviews = Testimonial.objects.all()[:5]
    return render(request, 'index.html',
                  {'products': products,
                   'testimonials': testimonials,
                   'total_customers': formatted_total_customers,
                   'happy_customers': formatted_happy_customers,
                   'reviews': reviews,
                   })


def all_products(request):
    products = Product.objects.order_by('name').filter(is_published=True)
    paginator = Paginator(products, 8)
    page_number = request.GET.get('page')
    try:
        products = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        products = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g., 9999), deliver last page of results.
        products = paginator.page(paginator.num_pages)
    return render(request, 'category.html', {'products': products})


def product(request, pk):
    products = Product.objects.filter(id=pk)
    return render(request, 'product.html', {'products': products})


def special_products(request):
    products = Product.objects.all()
    return render(request, 'special-products.html', {'products': products})


from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import Profile
from django.shortcuts import redirect, render
import json
from cart.cart import Cart  # Assuming you are using this for cart handling.


def login_user(request):
    if request.method == 'POST':
        # Retrieve the login credentials
        username_or_email_or_phone = request.POST.get('username_or_email_or_phone')  # Input for username/email/phone
        password = request.POST['password']

        user = None
        if '@' in username_or_email_or_phone:  # Check if it's an email
            user = User.objects.filter(email=username_or_email_or_phone).first()
        elif username_or_email_or_phone.isdigit():  # Check if it's a phone number (digits only)
            user = User.objects.filter(profile__phone=username_or_email_or_phone).first()
        else:  # Default to username if neither email nor phone number is provided
            user = User.objects.filter(username=username_or_email_or_phone).first()

        if user:
            # Authenticate the user
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                login(request, user)

                # Load any saved cart data
                current_user = Profile.objects.get(user_id=request.user.id)
                saved_cart = current_user.old_cart

                if saved_cart:
                    converted_cart = json.loads(saved_cart)
                    cart = Cart(request)
                    for key, value in converted_cart.items():
                        cart.db_add(product=key, quantity=value)

                messages.success(request, 'Login successful! Please update your Profile...')
                return redirect('update_user')
            else:
                messages.error(request, 'Invalid login credentials. Please try again.')
                return redirect('login')
        else:
            messages.error(request, 'No account found with that email/phone number.')
            return redirect('login')
    else:
        return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, ("You have successfully logged out...!!"))
    return redirect('index')


def register_user(request):
    form = SignUpForm()
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()


            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            #log in user
            # user = authenticate(request, username=username, password=password)
            login(request, user)
            messages.success(request, 'Username Created - Please Fill the Details...')
            return redirect('update_info')
        else:
            for error in list(form.errors.values()):
                messages.error(request, error)
                return redirect('register')
    else:
        return render(request, 'register.html', {'form': form})

#           if user is not None:
#               login(request, user)  # Log the user in
#               messages.success(request, 'You are now logged in!')
#               return redirect('index')  # Redirect to the homepage
#           else:
#                for error in list(form.errors.values()):
#                   messages.error(request, error)
#                   return redirect('login')  # Redirect to the login page
#       else:
#           messages.error(request, 'There was an error with your registration.')
#           return render(request, 'register.html', {'form': form})
#  else:
#       form = SignUpForm()

#   return render(request, 'register.html', {'form': form})
