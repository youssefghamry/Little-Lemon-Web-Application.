from rest_framework import serializers
from .models import MenuItem, Category, User, Cart, Order, OrderItem

class CategorySerializer (serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id','title']

class MenuItemSerializer (serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = ['id','title','price','featured','category']

class UserSerializer (serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']

class CartSerializer (serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['id','user','menuitem','quantity','unit_price','price']

class OrderSerializer (serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id','user','delivery_crew','status','total','date']

class OrderItemSerializer (serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id','order','menuitem','quantity','unit_price','price']