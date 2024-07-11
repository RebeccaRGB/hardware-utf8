/*
 * Copyright (c) 2024 Rebecca G. Bettencourt
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_rebeccargb_hardware_utf8 (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // multiplexing signals
  wire read = ui_in[0]; // HIGH to read, LOW to write
  wire errs = ui_in[1]; // HIGH for errors, LOW for character properties

  assign uio_oe = {8{read}};

  // inputs
  wire chk_range = ui_in[2];
  wire cbe       = ui_in[3];
  wire cin       = (read ? 1 : ui_in[4]);
  wire cout      = (read ? ui_in[4] : 1);
  wire bin       = (read ? 1 : ui_in[5]);
  wire bout      = (read ? ui_in[5] : 1);
  wire rst_out   = ui_in[6];
  wire rst_in    = ui_in[7];

  // outputs
  wire cin_eof, cout_eof;
  wire bin_eof, bout_eof;
  wire ready, retry, invalid, overlong, nonuni, error;
  wire control, surrogate, highchar, private, nonchar;
  wire normal = ready & ~(error | control | surrogate | highchar | private | nonchar);

  assign uo_out[0] = (errs ? ready    : normal   );
  assign uo_out[1] = (errs ? retry    : control  );
  assign uo_out[2] = (errs ? invalid  : surrogate);
  assign uo_out[3] = (errs ? overlong : highchar );
  assign uo_out[4] = (errs ? nonuni   : private  );
  assign uo_out[5] = (errs ? error    : nonchar  );
  assign uo_out[6] = (read ? cout_eof : cin_eof  );
  assign uo_out[7] = (read ? bout_eof : bin_eof  );

  hardware_utf8 u8(
    uio_in, uio_out, chk_range, cbe,
    cin, cout, cin_eof, cout_eof,
    bin, bout, bin_eof, bout_eof,
    ready, retry, invalid, overlong, nonuni, error,
    control, surrogate, highchar, private, nonchar,
    rst_in, rst_out
  );

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, clk, rst_n, 1'b0};

endmodule
