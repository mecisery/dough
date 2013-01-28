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

from horizon.api import dough
from horizon import exceptions
from horizon import tables
from .tables import DoughTable

#from novaclient.v1_1 import client as nova_client

#from dough import client
from dough.client.dough_client import DoughClient

def tenant_dough_defaults():

    data = None
    client = DoughClient()
    tenant_id = '246eaa20db2b4a0c8939446c5db63288'
    time_from = '2012-12-01T00:00:00'
    time_to = '2012-12-31T00:00:00'

    data = client.query_monthly_report(tenant_id, time_from, time_to)
    return data


LOG = logging.getLogger(__name__)


class IndexView(tables.DataTableView):
    table_class = DoughTable
    template_name = 'nova/dough/index.html'

    def get_data(self):
        try:
            data = tenant_dough_defaults()
#             data = doughclt()
        except:
            exceptions.handle(self.request, _('Unable to get dough info.'))
        return data
