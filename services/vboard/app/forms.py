from django import forms


class PageForm(forms.Form):
    name = forms.CharField(label='Name page', required=True, min_length=3, max_length=40, error_messages={'min_length':'Слишком мало символов'})
    rating = forms.IntegerField(label='Rating page', required=False, min_value=1, max_value=10)
    content = forms.CharField(label='Content page', widget=forms.Textarea(attrs={'rows': 3, 'cols': 33}))


class UsregForm(forms.Form):
    username = forms.CharField(label='Username', required=True, min_length=3, max_length=32)
    password = forms.CharField(label='Password', required=True, min_length=3, max_length=120, widget=forms.PasswordInput)


class BidForm(forms.Form):
    title = forms.CharField(label='Title', required=True, min_length=3, max_length=32)
    content = forms.CharField(label='Content bid', required=True, max_length=500, widget=forms.Textarea(attrs={'rows': 3, 'cols': 33}))
    serial_key = forms.CharField(label='Serial key', max_length=40, required=False)


class PromoForm(forms.Form):
    idb = forms.CharField(label='ID bid', required=True, min_length=3, max_length=120)
    promo_key = forms.CharField(label='Promo key', required=True, min_length=3, max_length=120)