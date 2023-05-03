#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
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
from cmk.gui.plugins.wato import (
    HostRulespec,
    IndividualOrStoredPassword,
    rulespec_registry,
)
from cmk.gui.valuespec import (
    Dictionary,
    HTTPUrl,
)
from cmk.gui.plugins.wato.datasource_programs import RulespecGroupDatasourceProgramsApps


def _valuespec_special_agents_netbox():
    return Dictionary(
        title=_("Netbox Server"),
        help = _("This rule selects the Netbox agent"),
        elements = [
            (
                'url',
                HTTPUrl(
                    title = _("URL of the Netbox Rest API, e.g. https://netbox.example.com/api"),
                    allow_empty = False,
                )
            ),
            (
                'token',
                IndividualOrStoredPassword(
                    title = _("Netbox Token"),
                    allow_empty = True,
                )
            ),
        ],
        optional_keys = ['token'],
    )


rulespec_registry.register(
    HostRulespec(
        group=RulespecGroupDatasourceProgramsApps,
        name='special_agents:netbox',
        valuespec=_valuespec_special_agents_netbox,
    ))