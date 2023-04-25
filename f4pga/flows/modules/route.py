#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 F4PGA Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: Apache-2.0

from pathlib import Path

from f4pga.flows.tools.vpr import vpr_specific_values, vpr, VprArgs, save_vpr_log
from f4pga.flows.module import Module, ModuleContext


def p_route_place_file(ctx: ModuleContext):
    return Path(ctx.takes.eblif).with_suffix(".route")


class RouteModule(Module):
    def map_io(self, ctx: ModuleContext):
        return {"route": str(p_route_place_file(ctx))}

    def execute(self, ctx: ModuleContext):
        build_dir = Path(ctx.takes.eblif).parent

        yield "Routing with VPR..."
        vpr(
            "route",
            VprArgs(
                share=ctx.share,
                eblif=ctx.takes.eblif,
                arch_def=ctx.values.arch_def,
                lookahead=ctx.values.rr_graph_lookahead_bin,
                rr_graph=ctx.values.rr_graph_real_bin,
                place_delay=ctx.values.vpr_place_delay,
                device_name=ctx.values.vpr_grid_layout_name,
                vpr_options=ctx.values.vpr_options if ctx.values.vpr_options else {},
                sdc_file=ctx.takes.sdc,
            ),
            cwd=build_dir,
        )

        if ctx.is_output_explicit("route"):
            p_route_place_file(ctx).rename(ctx.outputs.route)

        yield "Saving log..."
        save_vpr_log("route.log", build_dir=build_dir)

    def __init__(self, _):
        self.name = "route"
        self.no_of_phases = 2
        self.takes = ["eblif", "place", "sdc?"]
        self.produces = ["route"]
        self.values = ["device", "vpr_options?"] + vpr_specific_values


ModuleClass = RouteModule
