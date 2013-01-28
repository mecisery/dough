import logging

from django.utils.translation import ugettext_lazy as _

from horizon import tables


LOG = logging.getLogger(__name__)


class DoughTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_('Dough Name'))
    limit = tables.Column('qurey', verbose_name=_('Qurey'))
