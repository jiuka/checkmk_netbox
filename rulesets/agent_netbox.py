#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-
#
# Copyright (C) 2023-2024  Marius Rieder <marius.rieder@scs.ch>
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

from cmk.rulesets.v1 import Title, Help
from cmk.rulesets.v1.form_specs import (
    DefaultValue,
    DictElement,
    Dictionary,
    InputHint,
    migrate_to_password,
    Password,
    SingleChoice,
    SingleChoiceElement,
    String,
    validators,
)
from cmk.rulesets.v1.rule_specs import SpecialAgent, Topic


def _form_special_agents_netbox() -> Dictionary:
    return Dictionary(
        title=Title("Netbox Server"),
        elements = {
            'url': DictElement(
                parameter_form=String(
                    title=Title('URL of the Netbox Rest API, e.g. https://netbox.example.com/api'),
                    custom_validate=(
                        validators.Url(
                            [validators.UrlProtocol.HTTP, validators.UrlProtocol.HTTPS],
                        ),
                    ),
                    prefill=InputHint('https://netbox.example.com/api')
                ),
                required=True,
            ),
            'token': DictElement(
                parameter_form=Password(
                    title=Title('Netbox Token'),
                    migrate=migrate_to_password
                ),
                required=True,
            ),
            'ignore_cert': DictElement(
                parameter_form=SingleChoice(
                    title=Title('SSL certificate checking'),
                    elements=[
                        SingleChoiceElement(name='ignore_cert', title=Title('Ignore Cert')),
                        SingleChoiceElement(name='check_cert', title=Title('Check Cert')),
                    ],
                    prefill=DefaultValue('check_cert'),
                ),
                required=True,
            ),
        },
    )


rule_spec_netbox_datasource = SpecialAgent(
    name="netbox",
    title=Title('Netbox Server'),
    help_text=Help('This rule selects the Netbox agent'),
    topic=Topic.APPLICATIONS,
    parameter_form=_form_special_agents_netbox,
)
