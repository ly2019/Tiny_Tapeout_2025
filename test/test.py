# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

#only testing output == 3 counters on... produced by chatgpt 5, because I am lazy.

import random
import cocotb
from cocotb.triggers import Timer

def get_handle(dut, path):
    """Fetch a hierarchical handle; raise a clear message if not found."""
    try:
        return dut._id(path, extended=True)
    except Exception as e:
        raise RuntimeError(f"Could not find '{path}'. "
                           f"Update the path to match your instance names. Original: {e}")

def try_timer_paths(dut):
    """
    Try common hierarchy patterns to find timer regs inside process_signal.
    Update/add candidates to match your RTL if needed.
    """
    candidates = [
        # wrapper instance name in tb.v is often 'user_project'
        # CASE 1: wrapper -> top 'core' -> process 'sensor_logic'
        ("user_project.core.sensor_logic.timer1",
         "user_project.core.sensor_logic.timer2",
         "user_project.core.sensor_logic.timer3"),
        # CASE 2: wrapper directly instantiates 'sensor_logic'
        ("user_project.sensor_logic.timer1",
         "user_project.sensor_logic.timer2",
         "user_project.sensor_logic.timer3"),
    ]
    last_err = None
    for p1, p2, p3 in candidates:
        try:
            t1 = get_handle(dut, p1)
            t2 = get_handle(dut, p2)
            t3 = get_handle(dut, p3)
            return t1, t2, t3
        except RuntimeError as e:
            last_err = e
    # If we got here, none matched
    raise last_err or RuntimeError("Timers not found; adjust hierarchy paths.")

@cocotb.test()
async def test_response_is_and_of_timers_gt_zero(dut):
    """
    Check: response == 1  iff (timer1>0 & timer2>0 & timer3>0)
           response == 0  otherwise.
    We do this by directly writing timer registers (no sensors, no clock).
    """

    dut._log.info("Init (no clock needed for this combinational check)")
    # No clock: we won't start dut.clk, so no posedges will overwrite timers.
    # Put harness lines in a safe state.
    dut.ena.value    = 1
    dut.ui_in.value  = 0
    dut.uio_in.value = 0
    dut.rst_n.value  = 1  # keep reset deasserted to avoid posedge reset

    # Locate internal timers
    t1, t2, t3 = try_timer_paths(dut)

    # Convenience: response bit (uo_out[0])
    def response():
        return (dut.uo_out.value.integer & 1)

    # Helper to drive timers and check expected output
    async def drive_and_check(v1, v2, v3):
        t1.value = int(v1)
        t2.value = int(v2)
        t3.value = int(v3)
        # Let combinational logic settle
        await Timer(1, units="ns")
        expected = 1 if (int(v1) > 0 and int(v2) > 0 and int(v3) > 0) else 0
        got = response()
        assert got == expected, (
            f"response mismatch for timers (t1={int(v1)}, t2={int(v2)}, t3={int(v3)}): "
            f"got {got}, expected {expected}"
        )

    # Deterministic edge cases
    await drive_and_check(0, 0, 0)
    await drive_and_check(1, 0, 0)
    await drive_and_check(0, 1, 0)
    await drive_and_check(0, 0, 1)
    await drive_and_check(1, 1, 0)
    await drive_and_check(1, 0, 1)
    await drive_and_check(0, 1, 1)
    await drive_and_check(1, 1, 1)
    await drive_and_check(60000, 60000, 60000)
    await drive_and_check(60000, 60000, 0)

    # A few random trials (including zeros and positive values)
    rng = random.Random(1234)
    for _ in range(20):
        v1 = rng.choice([0, rng.randrange(1, 70000)])
        v2 = rng.choice([0, rng.randrange(1, 70000)])
        v3 = rng.choice([0, rng.randrange(1, 70000)])
        await drive_and_check(v1, v2, v3)

    dut._log.info("PASS: response == (timer1>0 && timer2>0 && timer3>0)")
