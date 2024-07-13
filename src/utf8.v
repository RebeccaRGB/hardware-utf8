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
	output wire normal,      // ~(control | surrogate | private | nonchar)
	output wire control,     // character is a C0 or C1 control character
	output wire surrogate,   // character is a surrogate
	output wire highchar,    // character is a high surrogate or non-BMP
	output wire private,     // character is in a private use area
	output wire nonchar,     // character is a non-character
	input  wire rst_in,      // reset input (clears all registers)
	input  wire rst_out,     // reset output (clears only read positions)
	input  wire clk
);

	reg [31:0] rc; // character register
	reg [2:0] rcip; // character input pointer
	reg [2:0] rcop; // character output pointer
	reg [2:0] rbip; // byte input pointer
	reg [2:0] rbop; // byte output pointer

	task reset_all; begin
		// reset all registers
		rc <= 0;
		rcip <= 0;
		rcop <= 0;
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
		// write 8 bits to character register
		rc <= rcin;
		if (rcin < 32'h80000000) begin
			// 0x00000000 - 0x7FFFFFFF
			// valid encoding
			if (|rcin[30:26]) rbip <= 6;
			else if (|rcin[25:21]) rbip <= 5;
			else if (|rcin[20:16]) rbip <= 4;
			else if (|rcin[15:11]) rbip <= 3;
			else if (|rcin[10:7]) rbip <= 2;
			else rbip <= 1;
			ready <= 1;
			retry <= 0;
			invalid <= 0;
			overlong <= 0;
			nonuni <= (rcin[30:16] >= 15'h11);
		end else if (rcin < 32'hF0000000) begin
			// 0x80000000 - 0xEFFFFFFF
			// invalid input
			rbip <= 0;
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
				rbip <= 6;
				ready <= 1;
				invalid <= 0;
				overlong <= 1;
			end else if (rcin < 32'hF8000000) begin
				// 0xF4000000 - 0xF7FFFFFF
				// gap
				rbip <= 6;
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hF8200000) begin
				// 0xF8000000 - 0xF81FFFFF
				// 5-byte overlong encoding
				rbip <= 5;
				ready <= 1;
				invalid <= 0;
				overlong <= 1;
			end else if (rcin < 32'hFC000000) begin
				// 0xF8200000 - 0xFBFFFFFF
				// 5-byte unmasked encoding
				rbip <= 5;
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFE000000) begin
				// 0xFC000000 - 0xFDFFFFFF
				// 5-byte truncated encoding
				rbip <= 5;
				ready <= 0;
				invalid <= 0;
				overlong <= 0;
			end else if (rcin < 32'hFFC00000) begin
				// 0xFE000000 - 0xFFBFFFFF
				// gap
				rbip <= 5;
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFFC10000) begin
				// 0xFFC00000 - 0xFFC0FFFF
				// 4-byte overlong encoding
				rbip <= 4;
				ready <= 1;
				invalid <= 0;
				overlong <= 1;
			end else if (rcin < 32'hFFE00000) begin
				// 0xFFC10000 - 0xFFDFFFFF
				// 4-byte unmasked encoding
				rbip <= 4;
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFFF80000) begin
				// 0xFFE00000 - 0xFFF7FFFF
				// 4-byte truncated encoding
				rbip <= 4;
				ready <= 0;
				invalid <= 0;
				overlong <= 0;
			end else if (rcin < 32'hFFFE0000) begin
				// 0xFFF80000 - 0xFFFDFFFF
				// gap
				rbip <= 4;
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFFFE0800) begin
				// 0xFFFE0000 - 0xFFFE07FF
				// 3-byte overlong encoding
				rbip <= 3;
				ready <= 1;
				invalid <= 0;
				overlong <= 1;
			end else if (rcin < 32'hFFFF0000) begin
				// 0xFFFE0800 - 0xFFFEFFFF
				// 3-byte unmasked encoding
				rbip <= 3;
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFFFFE000) begin
				// 0xFFFF0000 - 0xFFFFDFFF
				// 3-byte truncated encoding
				rbip <= 3;
				ready <= 0;
				invalid <= 0;
				overlong <= 0;
			end else if (rcin < 32'hFFFFF000) begin
				// 0xFFFFE000 - 0xFFFFEFFF
				// gap
				rbip <= 3;
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFFFFF080) begin
				// 0xFFFFF000 - 0xFFFFF07F
				// 2-byte overlong encoding
				rbip <= 2;
				ready <= 1;
				invalid <= 0;
				overlong <= 1;
			end else if (rcin < 32'hFFFFF800) begin
				// 0xFFFFF080 - 0xFFFFF7FF
				// 2-byte unmasked encoding
				rbip <= 2;
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFFFFFF80) begin
				// 0xFFFFF800 - 0xFFFFFF7F
				// 2-byte truncated encoding
				rbip <= 2;
				ready <= 0;
				invalid <= 0;
				overlong <= 0;
			end else if (rcin < 32'hFFFFFFC0) begin
				// 0xFFFFFF80 - 0xFFFFFFBF
				// lone trailing byte
				rbip <= 1;
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end else if (rcin < 32'hFFFFFFFE) begin
				// 0xFFFFFFC0 - 0xFFFFFFFD
				// lone leading byte
				rbip <= 1;
				ready <= 0;
				invalid <= 0;
				overlong <= 0;
			end else begin
				// 0xFFFFFFFE - 0xFFFFFFFF
				// lone invalid byte
				rbip <= 1;
				ready <= 1;
				invalid <= 1;
				overlong <= 0;
			end
		end
		if (rcip < 4) rcip <= rcip + 1;
	end endtask

	task read_rc; begin
		// read 8 bits from character register
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

	task write_rb_decode_utf8; begin
		// write UTF-8 byte to character register
		if (rbip == 0) begin
			rbip <= 1;
			rc <= {{24{din[7]}}, din};
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
					rbip <= 2;
					if (&{rc[31:6], ~rc[5]}) begin
						ready <= 1;
						if (|rc[4:1]) begin
							rc <= {21'b0, rc[4:0], din[5:0]};
							nonuni <= 0;
						end else begin
							rc <= {rc[25:0], din[5:0]};
							overlong <= 1;
						end
					end else begin
						rc <= {rc[25:0], din[5:0]};
					end
				end
				2: begin
					rbip <= 3;
					if (&{rc[31:11], ~rc[10]}) begin
						ready <= 1;
						if (|rc[9:5]) begin
							rc <= {16'b0, rc[9:0], din[5:0]};
							nonuni <= 0;
						end else begin
							rc <= {rc[25:0], din[5:0]};
							overlong <= 1;
						end
					end else begin
						rc <= {rc[25:0], din[5:0]};
					end
				end
				3: begin
					rbip <= 4;
					if (&{rc[31:16], ~rc[15]}) begin
						ready <= 1;
						if (|rc[14:10]) begin
							rc <= {11'b0, rc[14:0], din[5:0]};
							nonuni <= (rc[14:10] >= 5'h11);
						end else begin
							rc <= {rc[25:0], din[5:0]};
							overlong <= 1;
						end
					end else begin
						rc <= {rc[25:0], din[5:0]};
					end
				end
				4: begin
					rbip <= 5;
					if (&{rc[31:21], ~rc[20]}) begin
						ready <= 1;
						if (|rc[19:15]) begin
							rc <= {6'b0, rc[19:0], din[5:0]};
							nonuni <= (rc[19:10] >= 10'h11);
						end else begin
							rc <= {rc[25:0], din[5:0]};
							overlong <= 1;
						end
					end else begin
						rc <= {rc[25:0], din[5:0]};
					end
				end
				5: begin
					rbip <= 6;
					if (&{rc[31:26], ~rc[25]}) begin
						ready <= 1;
						if (|rc[24:20]) begin
							rc <= {1'b0, rc[24:0], din[5:0]};
							nonuni <= (rc[24:10] >= 15'h11);
						end else begin
							rc <= {4'hF, rc[21:0], din[5:0]};
							overlong <= 1;
						end
					end else begin
						rc <= {4'hF, rc[21:0], din[5:0]};
					end
				end
			endcase
		end
	end endtask

	task read_rb; begin
		// read UTF-8 byte from character register
		if (rbop >= rbip) begin
			dout <= 0;
		end else if (rbop == 0) begin
			case (rbip)
				1: dout <= rc[7:0];
				2: dout <= {2'b11, rc[11:6]};
				3: dout <= {3'b111, rc[16:12]};
				4: dout <= {4'b1111, rc[21:18]};
				5: dout <= {5'b11111, rc[26:24]};
				6: dout <= {7'b1111110, (rc[31] ? 1'b0 : rc[30])};
				default: dout <= 0;
			endcase
		end else begin
			case (rbip - rbop)
				1: dout <= {2'b10, rc[5:0]};
				2: dout <= {2'b10, rc[11:6]};
				3: dout <= {2'b10, rc[17:12]};
				4: dout <= {2'b10, rc[23:18]};
				5: dout <= {2'b10, (rc[31] ? 2'b0 : rc[29:28]), rc[27:24]};
				default: dout <= 0;
			endcase
		end
		if (rbop < rbip) rbop <= rbop + 1;
	end endtask

	always @(posedge clk) begin
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
