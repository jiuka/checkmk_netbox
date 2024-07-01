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

from cmk.rulesets.v1 import Help, Title
from cmk.rulesets.v1.form_specs import (
    DictElement,
    Dictionary,
    InputHint,
    LevelDirection,
    migrate_to_float_simple_levels,
    SimpleLevels,
    TimeMagnitude,
    TimeSpan,
)
from cmk.rulesets.v1.rule_specs import CheckParameters, Topic, HostAndItemCondition


def _parameter_form_netbox_script():
    return Dictionary(
        elements={
            'maxage': DictElement(
                parameter_form=SimpleLevels(
                    title=Title('Maximal time since last run'),
                    help_text=Help('Thresholds for duration sinc the last script execution.'),
                    level_direction=LevelDirection.UPPER,
                    form_spec_template=TimeSpan(
                        displayed_magnitudes=[TimeMagnitude.DAY, TimeMagnitude.HOUR, TimeMagnitude.MINUTE]
                    ),
                    migrate=migrate_to_float_simple_levels,
                    prefill_fixed_levels=InputHint(value=(1800, 3600)),
                ),
                required=False,
            ),
        }
    )


rule_spec_netbox_script = CheckParameters(
    name='netbox_script',
    topic=Topic.APPLICATIONS,
    parameter_form=_parameter_form_netbox_script,
    title=Title('Netbox Scripts'),
    help_text=Help('This rule configures thresholds Netbox Scripts.'),
    condition=HostAndItemCondition(item_title=Title('Netbox Scripts Name')),
)
