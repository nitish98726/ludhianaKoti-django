from django.shortcuts import render , redirect
from django.http import HttpResponse
from .forms import RegistrationForm
from .models import Account
from django.contrib import messages , auth
from django.contrib.auth.decorators import login_required
from cart.views import _cart_id
from cart.models import Cart , CartItem

# Email Verification
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode ,urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage

# Create your views here.
def register(request):
    if request.method =="POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            username = email.split("@")[0]
            user = Account.objects.create_user(first_name = first_name ,last_name=last_name , email = email , username =username , password=password)
            user.phone_number = phone_number
            user.save()
            # USER ACTIVATION
            current_site = get_current_site(request)
            main_subject = "Please activate your account"
            message = render_to_string("accounts/account_verification.html" , {
                "user":user,
                'domain':current_site,
                'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            to_email = email
            send_email = EmailMessage(main_subject , message , to=[to_email])
            send_email.send()
            messages.success(request , "Thanks for Registering with us!!.We sent you an activation link on your mail")
            return redirect('register')
    else:
        form  = RegistrationForm()

    context={
        'form':form,
    }
    return render(request , "accounts/register.html" , context)

def login(request, login_param):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']

        user = auth.authenticate(email = email , password = password)
        print(user)
            
        if user is not None:
            try:
                cart = Cart.objects.get(cart_id = _cart_id(request))
                is_cart_item_exists = CartItem.objects.filter(cart=cart).exists()
                
                if is_cart_item_exists:
                    
                    cart_item = CartItem.objects.filter(cart=cart)
                    product_variation = []
                    id_nouser = []
                    for item in cart_item:
                        variation = item.variation.all()
                        product_variation.append(list(variation))
                        id_nouser.append(item.id)
                    print(product_variation)
                    
                    cart_item_user = CartItem.objects.filter(user = user)
                    ex_var_list = []
                    id_user =[]
                    for item in cart_item_user:
                        existing_variation = item.variation.all()
                        ex_var_list.append(list(existing_variation))
                        id_user.append(item.id)
                    print(ex_var_list)
                    for prod in product_variation:
                        if prod in ex_var_list:
                          
                            index = ex_var_list.index(prod)
                            
                            prod_id = id_user[index]
                            new_cart = CartItem.objects.get(id = prod_id , user= user)
                            
                            
                            new_cart.quantity +=1
                            
                            new_cart.save()
                        else:
                            
                            index_cart_item = product_variation.index(prod)
                            
                            prod_id_nouser = id_nouser[index_cart_item]
                            cart_item_nouser = CartItem.objects.get(id = prod_id_nouser , cart = cart)
                            
                            cart_item_nouser.user = user
                            
                            cart_item_nouser.save()

                    # for item in cart_item:
                    #     item.user = user
                    #     item.save()
            except:
                pass
            
            auth.login(request,user)
            messages.success(request , "You are now Logged in")
            if login_param == 651:
                return redirect('home')
            else:
                return redirect("checkout")
        else:
            messages.error(request , "Invalid Login Credentials")
            return redirect("/accounts/login/65")
    if login_param==65:
        return render(request , "accounts/login.html")
    else:
        return render(request , 'accounts/login1.html')

@login_required
def logout(request):
    auth.logout(request)
    messages.success(request , "You are Logged Out")
    return render(request , "accounts/logout.html")

def activate(request , uidb64 , token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Account._default_manager.get(pk =uid)
    except(TypeError, ValueError,OverflowError,Account.DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user,token):
        user.is_active = True
        user.save()
        messages.success(request , "congratulations , Your account is activated")

        return redirect("login")
    else:
        messages.error(request , "Invalid Link")
        return redirect("register")

@login_required(login_url='login')
def dashboard(request):
    return render(request , "accounts/dashboard.html")
