from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render, redirect
from django.core.urlresolvers import reverse
from django.contrib import messages
import json
from apps.admin.utils.decorator import access_required
from apps.admin.utils.exception_handling import ExceptionHandler
from django.views.decorators.csrf import csrf_exempt
from apps.seller.models.shipping_option import ShippingOption
from apps.seller.models.seller import Seller
from apps.seller.models.product import Product
from apps.seller.models.asset import Asset
from apps.admin.models import Color

@access_required('admin or seller')
def edit(request, product_id):
  from apps.seller.controller.forms import ProductEditForm
  from settings.settings import CLOUDINARY

  try:
    if request.session.get('admin_type') in ['master','country','trainer']:
      product = Product.objects.get(id=product_id)
    else:
      product = Product.objects.get(id=product_id,
                                    seller_id=request.session['seller_id'])

    product_form = ProductEditForm()
    product_form.fields['price'].initial  = product.price
    product_form.fields['length'].initial = product.length
    product_form.fields['width'].initial  = product.width
    product_form.fields['height'].initial = product.height
    product_form.fields['weight'].initial = product.weight

    for asset in product.assets.all():
      product_form.fields['assets'].initial += str(asset.id)+" "

    for color in product.colors.all():
      product_form.fields['colors'].initial += str(color.id)+" "

    for shipping_option in product.shipping_options.all():
      product_form.fields['shipping_options'].initial += str(shipping_option.id)+" "

    product_form.fields['product_id'].initial = product.id

    product.photos = product.photos.order_by('rank')#todo: remove, unnecessary

    context = {
      'product':          product,
      'product_form':     product_form,
      'CLOUDINARY':       CLOUDINARY,
    }
    return render(request, 'edit_product/edit.html', context)

  except Exception as e:
    error_message = "in inventory.edit with product %s" % str(product_id)
    ExceptionHandler(e, error_message)
    return redirect('seller:home')

@access_required('admin or seller')
@csrf_exempt
def saveProduct(request): #ajax requests only, not asset-aware #todo change name to updateProduct
  response = {}

  if request.method == 'GET': # it must be an ajax GET to work
    try:
      if request.session.get('admin_type') in ['master','country','trainer']:
        product = Product.objects.get(id=request.GET.get('product_id'))
      else:
        product = Product.objects.get(id=request.GET.get('product_id'),
                                      seller_id = request.session['seller_id'])

      if request.GET.get('activate') == "yes":
        product.is_active = True
        product.save()

      attribute = request.GET.get('attribute', None)
      status    = request.GET.get('status', None)
      value     = request.GET.get('value', None)
      value     = int(round(float(value))) if value else None

      if attribute == "asset":
        try:
          asset = (Asset.objects.filter(seller=product.seller) #asset belongs to seller
                   .get(id=request.GET.get('asset_id')))
          if status == "active":
            product.assets.add(asset)
            response['asset'] = "added asset %d" % asset.id
          else:
            product.assets.remove(asset)
            response['asset'] = "removed asset %d" % asset.id
        except Asset.DoesNotExist:
          response['asset'] = "asset does not exist"
        except Exception as e:
          response['asset'] = str(e)

      elif attribute == "shipping option":
        try:
          shipping_option = ShippingOption.objects.get(
                              id=request.GET.get('shipping_option_id'))
          if status == "active":
            product.shipping_options.add(shipping_option)
            response['shipping_option'] = "added shipping option %d" % shipping_option.id
          else:
            product.shipping_options.remove(shipping_option)
            response['shipping_option'] = "removed shipping option %d" % shipping_option.id
        except ShippingOption.DoesNotExist:
          response['shipping_option'] = "shipping option does not exist"
        except Exception as e:
          response['shipping_option'] = str(e)

      elif attribute == "color":
        try:
          color = Color.objects.get(id=request.GET.get('color_id'))
          if status == "active":
            product.colors.add(color)
            response['color'] = "added color %s" % color.name
          else:
            product.colors.remove(color)
            response['color'] = "removed color %s" % color.name
        except Color.DoesNotExist:
          response['color'] = "color does not exist"
        except Exception as e:
          response['color'] = str(e)

      elif attribute == "active":
        if status == "yes":
          product.is_active = True
        else:
          product.is_active = False


      elif attribute == 'price':    product.price = value
      elif attribute == 'length':   product.length = value
      elif attribute == 'width':    product.width = value
      elif attribute == 'height':   product.height = value
      elif attribute == 'weight':   product.weight = value

      else: #final else after all other possible options
        raise Exception('attribute does not exist')

      cost_summary = {
        'summary_price': str(product.price) if product.price else "",
        'summary_shipping_cost': str(product.shipping_cost)
      }
      response.update(cost_summary)
      response['is_complete'] = product.is_complete

      #save product only at the very end
      product.is_approved = False
      product.save()

    except Exception as e:
      ExceptionHandler(e, "in inventory.saveProduct")
      response = {'exception': str(e)}

  else:
    response['problem'] = "not GET"

  return HttpResponse(json.dumps(response), content_type='application/json')
  #return HttpResponse(response['exception'])