from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from django.core.urlresolvers import reverse
from datetime import datetime

def home(request, seller_id):
  from apps.seller.models import Seller

  try:
    store = Seller.objects.get(id=seller_id)
    store.artisans = store.asset_set.filter(ilk='artisan')

    unsold_products   = store.product_set.filter(sold_at=None)
    approved_products = unsold_products.filter(approved_at__lte=datetime.today())
    active_products   = approved_products.filter(deactive_at=None)
    ordered_products  = active_products.order_by('approved_at').reverse()

    context = {'store':store, 'products':ordered_products}

  except Seller.DoesNotExist:
    return Http404

  except Exception as e:
    context = {'except':e}

  return render(request, 'store.html', context)
