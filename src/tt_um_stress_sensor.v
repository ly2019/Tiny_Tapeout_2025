/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_stress_sensor (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

    // Create a new reset; inverting.
    wire reset = ~rst_n;
    
    // Map first 3 bits of ui_in to the inputs, and the output to the first output bit.
    wire sensor1 = ui_in[0];
    wire sensor2 = ui_in[1];
    wire sensor3 = ui_in[2];
    wire response = uo_out[0];
    
    // Instantiate the original top module stress_sensor
    stress_sensor to_tt (
        .clk(clk),
        .reset(reset),
        .sensor1(sensor1),
        .sensor2(sensor2),
        .sensor3(sensor3),
        .response(response)
    );
    
    // Tie off the unused outputs
    assign uo_out[7:1] = 7'b0;   // other output pins unused
    assign uio_out     = 8'b0;   // don't drive bidirectional pins
    assign uio_oe      = 8'b0;   // keep bidirectional pins as inputs (disabled)

    // Silence unused input warnings
    wire _unused = &{uio_in, ena, ui_in[7:3], 1'b0};

endmodule
