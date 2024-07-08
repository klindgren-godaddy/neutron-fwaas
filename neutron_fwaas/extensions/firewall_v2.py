# Copyright (c) 2016 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import abc
import netaddr

from neutron.api.v2 import resource_helper
from neutron_lib import exceptions as n_exc
from neutron_lib.api.definitions import constants as api_const
from neutron_lib.api import converters as api_conv
from neutron_lib.api.definitions import firewall_v2
from neutron_lib.api.validators import add_validator
from neutron_lib.api import extensions
from neutron_lib.services import base as service_base
from oslo_config import cfg

from neutron_fwaas._i18n import _
from neutron_fwaas.common import fwaas_constants


default_fwg_rules_opts = [
    cfg.StrOpt('ingress_action',
               default=api_const.FWAAS_DENY,
               help=_('Firewall group rule action allow or '
                      'deny or reject for ingress. '
                      'Default is deny.')),
    cfg.StrOpt('ingress_source_ipv4_address',
               default=None,
               help=_('IPv4 source address for ingress '
                      '(address or address/netmask). '
                      'Default is None.')),
    cfg.StrOpt('ingress_source_ipv6_address',
               default=None,
               help=_('IPv6 source address for ingress '
                      '(address or address/netmask). '
                      'Default is None.')),
    cfg.StrOpt('ingress_source_port',
               default=None,
               help=_('Source port number or range '
                      '(min:max) for ingress. '
                      'Default is None.')),
    cfg.StrOpt('ingress_destination_ipv4_address',
               default=None,
               help=_('IPv4 destination address for ingress '
                      '(address or address/netmask). '
                      'Default is None.')),
    cfg.StrOpt('ingress_destination_ipv6_address',
               default=None,
               help=_('IPv6 destination address for ingress '
                      '(address or address/netmask). '
                      'Default is deny.')),
    cfg.StrOpt('ingress_destination_port',
               default=None,
               help=_('Destination port number or range '
                      '(min:max) for ingress. '
                      'Default is None.')),
    cfg.StrOpt('egress_action',
               default=api_const.FWAAS_ALLOW,
               help=_('Firewall group rule action allow or '
                      'deny or reject for egress. '
                      'Default is allow.')),
    cfg.StrOpt('egress_source_ipv4_address',
               default=None,
               help=_('IPv4 source address for egress '
                      '(address or address/netmask). '
                      'Default is None.')),
    cfg.StrOpt('egress_source_ipv6_address',
               default=None,
               help=_('IPv6 source address for egress '
                      '(address or address/netmask). '
                      'Default is deny.')),
    cfg.StrOpt('egress_source_port',
               default=None,
               help=_('Source port number or range '
                      '(min:max) for egress. '
                      'Default is None.')),
    cfg.StrOpt('egress_destination_ipv4_address',
               default=None,
               help=_('IPv4 destination address for egress '
                      '(address or address/netmask). '
                      'Default is deny.')),
    cfg.StrOpt('egress_destination_ipv6_address',
               default=None,
               help=_('IPv6 destination address for egress '
                      '(address or address/netmask). '
                      'Default is deny.')),
    cfg.StrOpt('egress_destination_port',
               default=None,
               help=_('Destination port number or range '
                      '(min:max) for egress. '
                      'Default is None.')),
    cfg.BoolOpt('shared',
                default=False,
                help=_('Firewall group rule shared. '
                       'Default is False.')),
    cfg.StrOpt('protocol',
               default=None,
               help=_('Network protocols (tcp, udp, ...). '
                      'Default is None.')),
    cfg.BoolOpt('enabled',
                default=True,
                help=_('Firewall group rule enabled. '
                       'Default is True.')),
]
firewall_quota_opts = [
    cfg.IntOpt('quota_firewall_group',
               default=10,
               help=_('Number of firewall groups allowed per tenant. '
                      'A negative value means unlimited.')),
    cfg.IntOpt('quota_firewall_policy',
               default=10,
               help=_('Number of firewall policies allowed per tenant. '
                      'A negative value means unlimited.')),
    cfg.IntOpt('quota_firewall_rule',
               default=100,
               help=_('Number of firewall rules allowed per tenant. '
                      'A negative value means unlimited.')),
]
cfg.CONF.register_opts(default_fwg_rules_opts, 'default_fwg_rules')
cfg.CONF.register_opts(firewall_quota_opts, 'QUOTAS')

# TODO(KGL): this should go into neutron_lib
# add our new address group endpoints here:
firewall_address_groups = {
    'id': {
        'allow_post': False,
        'allow_put': False,
        'is_visible': True},
    'name': {
        'allow_post': True,
        'allow_put': True,
        'validate': {'type:string': None},
        'is_visible': True,
        'default': ''},
    'description': {
        'allow_post': True,
        'allow_put': True,
        'validate': {'type:string': None},
        'is_visible': True,
        'default': ''},
    'project_id': {
        'allow_post': True, 'allow_put': False,
        'required_by_policy': True,
        'validate': {'type:uuid': None},
        'is_visible': True},
    'addresses': {
        'allow_post': True,
        'allow_put': True,
        'convert_to': api_conv.convert_none_to_empty_list,
        'default': api_const.constants.ATTR_NOT_SPECIFIED,
        'validate': {"type:address_group_list": None},
        'is_visible': True},
    api_const.constants.SHARED: {'allow_post': False,
                                 'allow_put': False,
                                 'default': False,
                                 'convert_to': api_conv.convert_to_boolean,
                                 'is_visible': False,
                                 'is_filter': False,
                                 'is_sort_key': False},
    }
