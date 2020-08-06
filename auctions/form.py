from django import forms

CATEGORIES = [
    ("Home", "Home"),
    ("Technology", "Technology"),
    ("Sport", "Sport"),
    ("Fashion", "Fashion")
]

"""
Source: https://docs.djangoproject.com/en/3.0/topics/forms/#rendering-fields-manually
        https://docs.djangoproject.com/en/3.0/ref/forms/widgets/
"""

class ListingForm(forms.Form):
    # widget là các thể sẽ đc render trong html TextInput <=> <input type = "text"...>
    # attrs là các atributes của thẻ, phải đi kẻm widget
    title = forms.CharField(min_length = 5, max_length = 64, widget=forms.TextInput (attrs={'class':'form-control'}))
    
    # Các thẻ select có biến "choices" để thêm vào các <option>
    category = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), choices = CATEGORIES)
    description = forms.CharField(min_length = 10, max_length = 256, widget=forms.TextInput(attrs={'class':'form-control'}))
    starting_bid = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control'}))

    # Thêm value để user ko nhập xâu gì thì vx submit đc
    image = forms.URLField(min_length = 0, max_length = 2048, widget=forms.URLInput
                          (attrs={'class':'form-control', 
                                  'value':'https://bom.to/79jrla'}))

class BidForm(forms.Form):
    money = forms.FloatField(widget=forms.NumberInput(attrs={'class':'form-control', 'placeholder':'Place bid'}))                               


RATINGS= [
    (5, "Excellent"),
    (4, "Good"),
    (3, "Normal"),
    (2, "Bad"),
    (1, "Terrible")
]

class CommentForm(forms.Form):
    comment_content = forms.CharField(max_length = 512, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder':'Add Comment'}))
    comment_rating = forms.ChoiceField(widget=forms.Select(attrs={'class':'form-control'}), choices = RATINGS)