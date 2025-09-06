# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0
# Minimal cocotb testbench: only check that 3 sensors ON -> output=1 . produced by chatgpt 5, because I am lazy.

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer


@cocotb.test()
async def three_sensors_on_means_output_on(dut):
    """Check that when all 3 sensors are high, the output bit is 1."""

    # Start a 100 MHz clock (10 ns period)
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())

    # Reset
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)

    # Drive all three sensors ON: ui_in[2:0] = 111
    dut.ui_in.value = (dut.ui_in.value.integer & ~0b111) | 0b111

    # Wait >1 ms (at 100 MHz that’s ~100,000 cycles) so the 1 kHz divider ticks
    await Timer(1_200_000, units="ns")

    # Check that output bit 0 is 1
    assert (dut.uo_out.value.integer & 1) == 1, \
        "Expected uo_out[0] == 1 when all three sensors are ON"
