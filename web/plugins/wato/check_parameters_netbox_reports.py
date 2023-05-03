#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Netbox Reports Last Run
#
# Copyright (C) 2023  Marius Rieder <marius.rieder@scs.ch>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.

from cmk.gui.i18n import _
from cmk.gui.valuespec import (
    Age,
    Dictionary,
    TextAscii,
    Tuple,
)

from cmk.gui.plugins.wato import (
    CheckParameterRulespecWithItem,
    rulespec_registry,
    RulespecGroupCheckParametersApplications,
)

def _item_spec_netbox_reports():
    return TextAscii(title=_('Name of the Netbox Report'),
                     allow_empty=False)


def _parameter_valuespec_netbox_reports():
    return Dictionary(
        elements=[
            (
                'maxage',
                Tuple(
                    title=_('Maximal time since last run'),
                    elements=[
                        Age(title=_('Warning if older than')),
                        Age(title=_('Critical if older than')),
                    ],
                )
            ),
        ],
    )


rulespec_registry.register(
    CheckParameterRulespecWithItem(
        check_group_name='netbox_reports',
        group=RulespecGroupCheckParametersApplications,
        item_spec=_item_spec_netbox_reports,
        match_type='dict',
        parameter_valuespec=_parameter_valuespec_netbox_reports,
        title=lambda: _('Netbox Reports'),
    ))