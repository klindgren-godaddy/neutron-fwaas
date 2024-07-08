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

import itertools

from neutron_fwaas.policies import firewall_address_group
from neutron_fwaas.policies import firewall_group
from neutron_fwaas.policies import firewall_policy
from neutron_fwaas.policies import firewall_rule


def list_rules():
    return itertools.chain(
        firewall_address_group.list_rules(),
        firewall_group.list_rules(),
        firewall_policy.list_rules(),
        firewall_rule.list_rules(),
    )
