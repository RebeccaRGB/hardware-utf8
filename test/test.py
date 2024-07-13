# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0xFF
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 10)
    assert dut.uo_out.value == 0x80
    assert dut.uio_out.value == 0

    dut._log.info("Test project behavior")

    global ui_in
    ui_in = 0xFF

    async def clear_input(b):
        global ui_in
        ui_in &=~ (1 << b)
        dut.ui_in.value = ui_in
        await ClockCycles(dut.clk, 1)

    async def set_input(b):
        global ui_in
        ui_in |= (1 << b)
        dut.ui_in.value = ui_in
        await ClockCycles(dut.clk, 1)

    def get_output(b):
        return (dut.uo_out.value >> b) & 1

    async def write_byte(b, eof):
        dut.uio_in.value = b;
        await clear_input(0) # write mode
        await clear_input(5) # byte input clock down
        await set_input(5) # byte input clock up
        assert get_output(7) == eof

    async def read_byte(b, eof):
        await set_input(0) # read mode
        await clear_input(5) # byte output clock down
        await set_input(5) # byte output clock up
        assert get_output(7) == eof
        assert dut.uio_out.value == b

    async def write_char(b, eof):
        dut.uio_in.value = b;
        await clear_input(0) # write mode
        await clear_input(4) # char input clock down
        await set_input(4) # char input clock up
        assert get_output(6) == eof

    async def read_char(b, eof):
        await set_input(0) # read mode
        await clear_input(4) # char output clock down
        await set_input(4) # char output clock up
        assert get_output(6) == eof
        assert dut.uio_out.value == b

    async def read_reset():
        await clear_input(6) # read reset clock down
        await set_input(6) # read reset clock up

    async def write_reset():
        global ui_in
        await clear_input(7) # write reset clock down
        await set_input(7) # write reset clock up
        assert dut.uo_out.value == (0x80 if (ui_in & 0x01) else 0)
        assert dut.uio_out.value == 0

    async def write_cp(cp):
        await clear_input(0) # write mode
        dut.uio_in.value = (cp >> 24) & 0xFF
        await clear_input(4) # char input clock down
        await set_input(4) # char input clock up
        assert get_output(6) == 0
        dut.uio_in.value = (cp >> 16) & 0xFF
        await clear_input(4) # char input clock down
        await set_input(4) # char input clock up
        assert get_output(6) == 0
        dut.uio_in.value = (cp >> 8) & 0xFF
        await clear_input(4) # char input clock down
        await set_input(4) # char input clock up
        assert get_output(6) == 0
        dut.uio_in.value = cp & 0xFF
        await clear_input(4) # char input clock down
        await set_input(4) # char input clock up
        assert get_output(6) == 1

    async def read_bytes(*args):
        await set_input(0) # read mode
        for b in args:
            assert get_output(7) == 0
            await clear_input(5) # byte output clock down
            await set_input(5) # byte output clock up
            assert dut.uio_out.value == b
        assert get_output(7) == 1
        await clear_input(5) # byte output clock down
        await set_input(5) # byte output clock up
        assert dut.uio_out.value == 0
        assert get_output(7) == 1

    async def write_bytes(*args):
        await clear_input(0) # write mode
        for b in args:
            dut.uio_in.value = b
            await clear_input(5) # byte input clock down
            await set_input(5) # byte input clock up

    async def read_cp(cp):
        await set_input(0) # read mode
        await clear_input(4) # char output clock down
        await set_input(4) # char output clock up
        assert dut.uio_out.value == (cp >> 24) & 0xFF
        assert get_output(6) == 0
        await clear_input(4) # char output clock down
        await set_input(4) # char output clock up
        assert dut.uio_out.value == (cp >> 16) & 0xFF
        assert get_output(6) == 0
        await clear_input(4) # char output clock down
        await set_input(4) # char output clock up
        assert dut.uio_out.value == (cp >> 8) & 0xFF
        assert get_output(6) == 0
        await clear_input(4) # char output clock down
        await set_input(4) # char output clock up
        assert dut.uio_out.value == cp & 0xFF
        assert get_output(6) == 1

    UNDERFLOW = 0x00
    READY     = 0x01
    RETRY     = 0x02
    INVALID   = 0x04
    OVERLONG  = 0x08
    NONUNI    = 0x10
    ERROR     = 0x20

    async def want_errs(errs):
        await set_input(1) # error reporting mode
        assert (dut.uo_out.value & 0x3F) == errs

    async def want_retry(retry):
        await set_input(1) # error reporting mode
        assert (dut.uo_out.value & RETRY) == (RETRY if retry else 0)

    NORMAL    = 0x01
    CONTROL   = 0x02
    SURROGATE = 0x04
    HIGHCHAR  = 0x08
    PRIVATE   = 0x10
    NONCHAR   = 0x20

    async def want_props(props):
        await clear_input(1) # property reporting mode
        assert (dut.uo_out.value & 0x3F) == props

    # register I/O

    # write to byte buffer
    await write_byte(0xFD, 0)
    await write_byte(0xBE, 0)
    await write_byte(0xAC, 0)
    await write_byte(0x97, 0)
    await write_byte(0x86, 0)
    await write_byte(0xB5, 1)
    await write_byte(0xA4, 1)

    # read from byte buffer
    await read_byte(0xFD, 0)
    await read_byte(0xBE, 0)
    await read_byte(0xAC, 0)
    await read_byte(0x97, 0)
    await read_byte(0x86, 0)
    await read_byte(0xB5, 1)
    await read_byte(0, 1)

    # read from byte buffer again
    await read_reset()
    await read_byte(0xFD, 0)
    await read_byte(0xBE, 0)
    await read_byte(0xAC, 0)
    await read_byte(0x97, 0)
    await read_byte(0x86, 0)
    await read_byte(0xB5, 1)
    await read_byte(0, 1)

    await write_reset()

    # write to character buffer, big endian
    await write_char(11, 0)
    await write_char(22, 0)
    await write_char(33, 0)
    await write_char(44, 1)
    await write_char(55, 1)

    # read from character buffer, big endian
    await read_char(22, 0)
    await read_char(33, 0)
    await read_char(44, 0)
    await read_char(55, 1)
    await read_char(0, 1)

    # read from character buffer again
    await read_reset()
    await read_char(22, 0)
    await read_char(33, 0)
    await read_char(44, 0)
    await read_char(55, 1)
    await read_char(0, 1)

    await clear_input(3)
    await write_reset()

    # write to character buffer, little endian
    await write_char(11, 0)
    await write_char(22, 0)
    await write_char(33, 0)
    await write_char(44, 1)
    await write_char(55, 1)

    # read from character buffer, little endian
    await read_char(11, 0)
    await read_char(22, 0)
    await read_char(33, 0)
    await read_char(44, 1)
    await read_char(0, 1)

    # read from character buffer again
    await read_reset()
    await read_char(11, 0)
    await read_char(22, 0)
    await read_char(33, 0)
    await read_char(44, 1)
    await read_char(0, 1)

    await set_input(3)
    await write_reset()

    # write to byte buffer
    await write_byte(0xFD, 0)
    await write_byte(0xBE, 0)
    await write_byte(0xAC, 0)

    # read from byte buffer
    await read_byte(0xFD, 0)
    await read_byte(0xBE, 0)
    await read_byte(0xAC, 1)
    await read_byte(0, 1)

    # read from byte buffer again
    await read_reset()
    await read_byte(0xFD, 0)
    await read_byte(0xBE, 0)
    await read_byte(0xAC, 1)
    await read_byte(0, 1)

    await write_reset()

    # write to character buffer, big endian
    await write_char(111, 0)
    await write_char(222, 0)

    # read from character buffer, big endian
    await read_char(0, 0)
    await read_char(0, 0)
    await read_char(111, 0)
    await read_char(222, 1)
    await read_char(0, 1)

    # read from character buffer again
    await read_reset()
    await read_char(0, 0)
    await read_char(0, 0)
    await read_char(111, 0)
    await read_char(222, 1)
    await read_char(0, 1)

    await clear_input(3)
    await write_reset()

    # write to character buffer, little endian
    await write_char(111, 0)
    await write_char(222, 0)

    # read from character buffer, little endian
    await read_char(111, 0)
    await read_char(222, 0)
    await read_char(0, 0)
    await read_char(0, 1)
    await read_char(0, 1)

    # read from character buffer again
    await read_reset()
    await read_char(111, 0)
    await read_char(222, 0)
    await read_char(0, 0)
    await read_char(0, 1)
    await read_char(0, 1)

    await set_input(3)
    await write_reset()

    # UTF-8 encoding

    async def test_encode(cp, errs, props, *args):
        await write_cp(cp)
        await want_errs(errs)
        await want_props(props)
        await read_bytes(*args)
        await write_reset()

    # ASCII
    await test_encode(0x00000000, READY, CONTROL, 0x00)
    await test_encode(0x00000001, READY, CONTROL, 0x01)
    await test_encode(0x0000001F, READY, CONTROL, 0x1F)
    await test_encode(0x00000020, READY, NORMAL, 0x20)
    await test_encode(0x0000007E, READY, NORMAL, 0x7E)
    await test_encode(0x0000007F, READY, CONTROL, 0x7F)
    # 2-byte sequence
    await test_encode(0x00000080, READY, CONTROL, 0xC2, 0x80)
    await test_encode(0x0000009F, READY, CONTROL, 0xC2, 0x9F)
    await test_encode(0x000000A0, READY, NORMAL, 0xC2, 0xA0)
    await test_encode(0x000000FF, READY, NORMAL, 0xC3, 0xBF)
    await test_encode(0x00000100, READY, NORMAL, 0xC4, 0x80)
    await test_encode(0x000007FF, READY, NORMAL, 0xDF, 0xBF)
    # 3-byte sequence
    await test_encode(0x00000800, READY, NORMAL, 0xE0, 0xA0, 0x80)
    await test_encode(0x0000D7FF, READY, NORMAL, 0xED, 0x9F, 0xBF)
    await test_encode(0x0000D800, READY, SURROGATE|HIGHCHAR, 0xED, 0xA0, 0x80)
    await test_encode(0x0000DB7F, READY, SURROGATE|HIGHCHAR, 0xED, 0xAD, 0xBF)
    await test_encode(0x0000DB80, READY, SURROGATE|HIGHCHAR|PRIVATE, 0xED, 0xAE, 0x80)
    await test_encode(0x0000DBFF, READY, SURROGATE|HIGHCHAR|PRIVATE, 0xED, 0xAF, 0xBF)
    await test_encode(0x0000DC00, READY, SURROGATE, 0xED, 0xB0, 0x80)
    await test_encode(0x0000DFFF, READY, SURROGATE, 0xED, 0xBF, 0xBF)
    await test_encode(0x0000E000, READY, PRIVATE, 0xEE, 0x80, 0x80)
    await test_encode(0x0000F8FF, READY, PRIVATE, 0xEF, 0xA3, 0xBF)
    await test_encode(0x0000F900, READY, NORMAL, 0xEF, 0xA4, 0x80)
    await test_encode(0x0000FDCF, READY, NORMAL, 0xEF, 0xB7, 0x8F)
    await test_encode(0x0000FDD0, READY, NONCHAR, 0xEF, 0xB7, 0x90)
    await test_encode(0x0000FDEF, READY, NONCHAR, 0xEF, 0xB7, 0xAF)
    await test_encode(0x0000FDF0, READY, NORMAL, 0xEF, 0xB7, 0xB0)
    await test_encode(0x0000FFFD, READY, NORMAL, 0xEF, 0xBF, 0xBD)
    await test_encode(0x0000FFFE, READY, NONCHAR, 0xEF, 0xBF, 0xBE)
    await test_encode(0x0000FFFF, READY, NONCHAR, 0xEF, 0xBF, 0xBF)
    # 4-byte sequence
    await test_encode(0x00010000, READY, NORMAL|HIGHCHAR, 0xF0, 0x90, 0x80, 0x80)
    await test_encode(0x0001FFFD, READY, NORMAL|HIGHCHAR, 0xF0, 0x9F, 0xBF, 0xBD)
    await test_encode(0x0001FFFE, READY, NONCHAR|HIGHCHAR, 0xF0, 0x9F, 0xBF, 0xBE)
    await test_encode(0x0001FFFF, READY, NONCHAR|HIGHCHAR, 0xF0, 0x9F, 0xBF, 0xBF)
    await test_encode(0x00020000, READY, NORMAL|HIGHCHAR, 0xF0, 0xA0, 0x80, 0x80)
    await test_encode(0x0002FFFD, READY, NORMAL|HIGHCHAR, 0xF0, 0xAF, 0xBF, 0xBD)
    await test_encode(0x0002FFFE, READY, NONCHAR|HIGHCHAR, 0xF0, 0xAF, 0xBF, 0xBE)
    await test_encode(0x0002FFFF, READY, NONCHAR|HIGHCHAR, 0xF0, 0xAF, 0xBF, 0xBF)
    await test_encode(0x00030000, READY, NORMAL|HIGHCHAR, 0xF0, 0xB0, 0x80, 0x80)
    await test_encode(0x0003FFFD, READY, NORMAL|HIGHCHAR, 0xF0, 0xBF, 0xBF, 0xBD)
    await test_encode(0x0003FFFE, READY, NONCHAR|HIGHCHAR, 0xF0, 0xBF, 0xBF, 0xBE)
    await test_encode(0x0003FFFF, READY, NONCHAR|HIGHCHAR, 0xF0, 0xBF, 0xBF, 0xBF)
    await test_encode(0x00040000, READY, NORMAL|HIGHCHAR, 0xF1, 0x80, 0x80, 0x80)
    await test_encode(0x0004FFFD, READY, NORMAL|HIGHCHAR, 0xF1, 0x8F, 0xBF, 0xBD)
    await test_encode(0x0004FFFE, READY, NONCHAR|HIGHCHAR, 0xF1, 0x8F, 0xBF, 0xBE)
    await test_encode(0x0004FFFF, READY, NONCHAR|HIGHCHAR, 0xF1, 0x8F, 0xBF, 0xBF)
    await test_encode(0x00050000, READY, NORMAL|HIGHCHAR, 0xF1, 0x90, 0x80, 0x80)
    await test_encode(0x0005FFFD, READY, NORMAL|HIGHCHAR, 0xF1, 0x9F, 0xBF, 0xBD)
    await test_encode(0x0005FFFE, READY, NONCHAR|HIGHCHAR, 0xF1, 0x9F, 0xBF, 0xBE)
    await test_encode(0x0005FFFF, READY, NONCHAR|HIGHCHAR, 0xF1, 0x9F, 0xBF, 0xBF)
    await test_encode(0x00060000, READY, NORMAL|HIGHCHAR, 0xF1, 0xA0, 0x80, 0x80)
    await test_encode(0x0006FFFD, READY, NORMAL|HIGHCHAR, 0xF1, 0xAF, 0xBF, 0xBD)
    await test_encode(0x0006FFFE, READY, NONCHAR|HIGHCHAR, 0xF1, 0xAF, 0xBF, 0xBE)
    await test_encode(0x0006FFFF, READY, NONCHAR|HIGHCHAR, 0xF1, 0xAF, 0xBF, 0xBF)
    await test_encode(0x00070000, READY, NORMAL|HIGHCHAR, 0xF1, 0xB0, 0x80, 0x80)
    await test_encode(0x0007FFFD, READY, NORMAL|HIGHCHAR, 0xF1, 0xBF, 0xBF, 0xBD)
    await test_encode(0x0007FFFE, READY, NONCHAR|HIGHCHAR, 0xF1, 0xBF, 0xBF, 0xBE)
    await test_encode(0x0007FFFF, READY, NONCHAR|HIGHCHAR, 0xF1, 0xBF, 0xBF, 0xBF)
    await test_encode(0x00080000, READY, NORMAL|HIGHCHAR, 0xF2, 0x80, 0x80, 0x80)
    await test_encode(0x0008FFFD, READY, NORMAL|HIGHCHAR, 0xF2, 0x8F, 0xBF, 0xBD)
    await test_encode(0x0008FFFE, READY, NONCHAR|HIGHCHAR, 0xF2, 0x8F, 0xBF, 0xBE)
    await test_encode(0x0008FFFF, READY, NONCHAR|HIGHCHAR, 0xF2, 0x8F, 0xBF, 0xBF)
    await test_encode(0x00090000, READY, NORMAL|HIGHCHAR, 0xF2, 0x90, 0x80, 0x80)
    await test_encode(0x0009FFFD, READY, NORMAL|HIGHCHAR, 0xF2, 0x9F, 0xBF, 0xBD)
    await test_encode(0x0009FFFE, READY, NONCHAR|HIGHCHAR, 0xF2, 0x9F, 0xBF, 0xBE)
    await test_encode(0x0009FFFF, READY, NONCHAR|HIGHCHAR, 0xF2, 0x9F, 0xBF, 0xBF)
    await test_encode(0x000A0000, READY, NORMAL|HIGHCHAR, 0xF2, 0xA0, 0x80, 0x80)
    await test_encode(0x000AFFFD, READY, NORMAL|HIGHCHAR, 0xF2, 0xAF, 0xBF, 0xBD)
    await test_encode(0x000AFFFE, READY, NONCHAR|HIGHCHAR, 0xF2, 0xAF, 0xBF, 0xBE)
    await test_encode(0x000AFFFF, READY, NONCHAR|HIGHCHAR, 0xF2, 0xAF, 0xBF, 0xBF)
    await test_encode(0x000B0000, READY, NORMAL|HIGHCHAR, 0xF2, 0xB0, 0x80, 0x80)
    await test_encode(0x000BFFFD, READY, NORMAL|HIGHCHAR, 0xF2, 0xBF, 0xBF, 0xBD)
    await test_encode(0x000BFFFE, READY, NONCHAR|HIGHCHAR, 0xF2, 0xBF, 0xBF, 0xBE)
    await test_encode(0x000BFFFF, READY, NONCHAR|HIGHCHAR, 0xF2, 0xBF, 0xBF, 0xBF)
    await test_encode(0x000C0000, READY, NORMAL|HIGHCHAR, 0xF3, 0x80, 0x80, 0x80)
    await test_encode(0x000CFFFD, READY, NORMAL|HIGHCHAR, 0xF3, 0x8F, 0xBF, 0xBD)
    await test_encode(0x000CFFFE, READY, NONCHAR|HIGHCHAR, 0xF3, 0x8F, 0xBF, 0xBE)
    await test_encode(0x000CFFFF, READY, NONCHAR|HIGHCHAR, 0xF3, 0x8F, 0xBF, 0xBF)
    await test_encode(0x000D0000, READY, NORMAL|HIGHCHAR, 0xF3, 0x90, 0x80, 0x80)
    await test_encode(0x000DFFFD, READY, NORMAL|HIGHCHAR, 0xF3, 0x9F, 0xBF, 0xBD)
    await test_encode(0x000DFFFE, READY, NONCHAR|HIGHCHAR, 0xF3, 0x9F, 0xBF, 0xBE)
    await test_encode(0x000DFFFF, READY, NONCHAR|HIGHCHAR, 0xF3, 0x9F, 0xBF, 0xBF)
    await test_encode(0x000E0000, READY, NORMAL|HIGHCHAR, 0xF3, 0xA0, 0x80, 0x80)
    await test_encode(0x000EFFFD, READY, NORMAL|HIGHCHAR, 0xF3, 0xAF, 0xBF, 0xBD)
    await test_encode(0x000EFFFE, READY, NONCHAR|HIGHCHAR, 0xF3, 0xAF, 0xBF, 0xBE)
    await test_encode(0x000EFFFF, READY, NONCHAR|HIGHCHAR, 0xF3, 0xAF, 0xBF, 0xBF)
    await test_encode(0x000F0000, READY, PRIVATE|HIGHCHAR, 0xF3, 0xB0, 0x80, 0x80)
    await test_encode(0x000FFFFD, READY, PRIVATE|HIGHCHAR, 0xF3, 0xBF, 0xBF, 0xBD)
    await test_encode(0x000FFFFE, READY, NONCHAR|HIGHCHAR, 0xF3, 0xBF, 0xBF, 0xBE)
    await test_encode(0x000FFFFF, READY, NONCHAR|HIGHCHAR, 0xF3, 0xBF, 0xBF, 0xBF)
    await test_encode(0x00100000, READY, PRIVATE|HIGHCHAR, 0xF4, 0x80, 0x80, 0x80)
    await test_encode(0x0010FFFD, READY, PRIVATE|HIGHCHAR, 0xF4, 0x8F, 0xBF, 0xBD)
    await test_encode(0x0010FFFE, READY, NONCHAR|HIGHCHAR, 0xF4, 0x8F, 0xBF, 0xBE)
    await test_encode(0x0010FFFF, READY, NONCHAR|HIGHCHAR, 0xF4, 0x8F, 0xBF, 0xBF)
    # 4-byte sequence outside of Unicode range
    await test_encode(0x00110000, READY|NONUNI|ERROR, 0, 0xF4, 0x90, 0x80, 0x80)
    await test_encode(0x0011FFFD, READY|NONUNI|ERROR, 0, 0xF4, 0x9F, 0xBF, 0xBD)
    await test_encode(0x0011FFFE, READY|NONUNI|ERROR, 0, 0xF4, 0x9F, 0xBF, 0xBE)
    await test_encode(0x0011FFFF, READY|NONUNI|ERROR, 0, 0xF4, 0x9F, 0xBF, 0xBF)
    await test_encode(0x00120000, READY|NONUNI|ERROR, 0, 0xF4, 0xA0, 0x80, 0x80)
    await test_encode(0x0012FFFD, READY|NONUNI|ERROR, 0, 0xF4, 0xAF, 0xBF, 0xBD)
    await test_encode(0x0012FFFE, READY|NONUNI|ERROR, 0, 0xF4, 0xAF, 0xBF, 0xBE)
    await test_encode(0x0012FFFF, READY|NONUNI|ERROR, 0, 0xF4, 0xAF, 0xBF, 0xBF)
    await test_encode(0x00130000, READY|NONUNI|ERROR, 0, 0xF4, 0xB0, 0x80, 0x80)
    await test_encode(0x0013FFFD, READY|NONUNI|ERROR, 0, 0xF4, 0xBF, 0xBF, 0xBD)
    await test_encode(0x0013FFFE, READY|NONUNI|ERROR, 0, 0xF4, 0xBF, 0xBF, 0xBE)
    await test_encode(0x0013FFFF, READY|NONUNI|ERROR, 0, 0xF4, 0xBF, 0xBF, 0xBF)
    await clear_input(2) # disable range check to allow values 0x110000 and beyond
    await test_encode(0x00110000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF4, 0x90, 0x80, 0x80)
    await test_encode(0x0011FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF4, 0x9F, 0xBF, 0xBD)
    await test_encode(0x0011FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF4, 0x9F, 0xBF, 0xBE)
    await test_encode(0x0011FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF4, 0x9F, 0xBF, 0xBF)
    await test_encode(0x00120000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF4, 0xA0, 0x80, 0x80)
    await test_encode(0x0012FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF4, 0xAF, 0xBF, 0xBD)
    await test_encode(0x0012FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF4, 0xAF, 0xBF, 0xBE)
    await test_encode(0x0012FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF4, 0xAF, 0xBF, 0xBF)
    await test_encode(0x00130000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF4, 0xB0, 0x80, 0x80)
    await test_encode(0x0013FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF4, 0xBF, 0xBF, 0xBD)
    await test_encode(0x0013FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF4, 0xBF, 0xBF, 0xBE)
    await test_encode(0x0013FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF4, 0xBF, 0xBF, 0xBF)
    await test_encode(0x00140000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0x80, 0x80, 0x80)
    await test_encode(0x0014FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0x8F, 0xBF, 0xBD)
    await test_encode(0x0014FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0x8F, 0xBF, 0xBE)
    await test_encode(0x0014FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0x8F, 0xBF, 0xBF)
    await test_encode(0x00150000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0x90, 0x80, 0x80)
    await test_encode(0x0015FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0x9F, 0xBF, 0xBD)
    await test_encode(0x0015FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0x9F, 0xBF, 0xBE)
    await test_encode(0x0015FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0x9F, 0xBF, 0xBF)
    await test_encode(0x00160000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0xA0, 0x80, 0x80)
    await test_encode(0x0016FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0xAF, 0xBF, 0xBD)
    await test_encode(0x0016FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0xAF, 0xBF, 0xBE)
    await test_encode(0x0016FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0xAF, 0xBF, 0xBF)
    await test_encode(0x00170000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0xB0, 0x80, 0x80)
    await test_encode(0x0017FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0xBF, 0xBF, 0xBD)
    await test_encode(0x0017FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0xBF, 0xBF, 0xBE)
    await test_encode(0x0017FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0xBF, 0xBF, 0xBF)
    await test_encode(0x00180000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0x80, 0x80, 0x80)
    await test_encode(0x0018FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0x8F, 0xBF, 0xBD)
    await test_encode(0x0018FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0x8F, 0xBF, 0xBE)
    await test_encode(0x0018FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0x8F, 0xBF, 0xBF)
    await test_encode(0x00190000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0x90, 0x80, 0x80)
    await test_encode(0x0019FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0x9F, 0xBF, 0xBD)
    await test_encode(0x0019FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0x9F, 0xBF, 0xBE)
    await test_encode(0x0019FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0x9F, 0xBF, 0xBF)
    await test_encode(0x001A0000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0xA0, 0x80, 0x80)
    await test_encode(0x001AFFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0xAF, 0xBF, 0xBD)
    await test_encode(0x001AFFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0xAF, 0xBF, 0xBE)
    await test_encode(0x001AFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0xAF, 0xBF, 0xBF)
    await test_encode(0x001B0000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0xB0, 0x80, 0x80)
    await test_encode(0x001BFFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0xBF, 0xBF, 0xBD)
    await test_encode(0x001BFFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0xBF, 0xBF, 0xBE)
    await test_encode(0x001BFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0xBF, 0xBF, 0xBF)
    await test_encode(0x001C0000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0x80, 0x80, 0x80)
    await test_encode(0x001CFFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0x8F, 0xBF, 0xBD)
    await test_encode(0x001CFFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0x8F, 0xBF, 0xBE)
    await test_encode(0x001CFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0x8F, 0xBF, 0xBF)
    await test_encode(0x001D0000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0x90, 0x80, 0x80)
    await test_encode(0x001DFFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0x9F, 0xBF, 0xBD)
    await test_encode(0x001DFFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0x9F, 0xBF, 0xBE)
    await test_encode(0x001DFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0x9F, 0xBF, 0xBF)
    await test_encode(0x001E0000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0xA0, 0x80, 0x80)
    await test_encode(0x001EFFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0xAF, 0xBF, 0xBD)
    await test_encode(0x001EFFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0xAF, 0xBF, 0xBE)
    await test_encode(0x001EFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0xAF, 0xBF, 0xBF)
    await test_encode(0x001F0000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0xB0, 0x80, 0x80)
    await test_encode(0x001FFFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0xBF, 0xBF, 0xBD)
    await test_encode(0x001FFFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0xBF, 0xBF, 0xBE)
    await test_encode(0x001FFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0xBF, 0xBF, 0xBF)
    await test_encode(0x00200000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF8, 0x88, 0x80, 0x80, 0x80) # 5-byte sequence
    await test_encode(0x03FFFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xFB, 0xBF, 0xBF, 0xBF, 0xBF) # 5-byte sequence
    await test_encode(0x04000000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xFC, 0x84, 0x80, 0x80, 0x80, 0x80) # 6-byte sequence
    await test_encode(0x7FFFFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xFD, 0xBF, 0xBF, 0xBF, 0xBF, 0xBF) # 6-byte sequence
    await test_encode(0x80000000, READY|INVALID|ERROR, 0) # gap - impossible decoder output
    await test_encode(0xEFFFFFFF, READY|INVALID|ERROR, 0) # gap - impossible decoder output
    await test_encode(0xF0000000, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x80, 0x80) # 6-byte overlong encoding of 1-byte sequence
    await test_encode(0xF000007F, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x81, 0xBF) # 6-byte overlong encoding of 1-byte sequence
    await test_encode(0xF0000080, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x82, 0x80) # 6-byte overlong encoding of 2-byte sequence
    await test_encode(0xF00007FF, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x9F, 0xBF) # 6-byte overlong encoding of 2-byte sequence
    await test_encode(0xF0000800, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0xA0, 0x80) # 6-byte overlong encoding of 3-byte sequence
    await test_encode(0xF000FFFF, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x8F, 0xBF, 0xBF) # 6-byte overlong encoding of 3-byte sequence
    await set_input(2) # reënable range check
    await test_encode(0x00200000, READY|NONUNI|ERROR, 0, 0xF8, 0x88, 0x80, 0x80, 0x80) # 5-byte sequence
    await test_encode(0x03FFFFFF, READY|NONUNI|ERROR, 0, 0xFB, 0xBF, 0xBF, 0xBF, 0xBF) # 5-byte sequence
    await test_encode(0x04000000, READY|NONUNI|ERROR, 0, 0xFC, 0x84, 0x80, 0x80, 0x80, 0x80) # 6-byte sequence
    await test_encode(0x7FFFFFFF, READY|NONUNI|ERROR, 0, 0xFD, 0xBF, 0xBF, 0xBF, 0xBF, 0xBF) # 6-byte sequence
    await test_encode(0x80000000, READY|INVALID|ERROR, 0) # gap - impossible decoder output
    await test_encode(0xEFFFFFFF, READY|INVALID|ERROR, 0) # gap - impossible decoder output
    await test_encode(0xF0000000, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x80, 0x80) # 6-byte overlong encoding of 1-byte sequence
    await test_encode(0xF000007F, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x81, 0xBF) # 6-byte overlong encoding of 1-byte sequence
    await test_encode(0xF0000080, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x82, 0x80) # 6-byte overlong encoding of 2-byte sequence
    await test_encode(0xF00007FF, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x9F, 0xBF) # 6-byte overlong encoding of 2-byte sequence
    await test_encode(0xF0000800, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0xA0, 0x80) # 6-byte overlong encoding of 3-byte sequence
    await test_encode(0xF000FFFF, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x8F, 0xBF, 0xBF) # 6-byte overlong encoding of 3-byte sequence
    await test_encode(0xF0010000, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x90, 0x80, 0x80) # 6-byte overlong encoding of 4-byte sequence
    await test_encode(0xF01FFFFF, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x87, 0xBF, 0xBF, 0xBF) # 6-byte overlong encoding of 4-byte sequence
    await test_encode(0xF0200000, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x88, 0x80, 0x80, 0x80) # 6-byte overlong encoding of 5-byte sequence
    await test_encode(0xF3FFFFFF, READY|OVERLONG|ERROR, 0, 0xFC, 0x83, 0xBF, 0xBF, 0xBF, 0xBF) # 6-byte overlong encoding of 5-byte sequence
    await test_encode(0xF4000000, READY|INVALID|ERROR, 0, 0xFC, 0x84, 0x80, 0x80, 0x80, 0x80) # 6-byte unmasked encoding - impossible decoder output
    await test_encode(0xF7FFFFFF, READY|INVALID|ERROR, 0, 0xFC, 0x87, 0xBF, 0xBF, 0xBF, 0xBF) # 6-byte unmasked encoding - impossible decoder output
    await test_encode(0xF8000000, READY|OVERLONG|ERROR, 0, 0xF8, 0x80, 0x80, 0x80, 0x80) # 5-byte overlong encoding of 1-byte sequence
    await test_encode(0xF800007F, READY|OVERLONG|ERROR, 0, 0xF8, 0x80, 0x80, 0x81, 0xBF) # 5-byte overlong encoding of 1-byte sequence
    await test_encode(0xF8000080, READY|OVERLONG|ERROR, 0, 0xF8, 0x80, 0x80, 0x82, 0x80) # 5-byte overlong encoding of 2-byte sequence
    await test_encode(0xF80007FF, READY|OVERLONG|ERROR, 0, 0xF8, 0x80, 0x80, 0x9F, 0xBF) # 5-byte overlong encoding of 2-byte sequence
    await test_encode(0xF8000800, READY|OVERLONG|ERROR, 0, 0xF8, 0x80, 0x80, 0xA0, 0x80) # 5-byte overlong encoding of 3-byte sequence
    await test_encode(0xF800FFFF, READY|OVERLONG|ERROR, 0, 0xF8, 0x80, 0x8F, 0xBF, 0xBF) # 5-byte overlong encoding of 3-byte sequence
    await test_encode(0xF8010000, READY|OVERLONG|ERROR, 0, 0xF8, 0x80, 0x90, 0x80, 0x80) # 5-byte overlong encoding of 4-byte sequence
    await test_encode(0xF81FFFFF, READY|OVERLONG|ERROR, 0, 0xF8, 0x87, 0xBF, 0xBF, 0xBF) # 5-byte overlong encoding of 4-byte sequence
    await test_encode(0xF8200000, READY|INVALID|ERROR, 0, 0xF8, 0x88, 0x80, 0x80, 0x80) # 5-byte unmasked encoding - impossible decoder output
    await test_encode(0xFBFFFFFF, READY|INVALID|ERROR, 0, 0xFB, 0xBF, 0xBF, 0xBF, 0xBF) # 5-byte unmasked encoding - impossible decoder output
    await test_encode(0xFC000000, UNDERFLOW, 0, 0xFC, 0x80, 0x80, 0x80, 0x80) # 5-byte truncation of 6-byte sequence
    await test_encode(0xFDFFFFFF, UNDERFLOW, 0, 0xFD, 0xBF, 0xBF, 0xBF, 0xBF) # 5-byte truncation of 6-byte sequence
    await test_encode(0xFE000000, READY|INVALID|ERROR, 0, 0xFE, 0x80, 0x80, 0x80, 0x80) # gap - impossible decoder input, impossible decoder output
    await test_encode(0xFFBFFFFF, READY|INVALID|ERROR, 0, 0xFF, 0xAF, 0xBF, 0xBF, 0xBF) # gap - impossible decoder input, impossible decoder output
    await test_encode(0xFFC00000, READY|OVERLONG|ERROR, 0, 0xF0, 0x80, 0x80, 0x80) # 4-byte overlong encoding of 1-byte sequence
    await test_encode(0xFFC0007F, READY|OVERLONG|ERROR, 0, 0xF0, 0x80, 0x81, 0xBF) # 4-byte overlong encoding of 1-byte sequence
    await test_encode(0xFFC00080, READY|OVERLONG|ERROR, 0, 0xF0, 0x80, 0x82, 0x80) # 4-byte overlong encoding of 2-byte sequence
    await test_encode(0xFFC007FF, READY|OVERLONG|ERROR, 0, 0xF0, 0x80, 0x9F, 0xBF) # 4-byte overlong encoding of 2-byte sequence
    await test_encode(0xFFC00800, READY|OVERLONG|ERROR, 0, 0xF0, 0x80, 0xA0, 0x80) # 4-byte overlong encoding of 3-byte sequence
    await test_encode(0xFFC0FFFF, READY|OVERLONG|ERROR, 0, 0xF0, 0x8F, 0xBF, 0xBF) # 4-byte overlong encoding of 3-byte sequence
    await test_encode(0xFFC10000, READY|INVALID|ERROR, 0, 0xF0, 0x90, 0x80, 0x80) # 4-byte unmasked encoding - impossible decoder output
    await test_encode(0xFFDFFFFF, READY|INVALID|ERROR, 0, 0xF7, 0xBF, 0xBF, 0xBF) # 4-byte unmasked encoding - impossible decoder output
    await test_encode(0xFFE00000, UNDERFLOW, 0, 0xF8, 0x80, 0x80, 0x80) # 4-byte truncation of 5-byte sequence
    await test_encode(0xFFEFFFFF, UNDERFLOW, 0, 0xFB, 0xBF, 0xBF, 0xBF) # 4-byte truncation of 5-byte sequence
    await test_encode(0xFFF00000, UNDERFLOW, 0, 0xFC, 0x80, 0x80, 0x80) # 4-byte truncation of 6-byte sequence
    await test_encode(0xFFF7FFFF, UNDERFLOW, 0, 0xFD, 0xBF, 0xBF, 0xBF) # 4-byte truncation of 6-byte sequence
    await test_encode(0xFFF80000, READY|INVALID|ERROR, 0, 0xFE, 0x80, 0x80, 0x80) # gap - impossible decoder input, impossible decoder output
    await test_encode(0xFFFDFFFF, READY|INVALID|ERROR, 0, 0xFF, 0x9F, 0xBF, 0xBF) # gap - impossible decoder input, impossible decoder output
    await test_encode(0xFFFE0000, READY|OVERLONG|ERROR, 0, 0xE0, 0x80, 0x80) # 3-byte overlong encoding of 1-byte sequence
    await test_encode(0xFFFE007F, READY|OVERLONG|ERROR, 0, 0xE0, 0x81, 0xBF) # 3-byte overlong encoding of 1-byte sequence
    await test_encode(0xFFFE0080, READY|OVERLONG|ERROR, 0, 0xE0, 0x82, 0x80) # 3-byte overlong encoding of 2-byte sequence
    await test_encode(0xFFFE07FF, READY|OVERLONG|ERROR, 0, 0xE0, 0x9F, 0xBF) # 3-byte overlong encoding of 2-byte sequence
    await test_encode(0xFFFE0800, READY|INVALID|ERROR, 0, 0xE0, 0xA0, 0x80) # 3-byte unmasked encoding - impossible decoder output
    await test_encode(0xFFFEFFFF, READY|INVALID|ERROR, 0, 0xEF, 0xBF, 0xBF) # 3-byte unmasked encoding - impossible decoder output
    await test_encode(0xFFFF0000, UNDERFLOW, 0, 0xF0, 0x80, 0x80) # 3-byte truncation of 4-byte sequence
    await test_encode(0xFFFF7FFF, UNDERFLOW, 0, 0xF7, 0xBF, 0xBF) # 3-byte truncation of 4-byte sequence
    await test_encode(0xFFFF8000, UNDERFLOW, 0, 0xF8, 0x80, 0x80) # 3-byte truncation of 5-byte sequence
    await test_encode(0xFFFFBFFF, UNDERFLOW, 0, 0xFB, 0xBF, 0xBF) # 3-byte truncation of 5-byte sequence
    await test_encode(0xFFFFC000, UNDERFLOW, 0, 0xFC, 0x80, 0x80) # 3-byte truncation of 6-byte sequence
    await test_encode(0xFFFFDFFF, UNDERFLOW, 0, 0xFD, 0xBF, 0xBF) # 3-byte truncation of 6-byte sequence
    await test_encode(0xFFFFE000, READY|INVALID|ERROR, 0, 0xFE, 0x80, 0x80) # gap - impossible decoder input, impossible decoder output
    await test_encode(0xFFFFEFFF, READY|INVALID|ERROR, 0, 0xFE, 0xBF, 0xBF) # gap - impossible decoder input, impossible decoder output
    await test_encode(0xFFFFF000, READY|OVERLONG|ERROR, 0, 0xC0, 0x80) # 2-byte overlong encoding of 1-byte sequence
    await test_encode(0xFFFFF07F, READY|OVERLONG|ERROR, 0, 0xC1, 0xBF) # 2-byte overlong encoding of 1-byte sequence
    await test_encode(0xFFFFF080, READY|INVALID|ERROR, 0, 0xC2, 0x80) # 2-byte unmasked encoding - impossible decoder output
    await test_encode(0xFFFFF7FF, READY|INVALID|ERROR, 0, 0xDF, 0xBF) # 2-byte unmasked encoding - impossible decoder output
    await test_encode(0xFFFFF800, UNDERFLOW, 0, 0xE0, 0x80) # 2-byte truncation of 3-byte sequence
    await test_encode(0xFFFFFBFF, UNDERFLOW, 0, 0xEF, 0xBF) # 2-byte truncation of 3-byte sequence
    await test_encode(0xFFFFFC00, UNDERFLOW, 0, 0xF0, 0x80) # 2-byte truncation of 4-byte sequence
    await test_encode(0xFFFFFDFF, UNDERFLOW, 0, 0xF7, 0xBF) # 2-byte truncation of 4-byte sequence
    await test_encode(0xFFFFFE00, UNDERFLOW, 0, 0xF8, 0x80) # 2-byte truncation of 5-byte sequence
    await test_encode(0xFFFFFEFF, UNDERFLOW, 0, 0xFB, 0xBF) # 2-byte truncation of 5-byte sequence
    await test_encode(0xFFFFFF00, UNDERFLOW, 0, 0xFC, 0x80) # 2-byte truncation of 6-byte sequence
    await test_encode(0xFFFFFF7F, UNDERFLOW, 0, 0xFD, 0xBF) # 2-byte truncation of 6-byte sequence
    await test_encode(0xFFFFFF80, READY|INVALID|ERROR, 0, 0x80) # lone trailing byte
    await test_encode(0xFFFFFFBF, READY|INVALID|ERROR, 0, 0xBF) # lone trailing byte
    await test_encode(0xFFFFFFC0, UNDERFLOW, 0, 0xC0) # lone leading byte of 2-byte sequence
    await test_encode(0xFFFFFFDF, UNDERFLOW, 0, 0xDF) # lone leading byte of 2-byte sequence
    await test_encode(0xFFFFFFE0, UNDERFLOW, 0, 0xE0) # lone leading byte of 3-byte sequence
    await test_encode(0xFFFFFFEF, UNDERFLOW, 0, 0xEF) # lone leading byte of 3-byte sequence
    await test_encode(0xFFFFFFF0, UNDERFLOW, 0, 0xF0) # lone leading byte of 4-byte sequence
    await test_encode(0xFFFFFFF7, UNDERFLOW, 0, 0xF7) # lone leading byte of 4-byte sequence
    await test_encode(0xFFFFFFF8, UNDERFLOW, 0, 0xF8) # lone leading byte of 5-byte sequence
    await test_encode(0xFFFFFFFB, UNDERFLOW, 0, 0xFB) # lone leading byte of 5-byte sequence
    await test_encode(0xFFFFFFFC, UNDERFLOW, 0, 0xFC) # lone leading byte of 6-byte sequence
    await test_encode(0xFFFFFFFD, UNDERFLOW, 0, 0xFD) # lone leading byte of 6-byte sequence
    await test_encode(0xFFFFFFFE, READY|INVALID|ERROR, 0, 0xFE) # lone invalid byte
    await test_encode(0xFFFFFFFF, READY|INVALID|ERROR, 0, 0xFF) # lone invalid byte

    # UTF-8 decoding

    global td_pad
    td_pad = 0

    async def test_decode(cp, errs, props, *args):
        global td_pad
        await write_bytes(*args)
        await want_errs(errs)
        await want_props(props)
        await read_cp(cp)
        await read_reset()
        await write_bytes(td_pad)
        if errs or td_pad < 0x80 or td_pad >= 0xC0:
            await want_errs(errs|RETRY|ERROR)
            await want_props(props)
            await read_cp(cp)
        else:
            await want_retry(0)
        await write_reset()
        td_pad = (td_pad + 0x33) & 0xFF

    # ASCII
    await test_decode(0x00000000, READY, CONTROL, 0x00)
    await test_decode(0x00000001, READY, CONTROL, 0x01)
    await test_decode(0x0000001F, READY, CONTROL, 0x1F)
    await test_decode(0x00000020, READY, NORMAL, 0x20)
    await test_decode(0x0000007E, READY, NORMAL, 0x7E)
    await test_decode(0x0000007F, READY, CONTROL, 0x7F)
    # 2-byte sequence
    await test_decode(0x00000080, READY, CONTROL, 0xC2, 0x80)
    await test_decode(0x0000009F, READY, CONTROL, 0xC2, 0x9F)
    await test_decode(0x000000A0, READY, NORMAL, 0xC2, 0xA0)
    await test_decode(0x000000FF, READY, NORMAL, 0xC3, 0xBF)
    await test_decode(0x00000100, READY, NORMAL, 0xC4, 0x80)
    await test_decode(0x000007FF, READY, NORMAL, 0xDF, 0xBF)
    # 3-byte sequence
    await test_decode(0x00000800, READY, NORMAL, 0xE0, 0xA0, 0x80)
    await test_decode(0x0000D7FF, READY, NORMAL, 0xED, 0x9F, 0xBF)
    await test_decode(0x0000D800, READY, SURROGATE|HIGHCHAR, 0xED, 0xA0, 0x80)
    await test_decode(0x0000DB7F, READY, SURROGATE|HIGHCHAR, 0xED, 0xAD, 0xBF)
    await test_decode(0x0000DB80, READY, SURROGATE|HIGHCHAR|PRIVATE, 0xED, 0xAE, 0x80)
    await test_decode(0x0000DBFF, READY, SURROGATE|HIGHCHAR|PRIVATE, 0xED, 0xAF, 0xBF)
    await test_decode(0x0000DC00, READY, SURROGATE, 0xED, 0xB0, 0x80)
    await test_decode(0x0000DFFF, READY, SURROGATE, 0xED, 0xBF, 0xBF)
    await test_decode(0x0000E000, READY, PRIVATE, 0xEE, 0x80, 0x80)
    await test_decode(0x0000F8FF, READY, PRIVATE, 0xEF, 0xA3, 0xBF)
    await test_decode(0x0000F900, READY, NORMAL, 0xEF, 0xA4, 0x80)
    await test_decode(0x0000FDCF, READY, NORMAL, 0xEF, 0xB7, 0x8F)
    await test_decode(0x0000FDD0, READY, NONCHAR, 0xEF, 0xB7, 0x90)
    await test_decode(0x0000FDEF, READY, NONCHAR, 0xEF, 0xB7, 0xAF)
    await test_decode(0x0000FDF0, READY, NORMAL, 0xEF, 0xB7, 0xB0)
    await test_decode(0x0000FFFD, READY, NORMAL, 0xEF, 0xBF, 0xBD)
    await test_decode(0x0000FFFE, READY, NONCHAR, 0xEF, 0xBF, 0xBE)
    await test_decode(0x0000FFFF, READY, NONCHAR, 0xEF, 0xBF, 0xBF)
    # 4-byte sequence
    await test_decode(0x00010000, READY, NORMAL|HIGHCHAR, 0xF0, 0x90, 0x80, 0x80)
    await test_decode(0x0001FFFD, READY, NORMAL|HIGHCHAR, 0xF0, 0x9F, 0xBF, 0xBD)
    await test_decode(0x0001FFFE, READY, NONCHAR|HIGHCHAR, 0xF0, 0x9F, 0xBF, 0xBE)
    await test_decode(0x0001FFFF, READY, NONCHAR|HIGHCHAR, 0xF0, 0x9F, 0xBF, 0xBF)
    await test_decode(0x00020000, READY, NORMAL|HIGHCHAR, 0xF0, 0xA0, 0x80, 0x80)
    await test_decode(0x0002FFFD, READY, NORMAL|HIGHCHAR, 0xF0, 0xAF, 0xBF, 0xBD)
    await test_decode(0x0002FFFE, READY, NONCHAR|HIGHCHAR, 0xF0, 0xAF, 0xBF, 0xBE)
    await test_decode(0x0002FFFF, READY, NONCHAR|HIGHCHAR, 0xF0, 0xAF, 0xBF, 0xBF)
    await test_decode(0x00030000, READY, NORMAL|HIGHCHAR, 0xF0, 0xB0, 0x80, 0x80)
    await test_decode(0x0003FFFD, READY, NORMAL|HIGHCHAR, 0xF0, 0xBF, 0xBF, 0xBD)
    await test_decode(0x0003FFFE, READY, NONCHAR|HIGHCHAR, 0xF0, 0xBF, 0xBF, 0xBE)
    await test_decode(0x0003FFFF, READY, NONCHAR|HIGHCHAR, 0xF0, 0xBF, 0xBF, 0xBF)
    await test_decode(0x00040000, READY, NORMAL|HIGHCHAR, 0xF1, 0x80, 0x80, 0x80)
    await test_decode(0x0004FFFD, READY, NORMAL|HIGHCHAR, 0xF1, 0x8F, 0xBF, 0xBD)
    await test_decode(0x0004FFFE, READY, NONCHAR|HIGHCHAR, 0xF1, 0x8F, 0xBF, 0xBE)
    await test_decode(0x0004FFFF, READY, NONCHAR|HIGHCHAR, 0xF1, 0x8F, 0xBF, 0xBF)
    await test_decode(0x00050000, READY, NORMAL|HIGHCHAR, 0xF1, 0x90, 0x80, 0x80)
    await test_decode(0x0005FFFD, READY, NORMAL|HIGHCHAR, 0xF1, 0x9F, 0xBF, 0xBD)
    await test_decode(0x0005FFFE, READY, NONCHAR|HIGHCHAR, 0xF1, 0x9F, 0xBF, 0xBE)
    await test_decode(0x0005FFFF, READY, NONCHAR|HIGHCHAR, 0xF1, 0x9F, 0xBF, 0xBF)
    await test_decode(0x00060000, READY, NORMAL|HIGHCHAR, 0xF1, 0xA0, 0x80, 0x80)
    await test_decode(0x0006FFFD, READY, NORMAL|HIGHCHAR, 0xF1, 0xAF, 0xBF, 0xBD)
    await test_decode(0x0006FFFE, READY, NONCHAR|HIGHCHAR, 0xF1, 0xAF, 0xBF, 0xBE)
    await test_decode(0x0006FFFF, READY, NONCHAR|HIGHCHAR, 0xF1, 0xAF, 0xBF, 0xBF)
    await test_decode(0x00070000, READY, NORMAL|HIGHCHAR, 0xF1, 0xB0, 0x80, 0x80)
    await test_decode(0x0007FFFD, READY, NORMAL|HIGHCHAR, 0xF1, 0xBF, 0xBF, 0xBD)
    await test_decode(0x0007FFFE, READY, NONCHAR|HIGHCHAR, 0xF1, 0xBF, 0xBF, 0xBE)
    await test_decode(0x0007FFFF, READY, NONCHAR|HIGHCHAR, 0xF1, 0xBF, 0xBF, 0xBF)
    await test_decode(0x00080000, READY, NORMAL|HIGHCHAR, 0xF2, 0x80, 0x80, 0x80)
    await test_decode(0x0008FFFD, READY, NORMAL|HIGHCHAR, 0xF2, 0x8F, 0xBF, 0xBD)
    await test_decode(0x0008FFFE, READY, NONCHAR|HIGHCHAR, 0xF2, 0x8F, 0xBF, 0xBE)
    await test_decode(0x0008FFFF, READY, NONCHAR|HIGHCHAR, 0xF2, 0x8F, 0xBF, 0xBF)
    await test_decode(0x00090000, READY, NORMAL|HIGHCHAR, 0xF2, 0x90, 0x80, 0x80)
    await test_decode(0x0009FFFD, READY, NORMAL|HIGHCHAR, 0xF2, 0x9F, 0xBF, 0xBD)
    await test_decode(0x0009FFFE, READY, NONCHAR|HIGHCHAR, 0xF2, 0x9F, 0xBF, 0xBE)
    await test_decode(0x0009FFFF, READY, NONCHAR|HIGHCHAR, 0xF2, 0x9F, 0xBF, 0xBF)
    await test_decode(0x000A0000, READY, NORMAL|HIGHCHAR, 0xF2, 0xA0, 0x80, 0x80)
    await test_decode(0x000AFFFD, READY, NORMAL|HIGHCHAR, 0xF2, 0xAF, 0xBF, 0xBD)
    await test_decode(0x000AFFFE, READY, NONCHAR|HIGHCHAR, 0xF2, 0xAF, 0xBF, 0xBE)
    await test_decode(0x000AFFFF, READY, NONCHAR|HIGHCHAR, 0xF2, 0xAF, 0xBF, 0xBF)
    await test_decode(0x000B0000, READY, NORMAL|HIGHCHAR, 0xF2, 0xB0, 0x80, 0x80)
    await test_decode(0x000BFFFD, READY, NORMAL|HIGHCHAR, 0xF2, 0xBF, 0xBF, 0xBD)
    await test_decode(0x000BFFFE, READY, NONCHAR|HIGHCHAR, 0xF2, 0xBF, 0xBF, 0xBE)
    await test_decode(0x000BFFFF, READY, NONCHAR|HIGHCHAR, 0xF2, 0xBF, 0xBF, 0xBF)
    await test_decode(0x000C0000, READY, NORMAL|HIGHCHAR, 0xF3, 0x80, 0x80, 0x80)
    await test_decode(0x000CFFFD, READY, NORMAL|HIGHCHAR, 0xF3, 0x8F, 0xBF, 0xBD)
    await test_decode(0x000CFFFE, READY, NONCHAR|HIGHCHAR, 0xF3, 0x8F, 0xBF, 0xBE)
    await test_decode(0x000CFFFF, READY, NONCHAR|HIGHCHAR, 0xF3, 0x8F, 0xBF, 0xBF)
    await test_decode(0x000D0000, READY, NORMAL|HIGHCHAR, 0xF3, 0x90, 0x80, 0x80)
    await test_decode(0x000DFFFD, READY, NORMAL|HIGHCHAR, 0xF3, 0x9F, 0xBF, 0xBD)
    await test_decode(0x000DFFFE, READY, NONCHAR|HIGHCHAR, 0xF3, 0x9F, 0xBF, 0xBE)
    await test_decode(0x000DFFFF, READY, NONCHAR|HIGHCHAR, 0xF3, 0x9F, 0xBF, 0xBF)
    await test_decode(0x000E0000, READY, NORMAL|HIGHCHAR, 0xF3, 0xA0, 0x80, 0x80)
    await test_decode(0x000EFFFD, READY, NORMAL|HIGHCHAR, 0xF3, 0xAF, 0xBF, 0xBD)
    await test_decode(0x000EFFFE, READY, NONCHAR|HIGHCHAR, 0xF3, 0xAF, 0xBF, 0xBE)
    await test_decode(0x000EFFFF, READY, NONCHAR|HIGHCHAR, 0xF3, 0xAF, 0xBF, 0xBF)
    await test_decode(0x000F0000, READY, PRIVATE|HIGHCHAR, 0xF3, 0xB0, 0x80, 0x80)
    await test_decode(0x000FFFFD, READY, PRIVATE|HIGHCHAR, 0xF3, 0xBF, 0xBF, 0xBD)
    await test_decode(0x000FFFFE, READY, NONCHAR|HIGHCHAR, 0xF3, 0xBF, 0xBF, 0xBE)
    await test_decode(0x000FFFFF, READY, NONCHAR|HIGHCHAR, 0xF3, 0xBF, 0xBF, 0xBF)
    await test_decode(0x00100000, READY, PRIVATE|HIGHCHAR, 0xF4, 0x80, 0x80, 0x80)
    await test_decode(0x0010FFFD, READY, PRIVATE|HIGHCHAR, 0xF4, 0x8F, 0xBF, 0xBD)
    await test_decode(0x0010FFFE, READY, NONCHAR|HIGHCHAR, 0xF4, 0x8F, 0xBF, 0xBE)
    await test_decode(0x0010FFFF, READY, NONCHAR|HIGHCHAR, 0xF4, 0x8F, 0xBF, 0xBF)
    # 4-byte sequence outside of Unicode range
    await test_decode(0x00110000, READY|NONUNI|ERROR, 0, 0xF4, 0x90, 0x80, 0x80)
    await test_decode(0x0011FFFD, READY|NONUNI|ERROR, 0, 0xF4, 0x9F, 0xBF, 0xBD)
    await test_decode(0x0011FFFE, READY|NONUNI|ERROR, 0, 0xF4, 0x9F, 0xBF, 0xBE)
    await test_decode(0x0011FFFF, READY|NONUNI|ERROR, 0, 0xF4, 0x9F, 0xBF, 0xBF)
    await test_decode(0x00120000, READY|NONUNI|ERROR, 0, 0xF4, 0xA0, 0x80, 0x80)
    await test_decode(0x0012FFFD, READY|NONUNI|ERROR, 0, 0xF4, 0xAF, 0xBF, 0xBD)
    await test_decode(0x0012FFFE, READY|NONUNI|ERROR, 0, 0xF4, 0xAF, 0xBF, 0xBE)
    await test_decode(0x0012FFFF, READY|NONUNI|ERROR, 0, 0xF4, 0xAF, 0xBF, 0xBF)
    await test_decode(0x00130000, READY|NONUNI|ERROR, 0, 0xF4, 0xB0, 0x80, 0x80)
    await test_decode(0x0013FFFD, READY|NONUNI|ERROR, 0, 0xF4, 0xBF, 0xBF, 0xBD)
    await test_decode(0x0013FFFE, READY|NONUNI|ERROR, 0, 0xF4, 0xBF, 0xBF, 0xBE)
    await test_decode(0x0013FFFF, READY|NONUNI|ERROR, 0, 0xF4, 0xBF, 0xBF, 0xBF)
    await clear_input(2) # disable range check to allow values 0x110000 and beyond
    await test_decode(0x00110000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF4, 0x90, 0x80, 0x80)
    await test_decode(0x0011FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF4, 0x9F, 0xBF, 0xBD)
    await test_decode(0x0011FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF4, 0x9F, 0xBF, 0xBE)
    await test_decode(0x0011FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF4, 0x9F, 0xBF, 0xBF)
    await test_decode(0x00120000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF4, 0xA0, 0x80, 0x80)
    await test_decode(0x0012FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF4, 0xAF, 0xBF, 0xBD)
    await test_decode(0x0012FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF4, 0xAF, 0xBF, 0xBE)
    await test_decode(0x0012FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF4, 0xAF, 0xBF, 0xBF)
    await test_decode(0x00130000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF4, 0xB0, 0x80, 0x80)
    await test_decode(0x0013FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF4, 0xBF, 0xBF, 0xBD)
    await test_decode(0x0013FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF4, 0xBF, 0xBF, 0xBE)
    await test_decode(0x0013FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF4, 0xBF, 0xBF, 0xBF)
    await test_decode(0x00140000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0x80, 0x80, 0x80)
    await test_decode(0x0014FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0x8F, 0xBF, 0xBD)
    await test_decode(0x0014FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0x8F, 0xBF, 0xBE)
    await test_decode(0x0014FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0x8F, 0xBF, 0xBF)
    await test_decode(0x00150000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0x90, 0x80, 0x80)
    await test_decode(0x0015FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0x9F, 0xBF, 0xBD)
    await test_decode(0x0015FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0x9F, 0xBF, 0xBE)
    await test_decode(0x0015FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0x9F, 0xBF, 0xBF)
    await test_decode(0x00160000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0xA0, 0x80, 0x80)
    await test_decode(0x0016FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0xAF, 0xBF, 0xBD)
    await test_decode(0x0016FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0xAF, 0xBF, 0xBE)
    await test_decode(0x0016FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0xAF, 0xBF, 0xBF)
    await test_decode(0x00170000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0xB0, 0x80, 0x80)
    await test_decode(0x0017FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF5, 0xBF, 0xBF, 0xBD)
    await test_decode(0x0017FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0xBF, 0xBF, 0xBE)
    await test_decode(0x0017FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF5, 0xBF, 0xBF, 0xBF)
    await test_decode(0x00180000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0x80, 0x80, 0x80)
    await test_decode(0x0018FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0x8F, 0xBF, 0xBD)
    await test_decode(0x0018FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0x8F, 0xBF, 0xBE)
    await test_decode(0x0018FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0x8F, 0xBF, 0xBF)
    await test_decode(0x00190000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0x90, 0x80, 0x80)
    await test_decode(0x0019FFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0x9F, 0xBF, 0xBD)
    await test_decode(0x0019FFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0x9F, 0xBF, 0xBE)
    await test_decode(0x0019FFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0x9F, 0xBF, 0xBF)
    await test_decode(0x001A0000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0xA0, 0x80, 0x80)
    await test_decode(0x001AFFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0xAF, 0xBF, 0xBD)
    await test_decode(0x001AFFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0xAF, 0xBF, 0xBE)
    await test_decode(0x001AFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0xAF, 0xBF, 0xBF)
    await test_decode(0x001B0000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0xB0, 0x80, 0x80)
    await test_decode(0x001BFFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF6, 0xBF, 0xBF, 0xBD)
    await test_decode(0x001BFFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0xBF, 0xBF, 0xBE)
    await test_decode(0x001BFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF6, 0xBF, 0xBF, 0xBF)
    await test_decode(0x001C0000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0x80, 0x80, 0x80)
    await test_decode(0x001CFFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0x8F, 0xBF, 0xBD)
    await test_decode(0x001CFFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0x8F, 0xBF, 0xBE)
    await test_decode(0x001CFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0x8F, 0xBF, 0xBF)
    await test_decode(0x001D0000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0x90, 0x80, 0x80)
    await test_decode(0x001DFFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0x9F, 0xBF, 0xBD)
    await test_decode(0x001DFFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0x9F, 0xBF, 0xBE)
    await test_decode(0x001DFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0x9F, 0xBF, 0xBF)
    await test_decode(0x001E0000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0xA0, 0x80, 0x80)
    await test_decode(0x001EFFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0xAF, 0xBF, 0xBD)
    await test_decode(0x001EFFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0xAF, 0xBF, 0xBE)
    await test_decode(0x001EFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0xAF, 0xBF, 0xBF)
    await test_decode(0x001F0000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0xB0, 0x80, 0x80)
    await test_decode(0x001FFFFD, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF7, 0xBF, 0xBF, 0xBD)
    await test_decode(0x001FFFFE, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0xBF, 0xBF, 0xBE)
    await test_decode(0x001FFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xF7, 0xBF, 0xBF, 0xBF)
    await test_decode(0x00200000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xF8, 0x88, 0x80, 0x80, 0x80) # 5-byte sequence
    await test_decode(0x03FFFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xFB, 0xBF, 0xBF, 0xBF, 0xBF) # 5-byte sequence
    await test_decode(0x04000000, READY|NONUNI, PRIVATE|HIGHCHAR, 0xFC, 0x84, 0x80, 0x80, 0x80, 0x80) # 6-byte sequence
    await test_decode(0x7FFFFFFF, READY|NONUNI, NONCHAR|HIGHCHAR, 0xFD, 0xBF, 0xBF, 0xBF, 0xBF, 0xBF) # 6-byte sequence
    await test_decode(0xF0000000, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x80, 0x80) # 6-byte overlong encoding of 1-byte sequence
    await test_decode(0xF000007F, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x81, 0xBF) # 6-byte overlong encoding of 1-byte sequence
    await test_decode(0xF0000080, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x82, 0x80) # 6-byte overlong encoding of 2-byte sequence
    await test_decode(0xF00007FF, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x9F, 0xBF) # 6-byte overlong encoding of 2-byte sequence
    await test_decode(0xF0000800, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0xA0, 0x80) # 6-byte overlong encoding of 3-byte sequence
    await test_decode(0xF000FFFF, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x8F, 0xBF, 0xBF) # 6-byte overlong encoding of 3-byte sequence
    await set_input(2) # reënable range check
    await test_decode(0x00200000, READY|NONUNI|ERROR, 0, 0xF8, 0x88, 0x80, 0x80, 0x80) # 5-byte sequence
    await test_decode(0x03FFFFFF, READY|NONUNI|ERROR, 0, 0xFB, 0xBF, 0xBF, 0xBF, 0xBF) # 5-byte sequence
    await test_decode(0x04000000, READY|NONUNI|ERROR, 0, 0xFC, 0x84, 0x80, 0x80, 0x80, 0x80) # 6-byte sequence
    await test_decode(0x7FFFFFFF, READY|NONUNI|ERROR, 0, 0xFD, 0xBF, 0xBF, 0xBF, 0xBF, 0xBF) # 6-byte sequence
    await test_decode(0xF0000000, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x80, 0x80) # 6-byte overlong encoding of 1-byte sequence
    await test_decode(0xF000007F, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x81, 0xBF) # 6-byte overlong encoding of 1-byte sequence
    await test_decode(0xF0000080, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x82, 0x80) # 6-byte overlong encoding of 2-byte sequence
    await test_decode(0xF00007FF, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0x9F, 0xBF) # 6-byte overlong encoding of 2-byte sequence
    await test_decode(0xF0000800, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x80, 0xA0, 0x80) # 6-byte overlong encoding of 3-byte sequence
    await test_decode(0xF000FFFF, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x8F, 0xBF, 0xBF) # 6-byte overlong encoding of 3-byte sequence
    await test_decode(0xF0010000, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x80, 0x90, 0x80, 0x80) # 6-byte overlong encoding of 4-byte sequence
    await test_decode(0xF01FFFFF, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x87, 0xBF, 0xBF, 0xBF) # 6-byte overlong encoding of 4-byte sequence
    await test_decode(0xF0200000, READY|OVERLONG|ERROR, 0, 0xFC, 0x80, 0x88, 0x80, 0x80, 0x80) # 6-byte overlong encoding of 5-byte sequence
    await test_decode(0xF3FFFFFF, READY|OVERLONG|ERROR, 0, 0xFC, 0x83, 0xBF, 0xBF, 0xBF, 0xBF) # 6-byte overlong encoding of 5-byte sequence
    await test_decode(0xF8000000, READY|OVERLONG|ERROR, 0, 0xF8, 0x80, 0x80, 0x80, 0x80) # 5-byte overlong encoding of 1-byte sequence
    await test_decode(0xF800007F, READY|OVERLONG|ERROR, 0, 0xF8, 0x80, 0x80, 0x81, 0xBF) # 5-byte overlong encoding of 1-byte sequence
    await test_decode(0xF8000080, READY|OVERLONG|ERROR, 0, 0xF8, 0x80, 0x80, 0x82, 0x80) # 5-byte overlong encoding of 2-byte sequence
    await test_decode(0xF80007FF, READY|OVERLONG|ERROR, 0, 0xF8, 0x80, 0x80, 0x9F, 0xBF) # 5-byte overlong encoding of 2-byte sequence
    await test_decode(0xF8000800, READY|OVERLONG|ERROR, 0, 0xF8, 0x80, 0x80, 0xA0, 0x80) # 5-byte overlong encoding of 3-byte sequence
    await test_decode(0xF800FFFF, READY|OVERLONG|ERROR, 0, 0xF8, 0x80, 0x8F, 0xBF, 0xBF) # 5-byte overlong encoding of 3-byte sequence
    await test_decode(0xF8010000, READY|OVERLONG|ERROR, 0, 0xF8, 0x80, 0x90, 0x80, 0x80) # 5-byte overlong encoding of 4-byte sequence
    await test_decode(0xF81FFFFF, READY|OVERLONG|ERROR, 0, 0xF8, 0x87, 0xBF, 0xBF, 0xBF) # 5-byte overlong encoding of 4-byte sequence
    await test_decode(0xFC000000, UNDERFLOW, 0, 0xFC, 0x80, 0x80, 0x80, 0x80) # 5-byte truncation of 6-byte sequence
    await test_decode(0xFDFFFFFF, UNDERFLOW, 0, 0xFD, 0xBF, 0xBF, 0xBF, 0xBF) # 5-byte truncation of 6-byte sequence
    await test_decode(0xFFC00000, READY|OVERLONG|ERROR, 0, 0xF0, 0x80, 0x80, 0x80) # 4-byte overlong encoding of 1-byte sequence
    await test_decode(0xFFC0007F, READY|OVERLONG|ERROR, 0, 0xF0, 0x80, 0x81, 0xBF) # 4-byte overlong encoding of 1-byte sequence
    await test_decode(0xFFC00080, READY|OVERLONG|ERROR, 0, 0xF0, 0x80, 0x82, 0x80) # 4-byte overlong encoding of 2-byte sequence
    await test_decode(0xFFC007FF, READY|OVERLONG|ERROR, 0, 0xF0, 0x80, 0x9F, 0xBF) # 4-byte overlong encoding of 2-byte sequence
    await test_decode(0xFFC00800, READY|OVERLONG|ERROR, 0, 0xF0, 0x80, 0xA0, 0x80) # 4-byte overlong encoding of 3-byte sequence
    await test_decode(0xFFC0FFFF, READY|OVERLONG|ERROR, 0, 0xF0, 0x8F, 0xBF, 0xBF) # 4-byte overlong encoding of 3-byte sequence
    await test_decode(0xFFE00000, UNDERFLOW, 0, 0xF8, 0x80, 0x80, 0x80) # 4-byte truncation of 5-byte sequence
    await test_decode(0xFFEFFFFF, UNDERFLOW, 0, 0xFB, 0xBF, 0xBF, 0xBF) # 4-byte truncation of 5-byte sequence
    await test_decode(0xFFF00000, UNDERFLOW, 0, 0xFC, 0x80, 0x80, 0x80) # 4-byte truncation of 6-byte sequence
    await test_decode(0xFFF7FFFF, UNDERFLOW, 0, 0xFD, 0xBF, 0xBF, 0xBF) # 4-byte truncation of 6-byte sequence
    await test_decode(0xFFFE0000, READY|OVERLONG|ERROR, 0, 0xE0, 0x80, 0x80) # 3-byte overlong encoding of 1-byte sequence
    await test_decode(0xFFFE007F, READY|OVERLONG|ERROR, 0, 0xE0, 0x81, 0xBF) # 3-byte overlong encoding of 1-byte sequence
    await test_decode(0xFFFE0080, READY|OVERLONG|ERROR, 0, 0xE0, 0x82, 0x80) # 3-byte overlong encoding of 2-byte sequence
    await test_decode(0xFFFE07FF, READY|OVERLONG|ERROR, 0, 0xE0, 0x9F, 0xBF) # 3-byte overlong encoding of 2-byte sequence
    await test_decode(0xFFFF0000, UNDERFLOW, 0, 0xF0, 0x80, 0x80) # 3-byte truncation of 4-byte sequence
    await test_decode(0xFFFF7FFF, UNDERFLOW, 0, 0xF7, 0xBF, 0xBF) # 3-byte truncation of 4-byte sequence
    await test_decode(0xFFFF8000, UNDERFLOW, 0, 0xF8, 0x80, 0x80) # 3-byte truncation of 5-byte sequence
    await test_decode(0xFFFFBFFF, UNDERFLOW, 0, 0xFB, 0xBF, 0xBF) # 3-byte truncation of 5-byte sequence
    await test_decode(0xFFFFC000, UNDERFLOW, 0, 0xFC, 0x80, 0x80) # 3-byte truncation of 6-byte sequence
    await test_decode(0xFFFFDFFF, UNDERFLOW, 0, 0xFD, 0xBF, 0xBF) # 3-byte truncation of 6-byte sequence
    await test_decode(0xFFFFF000, READY|OVERLONG|ERROR, 0, 0xC0, 0x80) # 2-byte overlong encoding of 1-byte sequence
    await test_decode(0xFFFFF07F, READY|OVERLONG|ERROR, 0, 0xC1, 0xBF) # 2-byte overlong encoding of 1-byte sequence
    await test_decode(0xFFFFF800, UNDERFLOW, 0, 0xE0, 0x80) # 2-byte truncation of 3-byte sequence
    await test_decode(0xFFFFFBFF, UNDERFLOW, 0, 0xEF, 0xBF) # 2-byte truncation of 3-byte sequence
    await test_decode(0xFFFFFC00, UNDERFLOW, 0, 0xF0, 0x80) # 2-byte truncation of 4-byte sequence
    await test_decode(0xFFFFFDFF, UNDERFLOW, 0, 0xF7, 0xBF) # 2-byte truncation of 4-byte sequence
    await test_decode(0xFFFFFE00, UNDERFLOW, 0, 0xF8, 0x80) # 2-byte truncation of 5-byte sequence
    await test_decode(0xFFFFFEFF, UNDERFLOW, 0, 0xFB, 0xBF) # 2-byte truncation of 5-byte sequence
    await test_decode(0xFFFFFF00, UNDERFLOW, 0, 0xFC, 0x80) # 2-byte truncation of 6-byte sequence
    await test_decode(0xFFFFFF7F, UNDERFLOW, 0, 0xFD, 0xBF) # 2-byte truncation of 6-byte sequence
    await test_decode(0xFFFFFF80, READY|INVALID|ERROR, 0, 0x80) # lone trailing byte
    await test_decode(0xFFFFFFBF, READY|INVALID|ERROR, 0, 0xBF) # lone trailing byte
    await test_decode(0xFFFFFFC0, UNDERFLOW, 0, 0xC0) # lone leading byte of 2-byte sequence
    await test_decode(0xFFFFFFDF, UNDERFLOW, 0, 0xDF) # lone leading byte of 2-byte sequence
    await test_decode(0xFFFFFFE0, UNDERFLOW, 0, 0xE0) # lone leading byte of 3-byte sequence
    await test_decode(0xFFFFFFEF, UNDERFLOW, 0, 0xEF) # lone leading byte of 3-byte sequence
    await test_decode(0xFFFFFFF0, UNDERFLOW, 0, 0xF0) # lone leading byte of 4-byte sequence
    await test_decode(0xFFFFFFF7, UNDERFLOW, 0, 0xF7) # lone leading byte of 4-byte sequence
    await test_decode(0xFFFFFFF8, UNDERFLOW, 0, 0xF8) # lone leading byte of 5-byte sequence
    await test_decode(0xFFFFFFFB, UNDERFLOW, 0, 0xFB) # lone leading byte of 5-byte sequence
    await test_decode(0xFFFFFFFC, UNDERFLOW, 0, 0xFC) # lone leading byte of 6-byte sequence
    await test_decode(0xFFFFFFFD, UNDERFLOW, 0, 0xFD) # lone leading byte of 6-byte sequence
    await test_decode(0xFFFFFFFE, READY|INVALID|ERROR, 0, 0xFE) # lone invalid byte
    await test_decode(0xFFFFFFFF, READY|INVALID|ERROR, 0, 0xFF) # lone invalid byte
