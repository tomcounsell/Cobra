from django import template
from math import ceil as roundUp
register = template.Library()

@register.inclusion_tag('inventory/product_detail.html')
def product_detail_tag(product):
  product.first_photo = product.photo_set.order_by('rank')[0]

  return {'product':product}

@register.inclusion_tag('inventory/sold_product_detail.html')
def sold_product_detail_tag(product):
  product.first_photo = product.photo_set.order_by('rank')[0]
  product.total_cost = product.shipping_cost + product.local_price

  return {'product':product}

@register.inclusion_tag('inventory/photo_upload.html')
def photo_upload_tag(photo_form, product, rank):
  try:
    photo = product.photo_set.get(rank=rank)
  except:
    photo = None

  photo_url = photo.thumb_size  if photo else None
  photo_id  = photo.id          if photo else None

  photo_form.fields['rank'].initial = rank
  photo_form.fields['product'].initial = product.id

  return {'photo_form':photo_form,
          'photo_url':photo_url,
          'photo_id':photo_id,
          'product_id':product.id
         }

@register.inclusion_tag('inventory/product_asset_choosers/asset_chooser.html')
def asset_chooser_tag(request, product, ilk):
  try:
    assets = product.seller.asset_set.filter(ilk=ilk)
  except Exception as e:
    assets = None

  return {'assets':assets, 'ilk':ilk, 'product_id':product.id}

@register.inclusion_tag('inventory/product_asset_choosers/shipping_option_chooser.html')
def shipping_option_chooser_tag(request, product):
  try:
    shipping_options = product.seller.country.shippingoption_set.all()
  except Exception as e:
    shipping_options = None

  return {'shipping_options':shipping_options, 'product_id':product.id}

@register.inclusion_tag('inventory/product_asset_choosers/color_chooser.html')
def color_chooser_tag(product):
  from apps.admin.models import Color
  try:
    colors = Color.objects.all()
  except Exception as e:
    colors = None
  return {'colors':colors, 'product_id':product.id}
