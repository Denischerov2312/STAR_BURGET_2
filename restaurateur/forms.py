from django import forms
from django.forms import inlineformset_factory
from foodcartapp.models import Order, OrderItem


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status', 'comment', 'firstname', 'lastname', 'phonenumber', 'address', 'payment_method']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Внутренние заметки к заказу...'}),
            'firstname': forms.TextInput(attrs={'class': 'form-control'}),
            'lastname': forms.TextInput(attrs={'class': 'form-control'}),
            'phonenumber': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
        }


OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    fields=['quantity'],
    extra=0,
    can_delete=False,
    widgets={
        'quantity': forms.NumberInput(attrs={
            'class': 'form-control',
            'min': 1,
            'style': 'max-width: 100px;',
        }),
    }
)