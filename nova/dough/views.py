# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2012 United States Government as represented by the
# Administrator of the National Aeronautics and Space Administration.
# All Rights Reserved.
#
# Copyright 2012 Nebula, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import logging
from django.utils.translation import ugettext as _

from django.conf import settings

from horizon import usage

#from horizon.api import dough
from horizon import exceptions
from horizon import tables
from .tables import DoughTable
from .tables import ProductsTable 
from horizon import api
#from novaclient.v1_1 import client as nova_client

import iso8601
#from horizon import time
import time
#from dough import client
from dough.client.dough_client import DoughClient

#from horizon.dashboards.nova.images_and_snapshots.images import views
from horizon.forms import DateForm

def tenant_dough_defaults(tenant_id):
    data = None
    client = DoughClient()
    time_from = '2013-01-01T00:00:00'
    time_to = '2013-12-31T00:00:00'
#    time_to = time.strftime('%Y-%m-%dT%H:%M:%S',time.localtime(time.time()))

    data = client.query_monthly_report(tenant_id, time_from, time_to)
    return data


class Doughclient(object):
    def __init__(self,dough_id=0,dough_item=0,dough_region=0,dough_charge=0):
        self.id = dough_id
        self.item = dough_item
        self.region = dough_region
        self.charge = dough_charge

class DoughClt(object):
    def __init__(self,tenant_id):
        self.items = []
        b = tenant_dough_defaults(tenant_id)
        lenb = len(b['data'])
        for i in range(0, lenb):
            d = Doughclient(i+1, b['data'][i]['itemnm'], b['data'][i]['regionnm'], b['data'][i]['linett'])
            self.items.append(d)

def tenant_products_defaults():
    data = None
    client = DoughClient()
    data = client.query_item_products()
    return data


class productsclient(object):
    def __init__(self,products_id=0, products_item=0,products_itemtype=0,products_order_size=0,products_order_unit=0,products_price=0,products_currency=0):
        self.id = products_id
        self.item= products_item 
        self.itemtype= products_itemtype 
        self.order_size = products_order_size 
        self.order_unit = products_order_unit 
        self.price = products_price 
        self.currency = products_currency

class ProductsClt(object):
    def __init__(self):
        self.items = []
        b = tenant_products_defaults()
        lenb = len(b['data'])
        for i in range(0, lenb):
            d = productsclient(i+1, b['data'][i]['item_name'], b['data'][i]['item_type_name'], b['data'][i]['order_size'], b['data'][i]['order_unit'], b['data'][i]['price'], b['data'][i]['currency'])
            self.items.append(d)


LOG = logging.getLogger(__name__)


class IndexView(tables.MultiTableView):
    table_classes = (DoughTable, ProductsTable)
    template_name = 'nova/dough/index.html'

    def get_charge_data(self):
        try:
            tenant_id = self.request.user.tenant_id
            dough_set = DoughClt(tenant_id)
            data = dough_set.items   
        except:
            exceptions.handle(self.request, _('Unable to get dough info.'))
        return data

    def get_products_data(self):
#    def get_DataTableOptions_data(self):
        try:
            products_set = ProductsClt()
            data = products_set.items 
        except:
            exceptions.handle(self.request, _('Unable to get products info.'))
        return data  
            
#def UpdateView(request):
#    if request.method == 'POST':
#        form = DateForm(request.POST)
#            if form.is_valid():
#            return HttpResponseRedirect('/')
#        else:
#            form = ContactForm()                

#        variables = RequestContext(request,{'form':form})
#        return render_to_response('nova/dough/_monthly.html', {'form':form})
