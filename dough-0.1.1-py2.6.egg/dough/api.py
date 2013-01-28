#!/usr/bin/env python
# -*- coding: utf8 -*-

from dateutil.relativedelta import relativedelta
from dateutil import tz
import iso8601

from nova import flags
#from nova import utils
from nova.openstack.common import cfg

from dough import db
from dough import exception


api_opts = [
    cfg.StrOpt('api_listen',
               default='localhost',
               help='IP address for dough API to listen.'),
    cfg.IntOpt('api_listen_port',
               default=5557,
               help='Port for dough api to listen.'),
    ]

FLAGS = flags.FLAGS
FLAGS.register_opts(api_opts)

UTC_TIMEZONE = tz.gettz('UTC')


def _product_get_all(context, region=None, item=None, item_type=None,
                     payment_type=None):
    """
    """
    products = None
    try:
        # filter to get product_id
        filters = dict()
        filters['region_id'] = db.region_get_by_name(context, region)['id']
        filters['item_id'] = db.item_get_by_name(context, item)['id']
        filters['item_type_id'] = db.item_type_get_by_name(context,
                                                           item_type)['id']
        filters['payment_type_id'] = db.payment_type_get_by_name(context,
                                                            payment_type)['id']
        products = db.product_get_all(context, filters=filters)
    except Exception, e:
        # TODO(lzyeval): report
        print e
        raise
    return products


def subscribe_item(context, region=None, item=None, item_type=None,
                   payment_type=None, resource_uuid=None, resource_name=None,
                   **kwargs):
    """
    """
    # values of product
    values = {
        'project_id': context.project_id,
        'resource_uuid': resource_uuid,
        'resource_name': resource_name,
        }
    try:
        # filter to get product_id
        products = _product_get_all(context, region=region, item=item,
                                    item_type=item_type,
                                    payment_type=payment_type)
        # TODO(lzyeval): check if products size is not 1
        values['product_id'] = products[0]['id']
        values['status'] = "verified"
        print "subscription_create", item, payment_type, values
        app = context.app
        app.info("subscribe_item:proj_id=" + str(context.project_id) + \
                " name:" + str(resource_name) + \
                "/" + str(item) + \
                "/" + str(payment_type) + \
                "/" + str(resource_uuid))
        subscription_ref = db.subscription_create(context, values)
        db.subscription_extend(context,
                               subscription_ref['id'],
                               subscription_ref['created_at'])
        print "item subscribed."
    except Exception, e:
        # TODO(lzyeval): report
        print "subscribe failed:", Exception, e
        raise
    return dict()


def unsubscribe_item(context, region=None, item=None,
                     resource_uuid=None, **kwargs):
    """
    """
    try:
        app = context.app
        app.info("unsubscribe_item:" + str(region) + "/" + str(item) + "/" + str(resource_uuid))
        subscription_id = 0
        subscriptions = db.subscription_get_all_by_resource_uuid(context,
                                                                 resource_uuid)
        if not subscriptions:
            print "unsubscribe_item.SubscriptionNotFoundByResourceUUID", resource_uuid
            raise exception.SubscriptionNotFoundByResourceUUID(
                    resource_uuid=resource_uuid)
        for subscription in subscriptions:
            product = subscription['product']
            if product['region']['name'] != region:
                continue
            elif product['item']['name'] != item:
                continue
            # TODO: status==verified
            print subscription['status']
            if "floating_ip" == product['item']['name'] and "verified" != subscription['status']:
                continue
            subscription_id = subscription['id']
            break
        if not subscription_id:
            print "subscription_get_by_resource_uuid", resource_uuid, "item=", item, "region=", region
            raise exception.SubscriptionNotFoundByRegionOrItem(region=region,
                                                               item=item)
        app.info("\tsubs_id=" + str(subscription_id))
        db.subscription_destroy(context, subscription_id)
    except Exception, e:
        # TODO(lzyeval): report
        print e
        raise
    return dict()


def query_item_products(context, region=None, item=None, **kwargs):
    product_info = dict()

#geyg_20130121_Add the display of products in horizon in lenovo
    product_info_list = list()

#    filters = dict()
#    filters['region_id'] = db.region_get_by_name(context, region)['id']
#    filters['item_id'] = db.item_get_by_name(context, item)['id']
#    products = db.product_get_all(context, filters=filters)
    products = db.product_get_all(context)
    for product in products:
        item_name = product['item']['name']
        item_type_name = product['item_type']['name']
#        payment_type_name = product['payment_type']['name']
        order_unit = product['order_unit']
        order_size = product['order_size']
        price = product['price']
        currency = product['currency']
