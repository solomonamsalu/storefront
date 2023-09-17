from django.shortcuts import render
from django.http import HttpResponse
from store.models import Product,OrderItem
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q,F
from django.core.mail import EmailMessage,BadHeaderError
from templated_mail.mail import BaseEmailMessage


def say_hello(request):
        try:
             message=BaseEmailMessage(
                    template_name='email/hello.html',
                    context={'name':'Mosh'}
             )
             message.send(['john@moshbuy.com'])
        except BadHeaderError:
                pass
        return render(request,'hello.html',{'name':"Mosh"})
    
