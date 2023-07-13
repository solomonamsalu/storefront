from django.db.models.aggregates import Count
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework  import status
from rest_framework.permissions import IsAuthenticated,DjangoModelPermissions,IsAdminUser
from rest_framework.filters import SearchFilter,OrderingFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.viewsets import ModelViewSet,GenericViewSet
from rest_framework.mixins import CreateModelMixin,DestroyModelMixin,RetrieveModelMixin,UpdateModelMixin
from .models import Product,Collection,OrderItem,Review,Cart,CartItem
from .serializers import *
from .filters import ProductFilter
from .permissions import IsAdminOrReadOnly,FUllDjangoModelPermissions,ViewCustomerHistoryPermission


class ProdcutViewSet(ModelViewSet):
      queryset=Product.objects.all()
      serializer_class=ProductSerializer
      filter_backends=[DjangoFilterBackend,SearchFilter,OrderingFilter]
      filterset_class=ProductFilter
      permission_classes=[IsAdminOrReadOnly]
      search_fields=['title']
      ordering_fields=['price','last_update']
      

      def get_serializer_context(self):
           return{'request':self.request}
      
      def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() >0:
          return Response({'error':'product cannot be deleted because it is associated an order item.'},status=status.HTTP_405_METHOD_NOT_ALLOWED )
        return super().destroy(request, *args, **kwargs)
      
          
            

class collectionViewSet(ModelViewSet):
     queryset=Collection.objects.annotate(
         products_count=Count('products')
     )
     serializer_class=CollectionSerailizer   
     permission_classes=[IsAdminOrReadOnly]      

     def delete(self,request,pk): 
        collection=get_object_or_404(Collection,pk=pk)
        if collection.products.count()>0:
            return Response({'error':'Collection cannt be deleted'})  
        collection.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)    
     
class ReviewViewSet(ModelViewSet):
    serializer_class=ReviewSerializer
    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])
    def get_serializer_context(self):
        return {'product_id':self.kwargs['product_pk']} 


class CartViewSet(CreateModelMixin,RetrieveModelMixin,GenericViewSet,DestroyModelMixin):
    queryset=Cart.objects.all() 
    serializer_class=CartSerializer
    filter_backends=[SearchFilter]
    search_fields=['id']
    def get_serializer_context(self):
           return{'request':self.request}
    


class CartItemViewSet(ModelViewSet):
    http_method_names=['get','post','patch','delete']
    def get_serializer_class(self):
        if self.request.method=='POST':
            return AddCartItemSerializer
        elif self.request.method=='PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer
    
    def get_serializer_context(self):
        return {'cart_id':self.kwargs['cart_pk']}

    def get_queryset(self):
        return CartItem.objects\
            .filter(cart_id=self.kwargs['cart_pk'])\
            .select_related('product')

class CustomerViewSet(ModelViewSet):
    queryset=Customer.objects.all()
    serializer_class=CustomerSerializer
    permission_classes=[IsAdminUser]

    @action(detail=True,permission_classes=[ViewCustomerHistoryPermission])
    def history(self,request,pk):
        return Response('ok')

    @action(detail=False,methods=['GET','PUT'],permission_classes=[IsAuthenticated])
    def me(self,request):
        customer=Customer.objects.get(user_id=request.user.id)
        if request.method=='GET':
            serializers=CustomerSerializer(customer)
            return Response(serializers.data)
        elif request.method=='PUT':
            serializer=CustomerSerializer(customer,data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)



class OrderViewSet(ModelViewSet):
    http_method_names=['get','post','patch','delete','head','options']

    def get_permissions(self):
        if  self.request.method in ['PATCH','DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer=CreateOrderSerializer(
            data=request.data,
            context={'user_id':self.request.user.id})
        serializer.is_valid(raise_exception=True)
        order=serializer.save()
        serializer=OrderSerialiser(order)
        return Response(serializer.data)

    def get_serializer_class(self):
        if  self.request.method=='POST':
            return CreateOrderSerializer
        if self.request.method=='PATCH':
            return UpdateOrderSerializer
        return OrderSerialiser
    
    def get_serializer_context(self):
        return {'user_id':self.request.user.id}

    def get_queryset(self):
        user=self.request.user
        if user.is_staff:
            return Order.objects.all()
        customer_id=Customer.objects.only('id').get(user_id=user.id)
        return Order.objects.filter(customer_id=customer_id)