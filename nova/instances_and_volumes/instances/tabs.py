# vim: tabstop=4 shiftwidth=4 softtabstop=4

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

from django.utils.translation import ugettext_lazy as _

from horizon import api
from horizon import exceptions
from horizon import tabs
from nova import utils
from datetime import datetime
import time
import json


class OverviewTab(tabs.Tab):
    name = _("Overview")
    slug = "overview"
    template_name = ("nova/instances_and_volumes/instances/"
                     "_detail_overview.html")

    def get_context_data(self, request):
        return {"instance": self.tab_group.kwargs['instance']}


class LogTab(tabs.Tab):
    name = _("Log")
    slug = "log"
    template_name = "nova/instances_and_volumes/instances/_detail_log.html"
    preload = False

    def get_context_data(self, request):
        instance = self.tab_group.kwargs['instance']
        try:
            data = api.server_console_output(request,
                                            instance.id,
                                            tail_length=35)
        except:
            data = _('Unable to get log for instance "%s".') % instance.id
            exceptions.handle(request, ignore=True)
        return {"instance": instance,
                "console_log": data}


class MonitoringTab(tabs.Tab):
    name = _("Monitoring")
    slug = "Monitoring"
    template_name = "nova/instances_and_volumes/instances/_detail_monitoring.html"
    preload = False

    def get_context_data(self, request):
        instance = self.tab_group.kwargs['instance']
        scf = 'total'
        statistic = 'avg'
        period = 10
        time_to = utils.utcnow().isoformat()
        time_from = datetime.fromtimestamp(utils.utcnow_ts() - 24 * 60 * 60).isoformat()
        cpu_data = api.get_instance_data(instance.id, 'cpu', scf, statistic, period, time_to, time_from)
        mem_max_data = api.get_instance_data(instance.id, 'mem_max', scf, statistic, period, time_to, time_from)
        mem_free_data = api.get_instance_data(instance.id, 'mem_free', scf, statistic, period, time_to, time_from)

        host = getattr(instance, "OS-EXT-SRV-ATTR:host", None)
        instance_name = getattr(instance, "OS-EXT-SRV-ATTR:instance_name", None)
        if(host):
            detail = api.get_instance_detail(instance_name, host)
            blk_read, blk_write, blk_name = list(), list(), list()
            nic_incoming, nic_outgoing, nic_name = list(), list(), list()
            for blk in detail['blk_devs']:
                if(blk):
                    blk_read.append(api.get_instance_data(instance.id, 'blk_read', blk, statistic, period, time_to, time_from))
                    blk_write.append(api.get_instance_data(instance.id, 'blk_write', blk, statistic, period, time_to, time_from))
                    blk_name.append(blk)
            for nic in detail['nic_devs']:
                if(nic):
                    nic_incoming.append(api.get_instance_data(instance.id, 'nic_incoming', nic, statistic, period, time_to, time_from))
                    nic_outgoing.append(api.get_instance_data(instance.id, 'nic_outgoing', nic, statistic, period, time_to, time_from))
                    nic_name.append(nic)

        return {
                "instance": instance,
                'cpu_data': cpu_data,
                'mem_max_data': mem_max_data,
                'mem_free_data': mem_free_data,
                'blk_read': blk_read,
                'blk_write': blk_write,
                'blk_name': blk_name,
                'nic_outgoing': nic_outgoing,
                'nic_incoming': nic_incoming,
                'nic_name': nic_name
                }


class VNCTab(tabs.Tab):
    name = _("VNC")
    slug = "vnc"
    template_name = "nova/instances_and_volumes/instances/_detail_vnc.html"
    preload = False

    def get_context_data(self, request):
        instance = self.tab_group.kwargs['instance']
        try:
            console = api.nova.server_vnc_console(request, instance.id)
            vnc_url = "%s&title=%s(%s)" % (console.url,
                                           getattr(instance, "name", ""),
                                           instance.id)
        except:
            vnc_url = None
            exceptions.handle(request,
                              _('Unable to get VNC console for '
                                'instance "%s".') % instance.id)
        return {'vnc_url': vnc_url, 'instance_id': instance.id}


class InstanceDetailTabs(tabs.TabGroup):
    slug = "instance_details"
    tabs = (OverviewTab, LogTab, VNCTab, MonitoringTab)
