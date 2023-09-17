from django.contrib import admin
from django.conf import settings
from django.db import models
from django.core.validators import MinValueValidator
from  uuid import uuid4
from .validator import validate_file_size


class Promotion(models.Model):
    description=models.CharField(max_length=255)
    discount=models.FloatField()

class Collection(models.Model):
    title=models.CharField(max_length=255)
    featured_product=models.ForeignKey('Product',on_delete=models.SET_NULL,null=True,blank=True ,related_name='+')
    
    def __str__(self) -> str:
        return self.title

class Product(models.Model):
    title=models.CharField(max_length=255)
    slug=models.SlugField()
    discription=models.TextField()
    price=models.DecimalField(max_digits=6, decimal_places=2,validators=[MinValueValidator(1)])
    inventory=models.IntegerField()
    last_update=models.DateTimeField(auto_now=True)
    collection=models.ForeignKey(Collection,on_delete=models.PROTECT,related_name='products')
    promotions=models.ManyToManyField(Promotion,null=True,blank=True)

    def __str__(self) -> str:
        return self.title
    
    class Meta:
        ordering=['title']

class ProductImage(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='images')
    image=models.ImageField(upload_to='store/images',
                            validators=[validate_file_size])



class Review(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE,related_name='reviews')
    name=models.CharField(max_length=255)
    description=models.TextField()
    date=models.DateField(auto_now_add=True)


class Customer(models.Model): 
    MEMBERSHIP_BRONTH='B'
    MEMBERSHIP_SILVER='S'
    MEMBERSHIP_GOLD='G'
    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_BRONTH,'Bronze'),
        (MEMBERSHIP_SILVER,'Silver'),
        (MEMBERSHIP_GOLD,'Gold')
      ]
    phone=models.CharField(max_length=100)
    birth_date=models.DateField(null=True )
    membership=models.CharField(max_length=1,choices=MEMBERSHIP_CHOICES,default=MEMBERSHIP_BRONTH)
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    
    def __str__(self) -> str:
        return f'{self.user.first_name} {self.user.last_name}'
    @admin.display(ordering='user__first_name')
    def first_name(self):
        return self.user.first_name
    @admin.display(ordering='user__last_name')
    def last_name(self):
        return self.user.last_name
    
    class Meta:
        ordering=['user__first_name','user__last_name']
        permissions=[
            ('view_history','Can View History')
        ]

class Order(models.Model):
    PAYMENT_STATUS_PENDING='P'
    PAYMENT_STATUS_COMPLETE='C'
    PAYMENT_STATUS_FAILED='F'
    PAYMENT_STATUS_CHOICE=[
        (PAYMENT_STATUS_PENDING,'pending'),
        (PAYMENT_STATUS_COMPLETE,'Complate'),
        (PAYMENT_STATUS_FAILED,'Failed')
    ]
    placed_at=models.DateTimeField(auto_now_add=True)
    payment_status=models.CharField(max_length=1,choices=PAYMENT_STATUS_CHOICE,default=PAYMENT_STATUS_PENDING)
    customer=models.ForeignKey(Customer,on_delete=models.PROTECT)

    class Meta:
        permissions=[
            ('cancel_order','can cancel order')
        ]

class OrderItem(models.Model):
    order=models.ForeignKey(Order,on_delete=models.PROTECT,related_name='items')
    product=models.ForeignKey(Product,on_delete=models.PROTECT,related_name='orderitems')
    quantity=models.PositiveSmallIntegerField()
    unit_price=models.DecimalField(max_digits=6,decimal_places=2)

class Adress(models.Model):
    street=models.CharField(max_length=255)
    city=models.CharField(max_length=255)
    Customer=models.OneToOneField(Customer,on_delete=models.CASCADE,primary_key=True)

class Cart(models.Model):
    id=models.UUIDField(primary_key=True,default=uuid4)
    created_at=models.DateTimeField(auto_now_add=True)




class CartItem(models.Model):
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='items')
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity=models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    class Meta:
        unique_together= [['cart','product']]
        


