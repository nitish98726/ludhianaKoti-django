from django.shortcuts import render,redirect
from django.http import HttpResponse
from cart.models import CartItem
from .forms import OrderForm
from .models import Order
from datetime import datetime

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
            return redirect('checkout')
    else:
        return redirect('checkout ')

def payments(request):
    return render(request , 'orders/payments.html')