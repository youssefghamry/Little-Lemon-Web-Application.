from django.shortcuts import render, get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from .models import MenuItem, Category, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, UserSerializer, CartSerializer, OrderSerializer, OrderItemSerializer

from django.contrib.auth.models import User, Group
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.core.paginator import Paginator, EmptyPage

from datetime import date


# List All Menu Items
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def MenuItems(request):
    if request.method == 'GET':
        query_params = request.query_params
        category = query_params.get('category')
        featured = query_params.get('featured')
        max_price = query_params.get('to_price')
        ordering = query_params.get('ordering')
        search = query_params.get('search')
        perpage = query_params.get('perpage', default=2)
        page = query_params.get('page', default=1)

        items = MenuItem.objects.all()
        if category:
            items = items.filter(category__title=category)
        if featured:
            items = items.filter(featured=featured)
        if max_price:
            items = items.filter(price__lte = max_price)
        if search:
            items = items.filter(title__contains = search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)

        paginator = Paginator(items, per_page=perpage)
        try:
            items = paginator.page(number=page)
        except EmptyPage:
            items = []
        serializer = MenuItemSerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'POST':
        user = request.user
        if user.groups.filter(name='Manager').exists():
            # User is a manager, allowed to create menu items
            serializer = MenuItemSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            # User is not a manager, unauthorized to create menu items
            return Response(status=status.HTTP_403_FORBIDDEN)
    else:
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


