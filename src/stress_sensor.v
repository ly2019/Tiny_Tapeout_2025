`default_nettype none
`timescale 1ns/1ns

// Inner module: process_signal
module process_signal (
    input wire clk,         // 1 kHz clock
    input wire reset,
    input wire signal1,
    input wire signal2,
    input wire signal3,
    output reg out
);

reg [15:0] timer1 = 0;
reg [15:0] timer2 = 0;
reg [15:0] timer3 = 0;

always @(posedge clk or posedge reset) begin
    if (reset) begin
        timer1 <= 0;
        timer2 <= 0;
        timer3 <= 0;
    end else begin
        if (signal1)
            timer1 <= 16'd60000;
        else if (timer1 > 0)
            timer1 <= timer1 - 1;

        if (signal2)
            timer2 <= 16'd60000;
        else if (timer2 > 0)
            timer2 <= timer2 - 1;

        if (signal3)
            timer3 <= 16'd60000;
        else if (timer3 > 0)
            timer3 <= timer3 - 1;
    end
end

always @(*) begin
    out = (timer1 > 0) && (timer2 > 0) && (timer3 > 0);
end
endmodule

//A clock divider
`default_nettype none
`timescale 1ns/1ns
module clock_divider_1khz (
    input wire clk_in,     // 100 MHz input clock
    input wire reset,
    output reg clk_out     // 1 kHz output clock
);

reg [16:0] counter = 0;    // 17 bits is enough for counting to 100,000

parameter DIVISOR = 100_000;  // 100 MHz → 1 kHz

always @(posedge clk_in or posedge reset) begin
    if (reset) begin
        counter <= 0;
        clk_out <= 0;
    end else begin
        if (counter == (DIVISOR / 2 - 1)) begin
            clk_out <= ~clk_out;   // Toggle clock output
            counter <= 0;
        end else begin
            counter <= counter + 1;
        end
    end
end

endmodule

// Top-Level Module That Connects Sensors and clock divider
`default_nettype none
`timescale 1ns/1ns
module stress_sensor(
    input wire clk,          // 1 kHz clock
    input wire reset,
    input wire sensor1,
    input wire sensor2,
    input wire sensor3,
    output wire response
);

wire signal_out;

// Internal 1 kHz clock wire
wire clk_1khz;

// Instantiate clock divider
clock_divider_1khz clkdiv (
    .clk_in(clk),
    .reset(reset),
    .clk_out(clk_1khz)
);

process_signal sensor_logic (
    .clk(clk_1khz),
    .reset(reset),
    .signal1(sensor1),
    .signal2(sensor2),
    .signal3(sensor3),
    .out(signal_out)
);

assign response = signal_out;

endmodule
