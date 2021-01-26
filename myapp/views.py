from django.shortcuts import render,redirect
from .models import Contact,User,Product,WishList,Cart,Transaction
from django.core.mail import send_mail
import random
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .paytm import generate_checksum, verify_checksum
from django.http import JsonResponse
# Create your views here.
def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(email__iexact=username).exists()
    }
    return JsonResponse(data)
def index(request):
	return render(request,'index.html')

def seller_index(request):
	return render(request,'seller_index.html')

def contact(request):
	if request.method=="POST":
		Contact.objects.create(
				name=request.POST['name'],
				email=request.POST['email'],
				mobile=request.POST['mobile'],
				remarks=request.POST['remarks'],
			)
		contacts=Contact.objects.all().order_by('-id')
		msg="Contact Submit Succeessfully"
		return render(request,'contact.html',{'msg':msg,'contacts':contacts})
	else:
		contacts=Contact.objects.all().order_by('-id')
		return render(request,'contact.html',{'contacts':contacts})

def signup(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			if user:
				msg="Email Already Registered"
				return render(request,'signup.html',{'msg':msg})
		except:
			if request.POST['password']==request.POST['cpassword']:
				User.objects.create(
						fname=request.POST['fname'],
						lname=request.POST['lname'],
						email=request.POST['email'],
						mobile=request.POST['mobile'],
						password=request.POST['password'],
						cpassword=request.POST['cpassword'],
						usertype=request.POST['usertype'],
					)
				rec=[request.POST['email'],]
				subject=" OTP for Registration"
				otp=random.randint(1000,9999)
				massage="Your OTP for Registration Is "+str(otp)
				email_from = settings.EMAIL_HOST_USER
				send_mail(subject,massage,email_from,rec)
				return render(request,'otp.html',{'otp':otp,'email':request.POST['email']})
			else:
				msg="Password & Confrim Password Does Not Matched"
				return render(request,'signup.html',{'msg':msg})
	else:
		return render(request,'signup.html')

def login(request):
	if request.method=="POST":
		try:
			user=User.objects.get(
					email=request.POST['email'],
					password=request.POST['password'],
				)
			if user.usertype=="user":
				request.session['fname']=user.fname
				request.session['lname']=user.lname
				request.session['email']=user.email
				wishlists=WishList.objects.filter(user=user)
				request.session['wishlist_count']=len(wishlists)
				carts=Cart.objects.filter(user=user,status="pending")
				request.session['cart_count']=len(carts)
				return render(request,'index.html')

			elif user.usertype=="seller":
				request.session['fname']=user.fname
				request.session['lname']=user.lname
				request.session['email']=user.email

				return render(request,'seller_index.html')


		except:
			msg="Email Or Password Is Incorrect"
			return render(request,'login.html',{'msg':msg})
	else:
		return render(request,'login.html')

def validate_otp(request):
	myvar=""
	otp=request.POST['otp']
	uotp=request.POST['uotp']
	email=request.POST['email']
	try:
		myvar=request.POST['myvar']
	except:
		pass

	user=User.objects.get(email=email)

	if otp==uotp and myvar=="forgot_password":
		return render(request,'new_password.html',{'email':email})
	elif otp==uotp:
		user.status="active"
		user.save()
		msg="User Validated Succeessfully"
		return render(request,'login.html',{'msg':msg})
	else:
		msg="Invalid OTP"
		return render(request,'otp.html',{'msg':msg,'otp':otp,'email':email})

def logout(request):
	try:
		del request.session['fname']
		del request.session['lname']
		del request.session['email']
		del request.session['wishlist_count']
		del request.session['cart_count']
		return render(request,'login.html')
	except:
		return render(request,'login.html')

def change_password(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		if user.password==request.POST['old_password']:
			if request.POST['new_password']==request.POST['cnew_password']:
				user.password=request.POST['new_password']
				user.cpassword=request.POST['new_password']
				user.save()
				return redirect('logout')
			else:
				msg="New Password & Confrim New Password Does Not Matched"
				return render(request,'change_password.html',{'msg':msg})
		else:
			msg="Old Password Is Incorrect"
			return render(request,'change_password.html',{'msg':msg})		
	else:
		return render(request,'change_password.html')

def forgot_password(request):
	if request.method=="POST":
		try:
			user=User.objects.get(email=request.POST['email'])
			if user:
				rec=[request.POST['email'],]
				subject=" OTP for Forgot Password"
				otp=random.randint(1000,9999)
				massage="Your OTP for Forgot Password Is "+str(otp)
				email_from = settings.EMAIL_HOST_USER
				send_mail(subject,massage,email_from,rec)
				myvar="forgot_password"
				return render(request,'otp.html',{'otp':otp,'email':request.POST['email'],'myvar':myvar})
		except:
			msg="Email Does Not Exists"
			return render(request,'forgot_password.html',{'msg':msg})
	else:
		return render(request,'forgot_password.html')

def new_password(request):
	user=User.objects.get(email=request.POST['email'])
	if request.POST['new_password']==request.POST['cnew_password']:
		user.password=request.POST['new_password']
		user.cpassword=request.POST['cnew_password']
		user.save()
		return redirect('login')
	else:
		msg="New Password & Confrim New Password Does Not Matched"
		return render(request,'new_password.html',{'email':email,'msg':msg})

def seller_add_product(request):
	if request.method=="POST":
		user=User.objects.get(email=request.session['email'])
		Product.objects.create(
				product_seller=user,
				product_category=request.POST['product_category'],
				product_name=request.POST['product_name'],
				product_price=request.POST['product_price'],
				product_image=request.FILES['product_image'],
				product_desc=request.POST['product_desc'],
			)
		msg="Product Added Succeessfully"
		return render(request,'seller_add_product.html',{'msg':msg})

	else:
		return render(request,'seller_add_product.html')

def seller_view_product(request):
	user=User.objects.get(email=request.session['email'])
	products=Product.objects.filter(product_seller=user)
	return render(request,'seller_view_product.html',{'products':products})

def seller_product_detail(request,pk):
	product=Product.objects.get(pk=pk)
	return render(request,'seller_product_detail.html',{'product':product})

def seller_product_edit(request,pk):
	product=Product.objects.get(pk=pk)
	if request.method=="POST":
		product.product_name=request.POST['product_name']
		product.product_price=request.POST['product_price']
		product.product_desc=request.POST['product_desc']
		try:
			product.product_image=request.FILES['product_image']
		except:
			pass
		product.save()
		return redirect('seller_view_product')
	else:
		return render(request,'seller_product_edit.html',{'product':product})

def seller_product_delete(request,pk):
	product=Product.objects.get(pk=pk)
	product.delete()
	return redirect('seller_view_product')

def user_view_product(request,cn):
	products=Product.objects.filter(product_category=cn)
	return render(request,'user_view_product.html',{'products':products})

def user_product_detail(request,pk):
	flag=False
	flag1=False
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	try:
		wishlist=WishList.objects.get(user=user,product=product)
		flag=True
	except:
		pass

	try:
		cart=Cart.objects.get(user=user,product=product,status="pending")
		flag1=True
	except:
		pass
	return render(request,'user_product_detail.html',{'product':product,'flag':flag,'flag1':flag1})

def mywishlist(request):
	user=User.objects.get(email=request.session['email'])
	wishlists=WishList.objects.filter(user=user)
	request.session['wishlist_count']=len(wishlists)
	return render(request,'mywishlist.html',{'wishlists':wishlists})

def add_to_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	WishList.objects.create(user=user,product=product)
	return redirect('mywishlist')

def remove_from_wishlist(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	wishlist=WishList.objects.get(user=user,product=product)
	wishlist.delete()
	return redirect('mywishlist')


def mycart(request):
	total_amount=0
	user=User.objects.get(email=request.session['email'])
	carts=Cart.objects.filter(user=user,status="pending")
	request.session['cart_count']=len(carts)

	for i in carts:
		total_amount=total_amount+int(i.net_price)
	return render(request,'mycart.html',{'carts':carts,'total_amount':total_amount})

def add_to_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	Cart.objects.create(user=user,product=product,product_price=product.product_price,product_qty="1",net_price=product.product_price)
	return redirect('mycart')

def remove_from_cart(request,pk):
	product=Product.objects.get(pk=pk)
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(user=user,product=product)
	cart.delete()
	return redirect('mycart')

def change_qty(request):
	user=User.objects.get(email=request.session['email'])
	cart=Cart.objects.get(id=request.POST['cart_id'],user=user)
	cart.product_qty=request.POST['qty']
	cart.net_price=int(cart.product_price)*int(request.POST['qty'])
	cart.save()
	return redirect('mycart')

def initiate_payment(request):
    try:
        user=User.objects.get(email=request.session['email'])
        amount = int(request.POST['amount'])
        
    except:
        return render(request, 'mycart.html', context={'error': 'Wrong Accound Details or amount'})

    transaction = Transaction.objects.create(made_by=user,amount=amount)
    transaction.save()
    merchant_key = settings.PAYTM_SECRET_KEY

    params = (
        ('MID', settings.PAYTM_MERCHANT_ID),
        ('ORDER_ID', str(transaction.order_id)),
        ('CUST_ID', str(request.session['email'])),
        ('TXN_AMOUNT', str(transaction.amount)),
        ('CHANNEL_ID', settings.PAYTM_CHANNEL_ID),
        ('WEBSITE', settings.PAYTM_WEBSITE),
        # ('EMAIL', request.user.email),
        # ('MOBILE_N0', '9911223388'),
        ('INDUSTRY_TYPE_ID', settings.PAYTM_INDUSTRY_TYPE_ID),
        ('CALLBACK_URL', 'http://localhost:8000/callback/'),
        # ('PAYMENT_MODE_ONLY', 'NO'),
    )

    paytm_params = dict(params)
    checksum = generate_checksum(paytm_params, merchant_key)

    transaction.checksum = checksum
    transaction.save()
    user=User.objects.get(email=request.session['email'])
    carts=Cart.objects.filter(user=user,status="pending")
    for i in carts:
    	i.status="completed"
    	i.save()

    paytm_params['CHECKSUMHASH'] = checksum
    print('SENT: ', checksum)
    return render(request, 'redirect.html', context=paytm_params)


@csrf_exempt
def callback(request):
    if request.method == 'POST':
        received_data = dict(request.POST)
        paytm_params = {}
        paytm_checksum = received_data['CHECKSUMHASH'][0]
        for key, value in received_data.items():
            if key == 'CHECKSUMHASH':
                paytm_checksum = value[0]
            else:
                paytm_params[key] = str(value[0])
        # Verify checksum
        is_valid_checksum = verify_checksum(paytm_params, settings.PAYTM_SECRET_KEY, str(paytm_checksum))
        if is_valid_checksum:
            received_data['message'] = "Checksum Matched"
        else:
            received_data['message'] = "Checksum Mismatched"
            return redirect('mycart')
        return redirect('mycart')
