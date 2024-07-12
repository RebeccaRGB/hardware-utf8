module hardware_utf8 (
	input  wire [7:0] din,   // data input
	output reg  [7:0] dout,  // data output
	input  wire chk_range,   // restrict valid characters to 0-0x10FFFF
	input  wire cbe,         // character I/O is big endian
	input  wire cin,         // character input clock
	input  wire cout,        // character output clock
	output wire cin_eof,     // character input end of file
	output wire cout_eof,    // character output end of file
	input  wire bin,         // byte input clock
	input  wire bout,        // byte output clock
	output wire bin_eof,     // byte input end of file
	output wire bout_eof,    // byte output end of file
	output reg  ready,       // byte sequence is complete
	output reg  retry,       // consume output, reset, and try same input again
	output reg  invalid,     // input was invalid
	output reg  overlong,    // overlong encoding
	output reg  nonuni,      // out of Unicode range
	output wire error,       // (retry | invalid | overlong | (nonuni & chk_range))
	output wire normal,      // character is none of the below
	output wire control,     // character is a C0 or C1 control character
	output wire surrogate,   // character is a surrogate
	output wire highchar,    // character is a high surrogate or non-BMP
	output wire private,     // character is in a private use area
	output wire nonchar,     // character is a non-character
	input  wire rst_in,      // reset input (clears all registers)
	input  wire rst_out      // reset output (clears only read positions)
);

	reg [31:0] rc; // character register
	reg [2:0] rcip; // character input pointer
	reg [2:0] rcop; // character output pointer

	reg [7:0] rb0; // byte register 0
	reg [7:0] rb1; // byte register 1
	reg [7:0] rb2; // byte register 2
	reg [7:0] rb3; // byte register 3
	reg [7:0] rb4; // byte register 4
	reg [7:0] rb5; // byte register 5
	reg [2:0] rbip; // byte input pointer
	reg [2:0] rbop; // byte output pointer

	task reset_all; begin
		// reset all registers
		rc <= 0;
		rcip <= 0;
		rcop <= 0;
		rb0 <= 0;
		rb1 <= 0;
		rb2 <= 0;
		rb3 <= 0;
		rb4 <= 0;
		rb5 <= 0;
		rbip <= 0;
		rbop <= 0;
		dout <= 0;
		ready <= 0;
		retry <= 0;
		invalid <= 0;
		overlong <= 0;
		nonuni <= 0;
	end endtask

	task reset_read; begin
		// reset only read pointers
		rcop <= 0;
		rbop <= 0;
		dout <= 0;
	end endtask

	// value for character register after consuming the next 8 bits from din
	wire [31:0] rcin = (
		cbe ? {rc[23:0], din} :
		(rcip == 0) ? {rc[31:8], din} :
		(rcip == 1) ? {rc[31:16], din, rc[7:0]} :
		(rcip == 2) ? {rc[31:24], din, rc[15:0]} :
		(rcip == 3) ? {din, rc[23:0]} :
		rc
	);

	task write_rc_encode_utf8; begin
		// write byte to character register
		rc <= rcin;

		// encode to utf8
		if (rcin < 32'h80) begin
			// 0x00000000 - 0x0000007F
			// 1-byte correct encoding of 1-byte sequence
			rb0 <= rcin[7:0];
			rb1 <= 0;
			rb2 <= 0;
			rb3 <= 0;
			rb4 <= 0;
			rb5 <= 0;
			rbip <= 1;
		end else if (rcin < 32'h800) begin
			// 0x00000080 - 0x000007FF
			// 2-byte correct encoding of 2-byte sequence
			rb0 <= {3'b110, rcin[10:6]};
			rb1 <= {2'b10, rcin[5:0]};
			rb2 <= 0;
			rb3 <= 0;
			rb4 <= 0;
			rb5 <= 0;
			rbip <= 2;
		end else if (rcin < 32'h10000) begin
			// 0x00000800 - 0x0000FFFF
			// 3-byte correct encoding of 3-byte sequence
			rb0 <= {4'b1110, rcin[15:12]};
			rb1 <= {2'b10, rcin[11:6]};
			rb2 <= {2'b10, rcin[5:0]};
			rb3 <= 0;
			rb4 <= 0;
			rb5 <= 0;
			rbip <= 3;
		end else if (rcin < 32'h200000) begin
			// 0x00010000 - 0x001FFFFF
			// 4-byte correct encoding of 4-byte sequence
			rb0 <= {5'b11110, rcin[20:18]};
			rb1 <= {2'b10, rcin[17:12]};
			rb2 <= {2'b10, rcin[11:6]};
			rb3 <= {2'b10, rcin[5:0]};
			rb4 <= 0;
			rb5 <= 0;
			rbip <= 4;
		end else if (rcin < 32'h4000000) begin
			// 0x00200000 - 0x03FFFFFF
			// 5-byte correct encoding of 5-byte sequence
			rb0 <= {6'b111110, rcin[25:24]};
			rb1 <= {2'b10, rcin[23:18]};
			rb2 <= {2'b10, rcin[17:12]};
			rb3 <= {2'b10, rcin[11:6]};
			rb4 <= {2'b10, rcin[5:0]};
			rb5 <= 0;
			rbip <= 5;
		end else if (rcin < 32'h80000000) begin
			// 0x40000000 - 0x7FFFFFFF
			// 6-byte correct encoding of 6-byte sequence
			rb0 <= {7'b1111110, rcin[30]};
			rb1 <= {2'b10, rcin[29:24]};
			rb2 <= {2'b10, rcin[23:18]};
			rb3 <= {2'b10, rcin[17:12]};
			rb4 <= {2'b10, rcin[11:6]};
			rb5 <= {2'b10, rcin[5:0]};
			rbip <= 6;
		end else if (rcin < 32'hF0000000) begin
			// 0x80000000 - 0xEFFFFFFF
			// invalid input
			rb0 <= 0;
			rb1 <= 0;
			rb2 <= 0;
			rb3 <= 0;
			rb4 <= 0;
			rb5 <= 0;
			rbip <= 0;
		end else if (rcin < 32'hF8000000) begin
			// 0xF0000000 - 0xF3FFFFFF
			// 6-byte invalid encoding
			rb0 <= 8'b11111100;
			rb1 <= {4'b1000, rcin[27:24]};
			rb2 <= {2'b10, rcin[23:18]};
			rb3 <= {2'b10, rcin[17:12]};
			rb4 <= {2'b10, rcin[11:6]};
			rb5 <= {2'b10, rcin[5:0]};
			rbip <= 6;
		end else if (rcin < 32'hFFC00000) begin
			// 0xF8000000 - 0xFDFFFFFF
			// 5-byte invalid encoding
			rb0 <= rcin[31:24];
			rb1 <= {2'b10, rcin[23:18]};
			rb2 <= {2'b10, rcin[17:12]};
			rb3 <= {2'b10, rcin[11:6]};
			rb4 <= {2'b10, rcin[5:0]};
			rb5 <= 0;
			rbip <= 5;
		end else if (rcin < 32'hFFFE0000) begin
			// 0xFFC00000 - 0xFFF7FFFF
			// 4-byte invalid encoding
			rb0 <= rcin[25:18];
			rb1 <= {2'b10, rcin[17:12]};
			rb2 <= {2'b10, rcin[11:6]};
			rb3 <= {2'b10, rcin[5:0]};
			rb4 <= 0;
			rb5 <= 0;
			rbip <= 4;
		end else if (rcin < 32'hFFFFF000) begin
			// 0xFFFE0000 - 0xFFFFDFFF
			// 3-byte invalid encoding
			rb0 <= rcin[19:12];
			rb1 <= {2'b10, rcin[11:6]};
			rb2 <= {2'b10, rcin[5:0]};
			rb3 <= 0;
			rb4 <= 0;
			rb5 <= 0;
			rbip <= 3;
		end else if (rcin < 32'hFFFFFF80) begin
			// 0xFFFFF000 - 0xFFFFFF7F
			// 2-byte invalid encoding
			rb0 <= rcin[13:6];
			rb1 <= {2'b10, rcin[5:0]};
			rb2 <= 0;
			rb3 <= 0;
			rb4 <= 0;
			rb5 <= 0;
			rbip <= 2;
		end else begin
			// 0xFFFFFF80 - 0xFFFFFFFF
			// single invalid byte
			rb0 <= rcin[7:0];
			rb1 <= 0;
			rb2 <= 0;
			rb3 <= 0;
			rb4 <= 0;
			rb5 <= 0;
			rbip <= 1;
		end

		// set status flags
		if (rcin < 32'h110000) begin
			// 0x00000000 - 0x0010FFFF
			// valid Unicode code point
			ready <= 1;
			retry <= 0;
			invalid <= 0;
			overlong <= 0;
			nonuni <= 0;
		end else if (rcin < 32'h80000000) begin
			// 0x00110000 - 0x7FFFFFFF
			// out of Unicode range
			ready <= 1;
			retry <= 0;
			invalid <= 0;
			overlong <= 0;
			nonuni <= 1;
		end else if (rcin < 32'hF0000000) begin
			// 0x80000000 - 0xEFFFFFFF
			// invalid input
			ready <= 1;
			retry <= 0;
			invalid <= 1;
			overlong <= 0;
			nonuni <= 0;
		end else begin
			// 0xF0000000 - 0xFFFFFFFF
			// invalid encoding
			retry <= 0;
			nonuni <= 0;
			if (rcin < 32'hF4000000) begin
				// 0xF0000000 - 0xF3FFFFFF
				// 6-byte overlong encoding
				ready <= 1;
				invalid <= 0;
				overlong <= 1;
			end else if (rcin < 32'hF8000000) begin
				// 0xF4000000 - 0xF7FFFFFF
				// gap
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hF8200000) begin
				// 0xF8000000 - 0xF81FFFFF
				// 5-byte overlong encoding
				ready <= 1;
				invalid <= 0;
				overlong <= 1;
			end else if (rcin < 32'hFC000000) begin
				// 0xF8200000 - 0xFBFFFFFF
				// 5-byte unmasked encoding
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFE000000) begin
				// 0xFC000000 - 0xFDFFFFFF
				// 5-byte truncated encoding
				ready <= 0;
				invalid <= 0;
				overlong <= 0;
			end else if (rcin < 32'hFFC00000) begin
				// 0xFE000000 - 0xFFBFFFFF
				// gap
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFFC10000) begin
				// 0xFFC00000 - 0xFFC0FFFF
				// 4-byte overlong encoding
				ready <= 1;
				invalid <= 0;
				overlong <= 1;
			end else if (rcin < 32'hFFE00000) begin
				// 0xFFC10000 - 0xFFDFFFFF
				// 4-byte unmasked encoding
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFFF80000) begin
				// 0xFFE00000 - 0xFFF7FFFF
				// 4-byte truncated encoding
				ready <= 0;
				invalid <= 0;
				overlong <= 0;
			end else if (rcin < 32'hFFFE0000) begin
				// 0xFFF80000 - 0xFFFDFFFF
				// gap
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFFFE0800) begin
				// 0xFFFE0000 - 0xFFFE07FF
				// 3-byte overlong encoding
				ready <= 1;
				invalid <= 0;
				overlong <= 1;
			end else if (rcin < 32'hFFFF0000) begin
				// 0xFFFE0800 - 0xFFFEFFFF
				// 3-byte unmasked encoding
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFFFFE000) begin
				// 0xFFFF0000 - 0xFFFFDFFF
				// 3-byte truncated encoding
				ready <= 0;
				invalid <= 0;
				overlong <= 0;
			end else if (rcin < 32'hFFFFF000) begin
				// 0xFFFFE000 - 0xFFFFEFFF
				// gap
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFFFFF080) begin
				// 0xFFFFF000 - 0xFFFFF07F
				// 2-byte overlong encoding
				ready <= 1;
				invalid <= 0;
				overlong <= 1;
			end else if (rcin < 32'hFFFFF800) begin
				// 0xFFFFF080 - 0xFFFFF7FF
				// 2-byte unmasked encoding
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFFFFFF80) begin
				// 0xFFFFF800 - 0xFFFFFF7F
				// 2-byte truncated encoding
				ready <= 0;
				invalid <= 0;
				overlong <= 0;
			end else if (rcin < 32'hFFFFFFC0) begin
				// 0xFFFFFF80 - 0xFFFFFFBF
				// lone trailing byte
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFFFFFFFE) begin
				// 0xFFFFFFC0 - 0xFFFFFFFD
				// lone leading byte
				ready <= 0;
				invalid <= 0;
				overlong <= 0;
			end else begin
				// 0xFFFFFFFE - 0xFFFFFFFF
				// lone invalid byte
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end
		end

		// increment pointer
		if (rcip < 4) rcip <= rcip + 1;
	end endtask

	task read_rc; begin
		// read byte from character register
		if (cbe) begin
			case (rcop)
				0: dout <= rc[31:24];
				1: dout <= rc[23:16];
				2: dout <= rc[15:8];
				3: dout <= rc[7:0];
				default: dout <= 0;
			endcase
		end else begin
			case (rcop)
				0: dout <= rc[7:0];
				1: dout <= rc[15:8];
				2: dout <= rc[23:16];
				3: dout <= rc[31:24];
				default: dout <= 0;
			endcase
		end
		if (rcop < 4) rcop <= rcop + 1;
	end endtask

	// all possible values for character register after consuming a byte from din
	wire [31:0] rc0 = {{24{din[7]}}, din};
	wire [31:0] rc1c = {21'b0, rb0[4:0], din[5:0]};
	wire [31:0] rc1m = {18'h3FFFF, rb0, din[5:0]};
	wire [31:0] rc2c = {16'b0, rb0[3:0], rb1[5:0], din[5:0]};
	wire [31:0] rc2m = {12'hFFF, rb0, rb1[5:0], din[5:0]};
	wire [31:0] rc3c = {11'b0, rb0[2:0], rb1[5:0], rb2[5:0], din[5:0]};
	wire [31:0] rc3m = {6'h3F, rb0, rb1[5:0], rb2[5:0], din[5:0]};
	wire [31:0] rc4c = {6'b0, rb0[1:0], rb1[5:0], rb2[5:0], rb3[5:0], din[5:0]};
	wire [31:0] rc4m = {rb0, rb1[5:0], rb2[5:0], rb3[5:0], din[5:0]};
	wire [31:0] rc5c = {rb0[1:0], rb1[5:0], rb2[5:0], rb3[5:0], rb4[5:0], din[5:0]};
	wire [31:0] rc5m = {4'hF, rb1[3:0], rb2[5:0], rb3[5:0], rb4[5:0], din[5:0]};

	task write_rb_decode_utf8; begin
		// write byte to byte buffer
		case (rbip)
			0: rb0 <= din;
			1: rb1 <= din;
			2: rb2 <= din;
			3: rb3 <= din;
			4: rb4 <= din;
			5: rb5 <= din;
		endcase

		// decode from utf8
		// set status flags
		if (rbip == 0) begin
			rc <= rc0;
			retry <= 0;
			overlong <= 0;
			nonuni <= 0;
			if (din < 8'h80) begin
				ready <= 1;
				invalid <= 0;
			end else if (din < 8'hC0) begin
				ready <= 1;
				invalid <= 1;
			end else if (din < 8'hFE) begin
				ready <= 0;
				invalid <= 0;
			end else begin
				ready <= 1;
				invalid <= 1;
			end
		end else if (ready || (din[7:6] != 2'b10)) begin
			retry <= 1;
		end else begin
			case (rbip)
				1: begin
					if (rb0[7:5] == 3'b110) begin
						ready <= 1;
						if (rb0[4:1] != 0) begin
							rc <= rc1c;
							nonuni <= (rc1c >= 32'h110000);
						end else begin
							rc <= rc1m;
							overlong <= 1;
						end
					end else begin
						rc <= rc1m;
					end
				end
				2: begin
					if (rb0[7:4] == 4'b1110) begin
						ready <= 1;
						if ({rb0[3:0], rb1[5]} != 0) begin
							rc <= rc2c;
							nonuni <= (rc2c >= 32'h110000);
						end else begin
							rc <= rc2m;
							overlong <= 1;
						end
					end else begin
						rc <= rc2m;
					end
				end
				3: begin
					if (rb0[7:3] == 5'b11110) begin
						ready <= 1;
						if ({rb0[2:0], rb1[5:4]} != 0) begin
							rc <= rc3c;
							nonuni <= (rc3c >= 32'h110000);
						end else begin
							rc <= rc3m;
							overlong <= 1;
						end
					end else begin
						rc <= rc3m;
					end
				end
				4: begin
					if (rb0[7:2] == 6'b111110) begin
						ready <= 1;
						if ({rb0[1:0], rb1[5:3]} != 0) begin
							rc <= rc4c;
							nonuni <= (rc4c >= 32'h110000);
						end else begin
							rc <= rc4m;
							overlong <= 1;
						end
					end else begin
						rc <= rc4m;
					end
				end
				5: begin
					if (rb0[7:1] == 7'b1111110) begin
						ready <= 1;
						if ({rb0[0], rb1[5:2]} != 0) begin
							rc <= rc5c;
							nonuni <= (rc5c >= 32'h110000);
						end else begin
							rc <= rc5m;
							overlong <= 1;
						end
					end else begin
						rc <= rc5m;
					end
				end
			endcase
		end

		// increment pointer
		if (rbip < 6) rbip <= rbip + 1;
	end endtask

	task read_rb; begin
		// read byte from byte buffer
		case (rbop)
			0: dout <= rb0;
			1: dout <= rb1;
			2: dout <= rb2;
			3: dout <= rb3;
			4: dout <= rb4;
			5: dout <= rb5;
			default: dout <= 0;
		endcase
		if (rbop < 6) rbop <= rbop + 1;
	end endtask

	wire something_dumb = rst_in & rst_out & cin & bin & cout & bout;

	always @(negedge something_dumb) begin
		if (~rst_in) reset_all;
		else if (~rst_out) reset_read;
		else if (~cin) write_rc_encode_utf8;
		else if (~bin) write_rb_decode_utf8;
		else if (~cout) read_rc;
		else if (~bout) read_rb;
	end

	assign cin_eof = (rcip >= 4);
	assign cout_eof = (rcop >= 4);
	assign bin_eof = (rbip >= 6);
	assign bout_eof = (rbop >= rbip);
	assign error = (retry | invalid | overlong | (nonuni & chk_range));

	wire p_ok = ready & ~(invalid | overlong | (nonuni & chk_range));
	wire p_ct = (rc < 32'h20) || (rc >= 32'h7F && rc < 32'hA0);
	wire p_sr = (rc >= 32'hD800 && rc < 32'hE000);
	wire p_hi = (rc >= 32'hD800 && rc < 32'hDC00) || (rc[31:16] > 0);
	wire p_pu = (rc >= 32'hDB80 && rc < 32'hDC00) ||
	            (rc >= 32'hE000 && rc < 32'hF900) ||
	            (rc[31:16] >= 16'h000F && rc[15:0] < 16'hFFFE);
	wire p_nc = (rc >= 32'hFDD0 && rc < 32'hFDF0) || (rc[15:0] >= 16'hFFFE);

	assign normal = p_ok & ~(p_ct | p_sr | p_pu | p_nc);
	assign control = p_ok & p_ct;
	assign surrogate = p_ok & p_sr;
	assign highchar = p_ok & p_hi;
	assign private = p_ok & p_pu;
	assign nonchar = p_ok & p_nc;

endmodule