#geyg_20130121_Add the display of products in horizon in lenovo

#        item_type_info = product_info.setdefault(item_type_name, dict())
#        item_type_info[payment_type_name] = {
#            'order_unit': order_unit,
#            'order_size': order_size,
#            'price': price,
#            'currency': currency,
#            }

        product_info = dict()
        product_info.setdefault('item_name',0)
        product_info['item_name'] = item_name 
        product_info.setdefault('item_type_name',0)
        product_info['item_type_name'] = item_type_name 
        product_info.setdefault('order_size',0)
        product_info['order_size'] = order_size 
        product_info.setdefault('order_unit',0)
        product_info['order_unit'] = order_unit 
        product_info.setdefault('price',0)
        product_info['price'] = price 
        product_info.setdefault('currency',0)
        product_info['currency'] = currency 
        product_info_list.append(product_info)

#    return {'data': product_info}
    return {'data': product_info_list}


def query_usage_report(context, timestamp_from=None,
                       timestamp_to=None, **kwargs):
    usage_report = dict()
    datetime_from = iso8601.parse_date(timestamp_from)
    datetime_to = iso8601.parse_date(timestamp_to)
    subscriptions = list()
    _subscriptions = db.subscription_get_all_by_project(context,
                                                        context.project_id)
    for subscription in _subscriptions:
        if subscription is None \
           or subscription['product'] is None \
           or subscription['product']['region'] is None \
           or subscription['product']['region']['name'] is None:
            continue
        subscription_id = subscription['id']
        resource_uuid = subscription['resource_uuid']
        resource_name = subscription['resource_name']
        created_at = subscription['created_at']
        expires_at = subscription['expires_at']
        region_name = subscription['product']['region']['name']
        item_name = subscription['product']['item']['name']
        item_type_name = subscription['product']['item_type']['name']
        order_unit = subscription['product']['order_unit']
        order_size = subscription['product']['order_size']
        price = subscription['product']['price']
        currency = subscription['product']['currency']
        subscriptions.append([subscription_id, resource_uuid, resource_name,
                              created_at, expires_at,
                              region_name, item_name, item_type_name,
                              order_unit, order_size, price, currency])
    for (subscription_id, resource_uuid, resource_name, created_at, expires_at,
         region_name, item_name, item_type_name,
         order_unit, order_size, price, currency) in subscriptions:
        purchases = db.purchase_get_all_by_subscription_and_timeframe(context,
                                                            subscription_id,
                                                            datetime_from,
                                                            datetime_to)
        if not purchases:
            continue
        quantity_sum = sum(map(lambda x: x['quantity'], purchases))
        line_total_sum = sum(map(lambda x: x['line_total'], purchases))
        # TODO(lzyeval): remove
        #assert (line_total_sum == quantity_sum * price)
        usage_datum = (resource_uuid, resource_name, item_type_name,
                       order_unit, order_size, price,
                       currency, quantity_sum, line_total_sum,
                       created_at.isoformat(), expires_at.isoformat())
        region_usage = usage_report.setdefault(region_name, dict())
        item_usage = region_usage.setdefault(item_name, list())
        item_usage.append(usage_datum)
    return {'data': usage_report}


def query_monthly_report(context, timestamp_from=None,
                         timestamp_to=None, **kwargs):

    def find_timeframe(start_time, end_time, target):
        target_utc = target.replace(tzinfo=UTC_TIMEZONE)
        current_frame = start_time
        month_cnt = 1
        while current_frame < end_time:
            # 2012-05-10 00:00:00+00:00-->2012-06-10 00:00:00+00:00
            next_frame = start_time + relativedelta(months=month_cnt)
            if current_frame <= target_utc < next_frame:
                break
            month_cnt += 1
            current_frame = next_frame
        assert(current_frame < end_time)

        return current_frame.isoformat()

    monthly_report = dict()
#geyg_20130114_change the json form for view of webpage
    monthly_report_list = [] 
    datetime_from = iso8601.parse_date(timestamp_from)
    datetime_to = iso8601.parse_date(timestamp_to)
    subscriptions = list()
    _subscriptions = db.subscription_get_all_by_project(context,
                                                        context.project_id)
    for subscription in _subscriptions:
        subscription_id = subscription['id']
        if subscription is None \
           or subscription['product'] is None \
           or subscription['product']['region'] is None \
           or subscription['product']['region']['name'] is None:
            continue
        region_name = subscription['product']['region']['name']
        item_name = subscription['product']['item']['name']
        subscriptions.append([subscription_id, region_name, item_name])
    for subscription_id, region_name, item_name in subscriptions:
        purchases = db.purchase_get_all_by_subscription_and_timeframe(context,
                                                            subscription_id,
                                                            datetime_from,
                                                            datetime_to)
        if not purchases:
            continue
        monthly_report = dict()
        monthly_report.setdefault('regionnm', 0)
        monthly_report['regionnm'] = region_name
        monthly_report.setdefault('timefm', 0)
