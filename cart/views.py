from django.shortcuts import render , redirect , get_object_or_404
from store.models import Product , Variation
from .models import Cart , CartItem
from django.contrib.auth.decorators import login_required

# Create your views here.
def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart =request.session.create()
    return cart
# adding item to cart

def add_cart(request , product_id):
    current_user = request.user
    product = Product.objects.get(id = product_id)
    
    if current_user.is_authenticated:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                # print(key , value)
                try:
                    
                    variation = Variation.objects.get(product = product , variation_category__iexact = key , variation_value__iexact = value)
                    product_variation.append(variation)
                    # print(product_variation)
                    
                    
                except:
                    pass
        # 
        
        
        cart_item_exists = CartItem.objects.filter(product=product , user=current_user).exists()
        if cart_item_exists:
            cart_item = CartItem.objects.filter(product = product , user=current_user)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
           
            ulti = 0
            if len(product_variation)>0:
                for i in range(len(ex_var_list)):
                    if all(elem in ex_var_list[i] for elem in product_variation):
                        print('working')
                        product_chosen_id = id[i]
                        print('working1') 
                        ex_cart_item = CartItem.objects.get(product=product  ,id = product_chosen_id )
                        print('working2')
                        ex_cart_item.quantity += 1
                        ex_cart_item.save() 
                        ulti = 1
                        break
            
                    else:
                        print('asm')
            
            
            if ulti==1:
                pass
            else:
                cart_item = CartItem.objects.create(product = product ,quantity =1 , user = current_user)
                if len(product_variation) >0:
                    for item in product_variation:
                        print(item)
                        cart_item.variation.add(item)
                    cart_item.save()
            
            
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity =1,
                user = current_user,
            )
            if len(product_variation) >0:
                for item in product_variation:
                    cart_item.variation.add(item)
            cart_item.save()
        
        return redirect('cart')
    # User is not authenticated
    else:
        product_variation = []
        if request.method == 'POST':
            for item in request.POST:
                key = item
                value = request.POST[key]
                # print(key , value)
                try:
                    
                    variation = Variation.objects.get(product = product , variation_category__iexact = key , variation_value__iexact = value)
                    product_variation.append(variation)
                    # print(product_variation)
                    
                    
                except:
                    pass
        # 
        try:
            cart = Cart.objects.get(cart_id =_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save()
        
        cart_item_exists = CartItem.objects.filter(product=product , cart= cart).exists()
        if cart_item_exists:
            cart_item = CartItem.objects.filter(product = product , cart= cart)
            ex_var_list = []
            id = []
            for item in cart_item:
                existing_variation = item.variation.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)
            print(product_variation)
            print(ex_var_list)
            print(id)
            ulti = 0
            if len(product_variation)>0:
                for i in range(len(ex_var_list)):
                    if all(elem in ex_var_list[i] for elem in product_variation):
                        print('working')
                        product_chosen_id = id[i]
                        print('working1') 
                        ex_cart_item = CartItem.objects.get(product=product , cart = cart ,id = product_chosen_id )
                        print('working2')
                        ex_cart_item.quantity += 1
                        ex_cart_item.save() 
                        ulti = 1
                        break
            
                    else:
                        print('asm')
            
            
            if ulti==1:
                pass
            else:
                cart_item = CartItem.objects.create(product = product ,quantity =1 , cart= cart)
                if len(product_variation) >0:
                    for item in product_variation:
                        cart_item.variation.add(item)
                    cart_item.save()
            
            
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity =1,
                cart = cart,
            )
            if len(product_variation) >0:
                for item in product_variation:
                    cart_item.variation.add(item)
            cart_item.save()
        return redirect('cart')
    
#subtracting item from cart
def remove_cart(request , product_id , item_id):
    product = get_object_or_404(Product , id = product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(product = product ,  user = request.user, id = item_id)

    else:
        cart = Cart.objects.get(cart_id =_cart_id(request))  
        cart_item = CartItem.objects.get(product = product ,  cart = cart, id = item_id)
    
    try:
        
        if cart_item.quantity >1:
            cart_item.quantity -=1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

#deleting item from cart
def remove_item(request , product_id , item_id):
    product = get_object_or_404(Product , id = product_id)
    if request.user.is_authenticated:
       cart_item = CartItem.objects.get(product = product ,  user = request.user ,id = item_id)
    else:
        cart = Cart.objects.get(cart_id =_cart_id(request))
        cart_item = CartItem.objects.get(product = product ,  cart= cart ,id = item_id)
    
    
    cart_item.delete()
    return redirect('cart')


def cart(request, total =0 ,quantity =0 , cart_items=None):
    tax = (2*total)/100
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user , is_active=True)
        else:
            cart = Cart.objects.get(cart_id =_cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart , is_active = True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
            
    except :
        pass
   
    
    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
        
    }
    return render(request , "store/cart.html", context)

@login_required(login_url = "/accounts/login/45/")
def checkout(request,total =0 ,quantity =0 , cart_items=None):
    try:
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user , is_active=True)
        else:
            cart = Cart.objects.get(cart_id =_cart_id(request))
            cart_items = CartItem.objects.filter(cart = cart , is_active = True)
        
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        
    except :
        pass
   
    
    context = {
        'total' : total,
        'quantity' : quantity,
        'cart_items' : cart_items,
    }
    return render(request , "store/checkout.html" ,context)