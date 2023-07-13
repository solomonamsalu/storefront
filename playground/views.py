from django.shortcuts import render
from django.http import HttpResponse
from store.models import Product,OrderItem
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q,F


def say_hello(request):
        product=OrderItem.objects.values('product__id').distinct().order_by('id')
        return render(request,'hello.html',{'product':product})
    
# Create your views here.
#request->_ 