# Single Menu Items
@api_view(['GET','DELETE','PUT','PATCH'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def SingleMenuItems(request, id):
    user = request.user
    items = get_object_or_404(MenuItem, pk=id)
    
    if request.method == 'GET':
        serializer = MenuItemSerializer(items)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif user.groups.filter(name='Manager').exists():
        if request.method == 'PUT' or request.method == 'PATCH':
            serializer = MenuItemSerializer(items, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        elif request.method == 'DELETE':
            items.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    else:
        return Response(status=status.HTTP_403_FORBIDDEN)


@api_view(['GET','POST'])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle])
def categories(request):
    if request.method == 'GET':
        items = Category.objects.all()
        serializer = CategorySerializer(items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    return Response(status=status.HTTP_403_FORBIDDEN)

# Assign user to managers group
@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
@throttle_classes([UserRateThrottle])
def managers(request):
    user = request.user
    if user.groups.filter(name='Manager').exists():
        if request.method == 'GET':
            managers = Group.objects.get(name="Manager")
            managers_users = managers.user_set.all()
            serializer = UserSerializer(managers_users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            username = request.data['username']
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name="Manager")
            managers.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)

@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def SingleManagerView(request, id):
    user = request.user

    try:
        managers_crew = User.objects.get(id=id, groups__name='Manager')
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if user.groups.filter(name='Manager').exists():
        if request.method == 'GET':
            serializer = UserSerializer(managers_crew)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            managers = Group.objects.get(name="Manager")
            managers.user_set.remove(managers_crew)
            return Response(status=status.HTTP_200_OK)


    return Response(status=status.HTTP_403_FORBIDDEN)


# Delivery-Crew
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def DeliveryCrew(request):
    user = request.user
    if user.groups.filter(name='Manager').exists():
        if request.method == 'GET':
            delivcrew = Group.objects.get(name="delivery_crew")
            delivcrew_users = delivcrew.user_set.all()
            serializer = UserSerializer(delivcrew_users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif request.method == 'POST':
            username = request.data['username']
            user = get_object_or_404(User, username=username)
            delivcrew = Group.objects.get(name="delivery_crew")
            delivcrew.user_set.add(user)
            return Response(status=status.HTTP_201_CREATED)
        
@api_view(['GET', 'DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def SingleDeliveryCrew(request, id):
    user = request.user

    try:
        delivery_crew = User.objects.get(id=id, groups__name='delivery_crew')
    except User.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if user.groups.filter(name='Manager').exists():
        if request.method == 'GET':
            serializer = UserSerializer(delivery_crew)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'DELETE':
            delivcrew = Group.objects.get(name="delivery_crew")
            delivcrew.user_set.remove(delivery_crew)
            return Response(status=status.HTTP_200_OK)


    return Response(status=status.HTTP_403_FORBIDDEN)


# Views for Cart       
@api_view(['GET','POST','DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def ViewCart(request):
    user = request.user
    
    if request.method == 'GET':
        user_cart = Cart.objects.filter(user=user)
        serializer = CartSerializer(user_cart, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    elif request.method == 'POST':
        # user_id = user.id
        menuitem_id = request.data['menuitem']
        quantity = request.data['quantity']
        menuitem = get_object_or_404(MenuItem, id=menuitem_id)
        price = quantity * menuitem.price

        cart_item = Cart(user=user, menuitem=menuitem, quantity=quantity, unit_price=menuitem.price, price=price)
        cart_item.save()
        return Response(status=status.HTTP_201_CREATED)
    elif request.method == 'DELETE':
        user_cart = Cart.objects.filter(user=user)
        user_cart.delete()
        return Response({"message": "Cart items deleted"}, status=status.HTTP_204_NO_CONTENT)
    
# Views for order
@api_view(['GET','POST'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def ViewOrder(request):
    user = request.user

    if request.method == 'POST':
        cart_items = Cart.objects.filter(user=user)

        # Iterate over cart items and create order items
        total_price = 0
        for cart_item in cart_items:
            order_item = OrderItem(
                order=user,
                menuitem=cart_item.menuitem,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                price=cart_item.price
            )
            total_price += cart_item.price
            order_item.save()

        # Clear the cart items for the user
        cart_items.delete()
        
        # Craete new order
        today = date.today()
        new_order = Order(user=user, date=today, total=total_price)
        new_order.save()
        return Response({"message": "Order placed successfully"}, status=status.HTTP_201_CREATED)
    
    elif request.method == 'GET':
        query_params = request.query_params
        menuitem = query_params.get('menuitem')
        order_id = query_params.get('order')
        ordering = query_params.get('ordering')
        search = query_params.get('search')
        perpage = query_params.get('perpage', default=2)
        page = query_params.get('page', default=1)

        items = OrderItem.objects.all()
        if menuitem:
            items = items.filter(menuitem__title=menuitem)
        if order_id:
            items = items.filter(order=order_id)
        if search:
            items = items.filter(menuitem__title__contains = search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)


        if user.groups.filter(name='Manager').exists():
            # order = OrderItem.objects.all()
            paginator = Paginator(items, per_page=perpage)
            try:
                items = paginator.page(number=page)
            except EmptyPage:
                items = []
            serializer = OrderItemSerializer(items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        elif user.groups.filter(name='delivery_crew').exists():
            related_order = Order.objects.filter(delivery_crew = user)
            # related_order = items.filter(delivery_crew = user)
            for orderval in related_order:
                user_id = orderval.user

            # items = items.filter(order=user_id)
            items = items.filter(order=user_id)
            paginator = Paginator(items, per_page=perpage)
            try:
                items = paginator.page(number=page)
            except EmptyPage:
                items = []
            serializer = OrderItemSerializer(items, many=True)
            # serializer = OrderSerializer(related_order, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # elif user.groups.filter(name='delivery-crew').exists():
        #     related_orders = Order.objects.filter(delivery_crew=user)
        #     order_items = OrderItem.objects.filter(order__in=related_orders)
        #     serializer = OrderItemSerializer(order_items, many=True)
        #     return Response(serializer.data, status=status.HTTP_200_OK)

        else:
            # order = OrderItem.objects.filter(order=user)
            items = items.filter(order=user)
            paginator = Paginator(items, per_page=perpage)
            try:
                items = paginator.page(number=page)
            except EmptyPage:
                items = []
            serializer = OrderItemSerializer(items, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET','PUT','PATH','DELETE'])
@permission_classes([IsAuthenticated])
@throttle_classes([UserRateThrottle])
def OrderSummary(request, id):
    user = request.user
    order = get_object_or_404(Order, pk=id)
    # orderitem = get_object_or_404(OrderItem, order=user)
    

    if request.method == 'GET':
        if user.groups.filter(name='Manager').exists():
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif user.groups.filter(name='delivery_crew').exists():
            if order.delivery_crew == user:
                serializer = OrderSerializer(order)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response({"message": "This order assigned to another delivery crew"}, status=status.HTTP_403_FORBIDDEN)
        else:
            if order.user != user:
                return Response({"message": "You cannot view someone else's order"}, status=status.HTTP_403_FORBIDDEN)
        
            serializer = OrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT' or request.method == 'PATCH':
        # Manager Role: Can assign delivery crew and or update status
        if user.groups.filter(name='Manager').exists():
            delivery_crew_id = request.data['delivery_crew']

            try:
                delivery_crew = User.objects.get(id=delivery_crew_id)
                if not delivery_crew.groups.filter(name='delivery_crew').exists():
                    raise User.DoesNotExist
                order.delivery_crew = delivery_crew
                # Rest of your code
            except User.DoesNotExist:
                return Response({"message": "Invalid delivery crew ID"}, status=status.HTTP_400_BAD_REQUEST)
            
            status_new = request.data['status']
            # order.delivery_crew = delivery_crew
            order.status = status_new
            order.save()
            return Response({"Message":"Delivery crew has been assigned"}, status=status.HTTP_201_CREATED)
        # Delivery crew role: can update status
        elif user.groups.filter(name='delivery_crew').exists():
            status_new = request.data['status']
            order.status = status_new
            order.save()
            return Response({"Message":"Order status updated"}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message":"Order can be changed"}, status=status.HTTP_401_UNAUTHORIZED)
        # return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    elif request.method == 'DELETE':
        if user.groups.filter(name='Manager').exists():
            order.delete()
            # orderitem.delete()
            return Response({"message": "Order Complete!"}, status=status.HTTP_204_NO_CONTENT)