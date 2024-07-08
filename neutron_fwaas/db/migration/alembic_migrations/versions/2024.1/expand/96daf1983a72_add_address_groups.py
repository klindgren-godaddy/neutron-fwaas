# Copyright 2024 <PUT YOUR NAME/COMPANY HERE>
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
#

"""Add address groups

Revision ID: 96daf1983a72
Revises: 6941ce70131e
Create Date: 2024-07-03 13:26:14.832437

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '96daf1983a72'
down_revision = '6941ce70131e'
tables = ['firewall_address_groups_v2',
          'firewall_address_group_address_associations_v2',
          'firewall_rule_source_address_group_associations_v2',
          'firewall_rule_destination_address_group_associations_v2']


def upgrade():
    # Create firewall_address_groups_v2 table
    op.create_table(
        'firewall_address_groups_v2',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('project_id', sa.String(length=36), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Column('standard_attr_id', sa.BIGINT, nullable=False),
        sa.UniqueConstraint('standard_attr_id',
                            name='uniq_firewall_address_groups_v20standard_attr_id'),
        sa.ForeignKeyConstraint(['standard_attr_id'],
                                ['standardattributes.id'],
                                name='firewall_address_group_v2_ibfk_1',
                                ondelete='CASCADE'),

    )

    # Create firewall_address_group_address_associations_v2 table
    op.create_table(
        'firewall_address_group_address_associations_v2',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('firewall_address_group_id', sa.String(length=36), nullable=False),
        sa.Column('address', sa.String(length=46), nullable=True),
        sa.Column('ip_version', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['firewall_address_group_id'], ['firewall_address_groups_v2.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create firewall_rule_source_address_group_associations_v2 table
    op.create_table(
        'firewall_rule_source_address_group_associations_v2',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('firewall_rule_id', sa.String(length=36), nullable=False),
        sa.Column('address_group_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['firewall_rule_id'], ['firewall_rules_v2.id']),
        sa.ForeignKeyConstraint(['address_group_id'], ['firewall_address_groups_v2.id']),
        sa.PrimaryKeyConstraint('id')
    )

    # Create firewall_rule_destination_address_group_associations_v2 table
    op.create_table(
        'firewall_rule_destination_address_group_associations_v2',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('firewall_rule_id', sa.String(length=36), nullable=False),
        sa.Column('address_group_id', sa.String(length=36), nullable=False),
        sa.ForeignKeyConstraint(['firewall_rule_id'], ['firewall_rules_v2.id']),
        sa.ForeignKeyConstraint(['address_group_id'], ['firewall_address_groups_v2.id']),
        sa.PrimaryKeyConstraint('id')
    )
