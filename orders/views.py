from django.shortcuts import render,redirect
from django.http import HttpResponse
from cart.models import CartItem
from .forms import OrderForm
from .models import Order , Payment , OrderProduct
from datetime import datetime
from store.models import Product
import json
from django.core.mail import EmailMessage
from django.contrib import messages

from django.template.loader import render_to_string
from django.http import JsonResponse

# Create your views here.
def place_order(request):
    current_user = request.user
    cart_items = CartItem.objects.filter(user = current_user)
    cart_count = cart_items.count()
    if cart_count<=0:
        return redirect("cart")
    total=0
    tax=0
    for cart_item in cart_items:
        total += (cart_item.product.price*cart_item.quantity)
        tax = .05*total
    grand_total = total+tax
    if request.method=="POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            data = Order()
            data.user = current_user
            data.first_name = form.cleaned_data['first_name']
            data.last_name = form.cleaned_data['last_name']
            data.phone = form.cleaned_data['phone']
            data.email = form.cleaned_data['email']
            data.address_line1 = form.cleaned_data['address_line1']
            data.address_line2 = form.cleaned_data['address_line2']
            data.city = form.cleaned_data['city']
            data.state = form.cleaned_data['state']
            data.zip = form.cleaned_data['zip']
            data.order_total = grand_total
            data.tax = tax
            data.ip = request.META.get("REMOTE_ADDR")
            data.save()
            #Generating order_id
            now = datetime.now()
            current_date = (now.strftime(r"%Y%m%d"))
            order_number = current_date + str(data.id)
            data.order_number = order_number
            data.save()
            order = Order.objects.get(user = current_user , is_ordered = False , order_number =order_number  )
            context ={
                "order":order,
                'cart_items':cart_items,
                'total':total,
                'tax':tax,
                "grand_total":grand_total,
            }
            return render(request , 'orders/payments.html' , context)
    else:
        return redirect('checkout')

def payments(request):
    body = json.loads(request.body)
    # print(body)
    # Storing Transaction detail inside payment model
    
    order = Order.objects.get(user = request.user , is_ordered = False , order_number = body['orderID'])
    payment = Payment(
        user = request.user,
        payment_id = body["transID"],
        payment_method = body['payment_method'],
        amount_paid = order.order_total,
        status = body['status'],
    )
    payment.save()
    order.payment = payment
    order.is_ordered = True
    order.save()

    #code here is a bit ambigious
    #Move the cart item to order Product Table
    cart_items = CartItem.objects.filter(user = request.user)
    # order1 = Order.objects.get(user = request.user , order_number = body['orderID'])
    for item in cart_items:
        orderproduct = OrderProduct() # instance declaration
        orderproduct.order_id = order.id 
        # print(order.id)
        orderproduct.payment = payment
        orderproduct.user = request.user 
        orderproduct.product_id = item.product_id #now here we have item from CartItem model but not the product model so instead we served the id of the product mode
        # print(item.product_id)
        orderproduct.quantity = item.quantity
        orderproduct.productPrice = item.product.price
        orderproduct.ordered = True
        orderproduct.save()

        new_item = CartItem.objects.get(id = item.id)
        product_variation = new_item.variation.all()
        orderproduct = OrderProduct.objects.get(id = orderproduct.id)
        orderproduct.variation.set(product_variation)
        orderproduct.save()
        
        # decreasing stock
        product = Product.objects.get(id = item.product_id)
        product.stock -= item.quantity
        product.save()

    #clear cart of previous ordered items
    CartItem.objects.filter(user = request.user).delete()
    # send order received mail
    main_subject = "Thank you for your order"
    message = render_to_string("orders/orders_received.html" , {
            "user":request.user,
            "order":order,
            
            })
    to_email = request.user.email
    send_email = EmailMessage(main_subject , message , to=[to_email])
    send_email.send()
    messages.success(request , "Thanks for Ordering")
    
    #Send Order number and transaction id back to sendData method via JsonResponse
    data = {
        'order_number' : order.order_number,
        'transID':payment.payment_id,
    }
    return JsonResponse(data)
    return render(request , 'orders/payments.html')

def order_complete(request ):
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')

    try:
        order = Order.objects.get(order_number = order_number , is_ordered = True)
        ordered_products = OrderProduct.objects.filter(order_id = order.id)
        total = order.order_total - order.tax
        context = {
            'order':order,
            'ordered_products':ordered_products,
            'order_number':order.order_number,
            'total':total
        }
        return render(request , "orders/order_complete.html" , context)
    except:
        return redirect('home')
    