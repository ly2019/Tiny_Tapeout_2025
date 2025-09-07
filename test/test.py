# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 1 ms (1 kHz)
    clock = Clock(dut.clk, 1, units="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
   # if hasattr(dut, "uio_oe"): dut.uio_oe.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1




    dut._log.info("Test project behavior")

    # Set the input values you want to test 
    dut.ui_in.value = 0b00000101 
    
    # Wait for some clock cycle to see the output values 
    await ClockCycles(dut.clk, 50002) 
    
    
    # output is 0 because not all three signals are 1. 
    dut._log.info(f"uo_out.binstr = {dut.uo_out.value.binstr}")
    assert int(dut.uo_out.value)  == 0
    
    
    
    
    
