import logging

from django.utils.translation import ugettext_lazy as _

from horizon import tables


LOG = logging.getLogger(__name__)

class QuotaFilterAction(tables.FilterAction):
    def filter(self, table, dough, filter_string):
        q = filter_string.lower()

        def comp(tenant):
            if q in tenant.item.lower():
                return True
            return False

        return filter(comp, dough)


class DoughTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('Id'))
#    month = tables.Column('month', verbose_name=_('Month'))
    item = tables.Column('item', verbose_name=_('Item')) 
    region = tables.Column('region', verbose_name=_('Region'))
    charge = tables.Column('charge', verbose_name=_('Charge'))

    def get_object_id(self, obj):
        return obj.id

    class Meta:
        name = "charge"
        verbose_name = _("Charge")
        table_actions = (QuotaFilterAction,)
        multi_select = False

class ProductsTable(tables.DataTable):
    id = tables.Column('id', verbose_name=_('Id'))
    item = tables.Column('item', verbose_name=_('Item'))
    itemtype = tables.Column('itemtype', verbose_name=_('Itemtype'))
    order_size = tables.Column('order_size', verbose_name=_('Order_size'))
    order_unit= tables.Column('order_unit', verbose_name=_('Order_unit'))
    price = tables.Column('price', verbose_name=_('Price'))
    currency = tables.Column('currency', verbose_name=_('Currency'))

    def get_object_id(self, obj):
         return obj.id

    class Meta:
        name = "products"
        verbose_name = _("Products")
        multi_select = False
