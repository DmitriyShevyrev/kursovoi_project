from django import forms


class OrderCreateForm(forms.Form):
    first_name = forms.CharField(
        max_length=100,
        label='Имя',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        max_length=100,
        label='Фамилия',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    address = forms.CharField(
        label='Адрес доставки',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
    )