#        monthly_report['timefm'] = timeframe
        monthly_report.setdefault('itemnm', 0)
        monthly_report['itemnm'] = item_name
        monthly_report.setdefault('linett', 0)
        monthly_report['linett'] = 0 

        for purchase in purchases:
            line_total = purchase['line_total']
            timeframe = find_timeframe(datetime_from,
                                       datetime_to,
                                       purchase['created_at'])
#geyg_20130114_change the json form for view of webpage
#            region_usage = monthly_report.setdefault(region_name, dict())
#            monthly_usage = region_usage.setdefault(timeframe, dict())
#            monthly_usage.setdefault(item_name, 0)
#            monthly_usage[item_name] += line_total
            monthly_report['linett'] += line_total
        
        monthly_report['timefm'] = timeframe
        monthly_report_list.append(monthly_report)
    return {'data': monthly_report_list}


def query_report(context, timestamp_from=None, timestamp_to=None,
                  period=None, item_name=None, resource_name=None, **kwargs):
    """period='days' or 'hours'"""
    print "query_report", timestamp_from, timestamp_to, item_name, resource_name

    if not period in ['days', 'hours', 'months']:
        return {'data': None}

    def find_timeframe(start_time, end_time, target):
        target_utc = target.replace(tzinfo=UTC_TIMEZONE)
        current_frame = start_time
        cnt = 1
        while current_frame < end_time:
            foo = {period: cnt}
            next_frame = start_time + relativedelta(**foo)
            if current_frame <= target_utc < next_frame:
                break
            cnt += 1
            current_frame = next_frame
        assert(current_frame < end_time)
        return current_frame.isoformat()

    monthly_report = dict()
    datetime_from = iso8601.parse_date(timestamp_from)
    datetime_to = iso8601.parse_date(timestamp_to)
    subscriptions = list()
    _subscriptions = list()

    __subscriptions = db.subscription_get_all_by_project(context,
                                                        context.project_id)
    if not __subscriptions:
        return {'data': None}
    for subscription in __subscriptions:
        if subscription['resource_name'] != resource_name:
            continue
        elif subscription['product']['item']['name'] != item_name:
            continue
        _subscriptions.append(subscription)

    for subscription in _subscriptions:
        subscription_id = subscription['id']
        resource_uuid = subscription['resource_uuid']
        resource_name = subscription['resource_name']
        created_at = subscription['created_at']
        expires_at = subscription['expires_at']
        region_name = subscription['product']['region']['name']
        item_name = subscription['product']['item']['name']
        item_type_name = subscription['product']['item_type']['name']
        order_unit = subscription['product']['order_unit']
        order_size = subscription['product']['order_size']
        price = subscription['product']['price']
        currency = subscription['product']['currency']
        subscriptions.append([subscription_id, resource_uuid, resource_name,
                              created_at, expires_at,
                              region_name, item_name, item_type_name,
                              order_unit, order_size, price, currency])
    for (subscription_id, resource_uuid, resource_name, created_at, expires_at,
         region_name, item_name, item_type_name,
         order_unit, order_size, price, currency) in subscriptions:
        purchases = db.purchase_get_all_by_subscription_and_timeframe(context,
                                                            subscription_id,
                                                            datetime_from,
                                                            datetime_to)
        if not purchases:
            continue
        i = 0
        for purchase in purchases:
            line_total = purchase['line_total']
            quantity = purchase['quantity']
            timeframe = find_timeframe(datetime_from,
                                       datetime_to,
                                       purchase['created_at'])
#            print timeframe
            i += 1
            usage_datum = (resource_uuid, resource_name, item_type_name,
                           order_unit, order_size, price,
                           currency, quantity, line_total,
                           created_at.isoformat(), expires_at.isoformat())
            region_usage = monthly_report.setdefault(region_name, dict())
            monthly_usage = region_usage.setdefault(timeframe, dict())
            monthly_usage.setdefault(item_name, 0)
            monthly_usage[item_name] = usage_datum
            monthly_usage.setdefault("quantity", 0)
            monthly_usage.setdefault("line_total", 0)
            monthly_usage["quantity"] += quantity
            monthly_usage["line_total"] += line_total
        print "total:", i
    return {'data': monthly_report}
