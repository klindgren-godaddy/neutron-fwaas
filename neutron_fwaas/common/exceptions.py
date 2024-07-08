# Copyright 2018 Fujitsu Limited.
# All Rights Reserved.
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

from neutron_lib import exceptions as n_exc

from neutron_fwaas._i18n import _


# TODO(annp): migrate to neutron-lib after Queen release
class FirewallGroupPortNotSupported(n_exc.Conflict):
    message = _("Port %(port_id)s is not supported by firewall driver "
                "'%(driver_name)s'.")


# TODO(KGL): This should get moved to neutron-lib
class FirewallAddressGroupNotFound(n_exc.NotFound):
    msg = _("Firewall Address Group %(firewall_address_group_id)s could not be "
            "found.")


class FirewallAddressGroupInvalidAddress(n_exc.InvalidInput):
    msg = _("Invalid address '%(ip_address)s' for address group, "
            "needs to be a cidr.")


class FirewallAddressGroupInvalidIpVersion(n_exc.InvalidInput):
    msg = _("Invalid ip_version '%(ip_version)s' for address group, "
            "needs to be either 4 or 6.")


class FirewallAddressGroupInUse(n_exc.InUse):
    msg = _("Address group '%(address_group_id)s' is in use by "
            "firewall rule(s).")


class FirewallAddressGroupIpVersionConflict(n_exc.InvalidInput):
    message = _("Address group ip '%(ip_address)s' has conflicting "
                "ip_version '%(ip_version)s' set.")


class FirewallAddressGroupProjectConflict(n_exc.Conflict):
    message = _("Address group '%(ag_id)s' is in a different "
                "project than the firewall rule(s) using it.")


class FirewallRuleWithAddressGroupConflict(n_exc.Conflict):
    message = _("Firewall rule contains both an address group and "
                "an IP address on the same direction.  Use one or "
                "the other.")