from django.db import models
from django import forms
from seller.models import Asset, Product, Seller
from admin.models import Category

class SellerEditForm(forms.Form):
  from admin.models import Country, Currency
  name      = forms.CharField()
  email     = forms.EmailField(required=False)
  phone     = forms.CharField(required=False)
  bio       = forms.CharField(widget=forms.Textarea(attrs={'class':"description"}),
                              required=False)
  country   = forms.ModelChoiceField(queryset=Country.objects.all())
  currency  = forms.ModelChoiceField(queryset=Currency.objects.all())

  def clean_phone(self):
    phone = self.cleaned_data['phone']
    #require country code
    phone = phone.translate(None, string.digits)
    if 10 <= len(phone) <= 14:
      return phone
    else:
      return error

class AssetProductForm(forms.Form):
  ilk         = forms.CharField(widget=forms.TextInput(attrs={'class':"ilk"}),
                                initial='product')
  #image takes id of image after ajax upload
  image       = forms.CharField(widget=forms.TextInput(attrs={'class':"image_text"}))
  name        = forms.CharField(widget=forms.TextInput(
                                attrs={'class':"name", 'placeholder':"Name/Smiya"}),
                                max_length=50, required=False)
  description = forms.CharField(widget=forms.Textarea(
                                attrs={'class':"description", 'placeholder':"description"}),
                                required=False)
  category    = forms.ModelMultipleChoiceField( widget=forms.SelectMultiple(),
                                                queryset=Category.objects.all())
  ORDER       = forms.CharField(widget=forms.TextInput(attrs={'class':"order"}))
  DELETE      = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':"delete"}))

class AssetForm(forms.Form):
  ilk         = forms.CharField(widget=forms.TextInput(attrs={'class':"ilk"}))
  #image takes id of image after ajax upload
  image       = forms.CharField(widget=forms.TextInput(attrs={'class':"image_text"}))
  name        = forms.CharField(widget=forms.TextInput(
                                attrs={'class':"name", 'placeholder':"Name/Smiya"}),
                                max_length=50, required=False)
  description = forms.CharField(widget=forms.Textarea(
                                attrs={'class':"description", 'placeholder':"description"}),
                                required=False)
  ORDER       = forms.CharField(widget=forms.TextInput(attrs={'class':"order"}))
  DELETE      = forms.BooleanField(widget=forms.CheckboxInput(attrs={'class':"delete"}))

class ImageForm(forms.Form):#a form for posting directly to S3
  action      = "http://anou.s3.amazonaws.com/"
  file        = forms.FileField()
  key         = forms.CharField()
  #acl        = forms.CharField(type='hidden', default='public-read', editable=False)
  #policy     = forms.CharField(default='POLICY', editable=False)
  #signature  = forms.CharField(default='SIGNATURE', editable=False)
