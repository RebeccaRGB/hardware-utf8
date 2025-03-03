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

  // inputs
  wire rst_in    = rst_n;    // reset input, active low
  wire rst_out   = ui_in[0]; // reset output, active low
  wire errs      = ui_in[1]; // HIGH for errors, LOW for character properties
  wire chk_range = ui_in[2]; // HIGH to signal error on value ≥0x110000
  wire cbe       = ui_in[3]; // HIGH for big endian, LOW for little endian
  wire read      = ui_in[4]; // HIGH to read, LOW to write
  wire cin       = (read ? 1 : ui_in[5]); // character input
  wire cout      = (read ? ui_in[5] : 1); // character output
  wire uin       = (read ? 1 : ui_in[6]); // UTF-16 input
  wire uout      = (read ? ui_in[6] : 1); // UTF-16 output
  wire bin       = (read ? 1 : ui_in[7]); // UTF-8 input
  wire bout      = (read ? ui_in[7] : 1); // UTF-8 output
  assign uio_oe  = {8{read}};

  // outputs
  wire cin_eof, cout_eof;
  wire bin_eof, bout_eof;
  wire uin_eof, uout_eof;
  wire ready, retry, invalid, overlong, nonuni, error;
  wire normal, control, surrogate, highchar, private, nonchar;

  assign uo_out[0] = (errs ? ready    : normal   );
  assign uo_out[1] = (errs ? retry    : control  );
  assign uo_out[2] = (errs ? invalid  : surrogate);
  assign uo_out[3] = (errs ? overlong : highchar );
  assign uo_out[4] = (errs ? nonuni   : private  );
  assign uo_out[5] = (errs ? error    : nonchar  );
  assign uo_out[6] = (read ? uout_eof : uin_eof  );
  assign uo_out[7] = (read ? bout_eof : bin_eof  );

  hardware_utf8 u8(
    uio_in, uio_out, chk_range, cbe,
    cin, cout, cin_eof, cout_eof,
    bin, bout, bin_eof, bout_eof,
    uin, uout, uin_eof, uout_eof,
    ready, retry, invalid, overlong, nonuni, error,
    normal, control, surrogate, highchar, private, nonchar,
    rst_in, rst_out, clk
  );

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, cout_eof, cin_eof, 1'b0};

endmodule
