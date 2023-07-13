from store.signals import order_created
from django.dispatch import receiver

@receiver(order_created)
def  on_order_created(Sender,**kwargs):
    print(kwargs['order'])