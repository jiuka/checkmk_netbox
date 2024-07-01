#!/usr/bin/python
# -*- encoding: utf-8; py-indent-offset: 4 -*-License
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

from cmk.graphing.v1 import graphs, metrics, perfometers

metric_test_info = metrics.Metric(
    name='test_info',
    title=metrics.Title('Info'),
    unit=metrics.Unit(metrics.DecimalNotation("")),
    color=metrics.Color.LIGHT_BLUE,
)

metric_test_success = metrics.Metric(
    name='test_success',
    title=metrics.Title('Success'),
    unit=metrics.Unit(metrics.DecimalNotation("")),
    color=metrics.Color.GREEN,
)

metric_test_warning = metrics.Metric(
    name='test_warning',
    title=metrics.Title('Warning'),
    unit=metrics.Unit(metrics.DecimalNotation("")),
    color=metrics.Color.YELLOW,
)

metric_test_failure = metrics.Metric(
    name='test_failure',
    title=metrics.Title('Failure'),
    unit=metrics.Unit(metrics.DecimalNotation("")),
    color=metrics.Color.RED,
)

graph_netbox_script = graphs.Graph(
    name='netbox_script',
    title=graphs.Title('netbox Script'),
    minimal_range=graphs.MinimalRange(0, 1),
    compound_lines=[
        'test_info',
        'test_success',
        'test_warning',
        'test_failure',
    ],
)

perfometer_netbox_script = perfometers.Perfometer(
    name='netbox_script',
    focus_range=perfometers.FocusRange(perfometers.Closed(0), perfometers.Open(1)),
    segments=[
        'test_info',
        'test_success',
        'test_warning',
        'test_failure',
    ],
)
