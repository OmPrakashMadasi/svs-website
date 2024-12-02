from django.shortcuts import render, redirect
from cart.cart import Cart
from payment.forms import ShippingForm, PaymentForm
from .models import ShippingAddress, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib import messages
from webapp.models import Product

# Create your views here.

def process_order(request):
    if request.POST:
        # Get cart Info
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()
        # Get Billing Info from the last page   
        payment_form = PaymentForm(request.POST or None)
        # Get shipping session data
        my_shipping = request.session.get('my_shipping')
        print(my_shipping)

        # Gather Order Info
        full_name = my_shipping['shipping_full_name']
        email = my_shipping['shipping_email']
        # Create Shipping Address from session info
        shipping_address = f"{my_shipping['shipping_address1']}\n{my_shipping['shipping_address2']}\n{my_shipping['shipping_city']}\n{my_shipping['shipping_zipcode']}\n{my_shipping['shipping_country']}"
        amount_paid = totals

        if request.user.is_authenticated:
            #logged in
            user = request.user
            # Create Order
            create_order = Order(user=user, full_name= full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # add the order items
            # get the order ID
            order_id = create_order.pk

            # get product Info
            for product in cart_products():
                # get product id
                product_id = product.id
                # get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                # Get quantity
                for key, value in quantities().items():
                    if int(key) == product.id:
                        # create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, user=user, quantity=value, price=price)
                        create_order_item.save()

            # Delete our cart
            for key in list(request.session.keys()):
                if key == "session_key":
                    # Delete the key
                    del request.session[key]


            messages.success(request, "Order Placed!")
            return redirect('index')
        else:
            # not logged in
            # create order
            create_order = Order(full_name= full_name, email=email, shipping_address=shipping_address, amount_paid=amount_paid)
            create_order.save()

            # add the order items
            # get the order ID
            order_id = create_order.pk

            # get product Info
            for product in cart_products():
                # get product id
                product_id = product.id
                # get product price
                if product.is_sale:
                    price = product.sale_price
                else:
                    price = product.price

                # Get quantity
                for key, value in quantities().items():
                    if int(key) == product.id:
                        # create order item
                        create_order_item = OrderItem(order_id=order_id, product_id=product_id, quantity=value, price=price)
                        create_order_item.save()

            messages.success(request, "Order Placed!")
            return redirect('index')

    else:
        messages.success(request, 'Access Denied')
        return redirect('index')






def billing_info(request):
    if request.POST:
        cart = Cart(request)
        cart_products = cart.get_prods
        quantities = cart.get_quants
        totals = cart.cart_total()

        # Create a session with Shipping Info
        my_shipping = request.POST
        request.session['my_shipping'] = my_shipping


        # check to see if user is logged in
        if request.user.is_authenticated:
            # Get the billing form
            billing_form = PaymentForm()
            return render(request, 'billing_info.html', {"cart_products": cart_products,
                                                         "quantities": quantities, "totals": totals,
                                                         "shipping_info": request.POST, "billing_form": billing_form, })
        else:
            # not logged in
            # get the billing Form
            billing_form = PaymentForm()
            return render(request, 'billing_info.html', {"cart_products": cart_products,
                                                         "quantities": quantities, "totals": totals,
                                                         "shipping_info": request.POST, "billing_form": billing_form, })
            shipping_form = request.POST
            return render(request, 'billing_info.html', {"cart_products": cart_products,
                                                         "quantities": quantities, "totals": totals,
                                                         "shipping_form": shipping_form})
    else:
        messages.success(request, "Access Denied")
        return redirect('index')


def checkout(request):
    cart = Cart(request)
    cart_products = cart.get_prods
    quantities = cart.get_quants
    totals = cart.cart_total()

    if request.user.is_authenticated:
        #checkout as logged in user
        #shipping User
        shipping_user = ShippingAddress.objects.get(user_id=request.user.id)
        #shipping form
        shipping_form = ShippingForm(request.POST or None, instance=shipping_user)
        return render(request, 'checkout.html',
                      {"cart_products": cart_products,
                       "quantities": quantities, "totals": totals, "shipping_form": shipping_form, })
    else:
        #checkout as guest
        shipping_form = ShippingForm(request.POST or None)
        return render(request, 'checkout.html', {"cart_products": cart_products,
                                                 "quantities": quantities, "totals": totals,
                                                 "shipping_form": shipping_form, })


def payment_success(request):
    return render(request, 'payment_success.html')
