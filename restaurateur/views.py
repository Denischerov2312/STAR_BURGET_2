import copy
from django import forms
from django.shortcuts import redirect, render, get_object_or_404
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Prefetch

from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views


from foodcartapp.models import Product, Restaurant, Order, OrderItem, RestaurantMenuItem
from foodcartapp.geocoding import get_coordinates, calculate_distance
from .forms import OrderForm, OrderItemFormSet


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name').only('id', 'name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    products_with_restaurant_availability = []
    for product in products:
        availability = {item.restaurant_id: item.availability for item in product.menu_items.all()}
        ordered_availability = [availability.get(restaurant.id, False) for restaurant in restaurants]

        products_with_restaurant_availability.append(
            (product, ordered_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurant_availability': products_with_restaurant_availability,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    orders = Order.objects.count_total_cost().prefetch_related(
        Prefetch('items', queryset=OrderItem.objects.select_related('product'))
    )

    menu_items = RestaurantMenuItem.objects.filter(
        availability=True
    ).values_list('restaurant_id', 'product_id')

    restaurant_products = {}
    for rest_id, prod_id in menu_items:
        restaurant_products.setdefault(rest_id, set()).add(prod_id)

    restaurants_by_id = {r.id: r for r in Restaurant.objects.defer('contact_phone')}

    for restaurant in restaurants_by_id.values():
        if restaurant.lat is None or restaurant.lon is None:
            restaurant.coords = get_coordinates(restaurant.address)
        else:
            restaurant.coords = (restaurant.lon, restaurant.lat)

    for order in orders:
        order.coords = get_coordinates(order.address)
        order_product_ids = {item.product_id for item in order.items.all()}

        suitable_restaurants = []
        if order_product_ids:
            for rest_id, prod_ids in restaurant_products.items():
                if order_product_ids.issubset(prod_ids):
                    restaurant = restaurants_by_id[rest_id]
                    rest_copy = copy.copy(restaurant)

                    if order.coords and rest_copy.coords:
                        rest_copy.distance = calculate_distance(
                            order.coords, rest_copy.coords
                        )
                    else:
                        rest_copy.distance = None

                    suitable_restaurants.append(rest_copy)

        order.suitable_restaurants = sorted(
            suitable_restaurants, key=lambda r: (r.distance is None, r.distance)
        )

    return render(request, 'order_items.html', context={'order_items': orders})


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_order(request, order_id):
    order = get_object_or_404(
        Order.objects.count_total_cost().prefetch_related(
            Prefetch('items', queryset=OrderItem.objects.select_related('product'))
        ),
        id=order_id
    )
    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            return redirect('restaurateur:view_order', order_id=order.id)
    else:
        form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)

    order.coords = get_coordinates(order.address)
    suitable_restaurants = list(order.get_available_restaurants())

    for restaurant in suitable_restaurants:
        restaurant.coords = get_coordinates(restaurant.address)
        if order.coords and restaurant.coords:
            restaurant.distance = calculate_distance(
                order.coords, restaurant.coords
            )
        else:
            restaurant.distance = None

    order.suitable_restaurants = sorted(
        suitable_restaurants, key=lambda r: (r.distance is None, r.distance)
    )

    return render(
        request,
        'order_details.html',
        context={
            'order': order,
            'form': form,
            'formset': formset,
        },
    )


@user_passes_test(is_manager, login_url='restaurateur:login')
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        order_form = OrderForm(request.POST, instance=order)
        formset = OrderItemFormSet(request.POST, instance=order)

        if order_form.is_valid() and formset.is_valid():
            order_form.save()
            formset.save()
            return redirect('restaurateur:view_order', order_id=order.id)
    else:
        order_form = OrderForm(instance=order)
        formset = OrderItemFormSet(instance=order)

    return render(request, 'order_edit.html', {
        'order': order,
        'order_form': order_form,
        'formset': formset,
    })