from django.db import models
from django.utils import timezone
# Create your models here.
class Contact(models.Model):
	name=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	remarks=models.TextField()

	def __str__(self):
		return self.name

class User(models.Model):
	fname=models.CharField(max_length=100)
	lname=models.CharField(max_length=100)
	email=models.CharField(max_length=100)
	mobile=models.CharField(max_length=100)
	password=models.CharField(max_length=100)
	cpassword=models.CharField(max_length=100)
	status=models.CharField(max_length=100,default="inactive")
	usertype=models.CharField(max_length=100,default="user")

	def __str__(self):
		return self.fname+" "+self.lname

class Product(models.Model):

	Choices=(
        ('Kids','Kids'),
        ('Women','Women'),
        ('Men','Men'))
	product_seller=models.ForeignKey(User,on_delete=models.CASCADE)
	product_name=models.CharField(max_length=100)
	product_price=models.CharField(max_length=100)
	product_image=models.ImageField(upload_to='images/')
	product_desc=models.TextField()
	product_category=models.CharField(max_length=100,choices=Choices)

	def __str__(self):
		return self.product_seller.fname+" - "+self.product_name

class WishList(models.Model):

	user=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)

	def __str__(self):
		return self.user.fname+" - "+self.product.product_name

class Cart(models.Model):

	user=models.ForeignKey(User,on_delete=models.CASCADE)
	product=models.ForeignKey(Product,on_delete=models.CASCADE)
	date=models.DateTimeField(default=timezone.now)
	product_price=models.CharField(max_length=100,default="")
	product_qty=models.CharField(max_length=100,default="")
	net_price=models.CharField(max_length=100,default="")
	status=models.CharField(max_length=100,default="pending")

	def __str__(self):
		return self.user.fname+" - "+self.product.product_name

class Transaction(models.Model):
	
    made_by = models.ForeignKey(User, related_name='transactions', 
                                on_delete=models.CASCADE)
    made_on = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField()
    order_id = models.CharField(unique=True, max_length=100, null=True, blank=True)
    checksum = models.CharField(max_length=100, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.order_id is None and self.made_on and self.id:
            self.order_id = self.made_on.strftime('PAY2ME%Y%m%dODR') + str(self.id)
        return super().save(*args, **kwargs)