firewall_v2.RESOURCE_ATTRIBUTE_MAP['firewall_address_groups'] = firewall_address_groups

# Add address groups to the firewall Rules parameters
firewall_v2.RESOURCE_ATTRIBUTE_MAP['firewall_rules']['source_address_group_ids'] = {
    'allow_post': True,
    'allow_put': True,
    'convert_to': api_conv.convert_none_to_empty_list,
    'default': None,
    'validate': {'type:uuid_list': None},
    'is_visible': True,
    'is_filter': False,
    'is_sort_key': False
}
firewall_v2.RESOURCE_ATTRIBUTE_MAP['firewall_rules']['destination_address_group_ids'] = {
    'allow_post': True, 'allow_put': True,
    'convert_to': api_conv.convert_none_to_empty_list,
    'default': None,
    'validate': {'type:uuid_list': None},
    'is_visible': True,
    'is_filter': False,
    'is_sort_key': False
}


def validate_address_group_address(data, valid_values=None):
    try:
        for address in data:
            msg = _("Invalid address group format")
            if 'address' not in address:
                msg = _("'address' must be specified in address group")
                raise n_exc.InvalidInput(msg)
            if 'ip_version' not in address:
                msg = _("'ip_version' must be specified for address %s" % address['address'])
                raise n_exc.InvalidInput(msg)
            if address['ip_version'] not in (4, 6):
                msg = _("'ip_version' %s, must be 4 or 6" % address['ip_version'])
                raise n_exc.InvalidInput(msg)
            msg = _("'address' %s in not a valid cidr" % address['address'])
            net = netaddr.IPNetwork(address['address'])
            if '/' not in address['address'] or (net.network != net.ip):
                raise n_exc.InvalidInput
    except Exception:
        return msg


class Firewall_v2(extensions.APIExtensionDescriptor):
    api_definition = firewall_v2
    add_validator('type:address_group_list', validate_address_group_address)

    @classmethod
    def get_resources(cls):
        special_mappings = {'firewall_policies': 'firewall_policy'}
        plural_mappings = resource_helper.build_plural_mappings(
            special_mappings, firewall_v2.RESOURCE_ATTRIBUTE_MAP)
        return resource_helper.build_resource_info(
            plural_mappings, firewall_v2.RESOURCE_ATTRIBUTE_MAP,
            fwaas_constants.FIREWALL_V2, action_map=firewall_v2.ACTION_MAP,
            register_quota=True)

    @classmethod
    def get_plugin_interface(cls):
        return Firewallv2PluginBase


class Firewallv2PluginBase(service_base.ServicePluginBase,
                           metaclass=abc.ABCMeta):

    def get_plugin_type(self):
        return fwaas_constants.FIREWALL_V2

    def get_plugin_description(self):
        return 'Firewall Service v2 Plugin'

    # Firewall Address Group
    @abc.abstractmethod
    def create_firewall_address_group(self, context, firewall_address_group):
        pass

    @abc.abstractmethod
    def delete_firewall_address_group(self, context, id):
        pass

    @abc.abstractmethod
    def get_firewall_address_group(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def get_firewall_address_groups(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def update_firewall_address_group(self, context, id, firewall_address_group):
        pass

    # Firewall Group
    @abc.abstractmethod
    def create_firewall_group(self, context, firewall_group):
        pass

    @abc.abstractmethod
    def delete_firewall_group(self, context, id):
        pass

    @abc.abstractmethod
    def get_firewall_group(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def get_firewall_groups(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def update_firewall_group(self, context, id, firewall_group):
        pass

    # Firewall Policy
    @abc.abstractmethod
    def create_firewall_policy(self, context, firewall_policy):
        pass

    @abc.abstractmethod
    def delete_firewall_policy(self, context, id):
        pass

    @abc.abstractmethod
    def get_firewall_policy(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def get_firewall_policies(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def update_firewall_policy(self, context, id, firewall_policy):
        pass

    # Firewall Rule
    @abc.abstractmethod
    def create_firewall_rule(self, context, firewall_rule):
        pass

    @abc.abstractmethod
    def delete_firewall_rule(self, context, id):
        pass

    @abc.abstractmethod
    def get_firewall_rule(self, context, id, fields=None):
        pass

    @abc.abstractmethod
    def get_firewall_rules(self, context, filters=None, fields=None):
        pass

    @abc.abstractmethod
    def update_firewall_rule(self, context, id, firewall_rule):
        pass

    @abc.abstractmethod
    def insert_rule(self, context, id, rule_info):
        pass

    @abc.abstractmethod
    def remove_rule(self, context, id, rule_info):
        pass
