from django import forms
from django.forms.widgets import NumberInput


class CreateForm(forms.Form):
    title = forms.CharField(label="Name of your NFT", max_length=64)
    description = forms.CharField(label="Description of your NFT", widget=forms.Textarea(attrs={'rows': 3}), max_length=400)
    image = forms.URLField(label="URL to your NFT", max_length=200, error_messages={
        'task': {'max_length': ("Error: maximum length limit is 255 characters")}
    })
    price = forms.IntegerField(label="Price")
    starting_price = forms.IntegerField(label="Bidding starting price:")
    date_created = forms.DateField(widget=NumberInput(attrs={'type': 'date'}))


class BidForm(forms.Form):
    bid = forms.IntegerField(label="Bid")
