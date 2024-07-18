## How to test

The `test.py` file covers the following test cases.

## BMP characters

| UTF‑32     | UTF‑16 | UTF‑8      | Errors | Properties                   | Notes |
| ---------- | ------ | ---------- | ------ | ---------------------------- | ----- |
| `00000000` | `0000` | `00`       | READY  | CONTROL                      | First C0 control character; first 1‑byte UTF‑8 sequence
| `00000001` | `0001` | `01`       | READY  | CONTROL                      | First nonzero C0 control character
| `0000001F` | `001F` | `1F`       | READY  | CONTROL                      | Last C0 control character
| `00000020` | `0020` | `20`       | READY  | NORMAL                       | First printable ASCII character
| `0000007E` | `007E` | `7E`       | READY  | NORMAL                       | Last printable ASCII character
| `0000007F` | `007F` | `7F`       | READY  | CONTROL                      | Last ASCII character; last 1‑byte UTF‑8 sequence
| `00000080` | `0080` | `C2 80`    | READY  | CONTROL                      | First C1 control character; first 2‑byte UTF‑8 sequence
| `0000009F` | `009F` | `C2 9F`    | READY  | CONTROL                      | Last C1 control character
| `000000A0` | `00A0` | `C2 A0`    | READY  | NORMAL                       | First printable Latin‑1 character
| `000000FF` | `00FF` | `C3 BF`    | READY  | NORMAL                       | Last printable Latin‑1 character
| `00000100` | `0100` | `C4 80`    | READY  | NORMAL                       | First non-ASCII, non-Latin‑1 character
| `000007FF` | `07FF` | `DF BF`    | READY  | NORMAL                       | Last 2‑byte UTF‑8 sequence
| `00000800` | `0800` | `E0 A0 80` | READY  | NORMAL                       | First 3‑byte UTF‑8 sequence
| `0000D7FF` | `D7FF` | `ED 9F BF` | READY  | NORMAL                       | Predecessor of first high surrogate
| `0000D800` | `D800` | `ED A0 80` | READY  | SURROGATE, HIGHCHAR          | First high surrogate
| `0000DB7F` | `DB7F` | `ED AD BF` | READY  | SURROGATE, HIGHCHAR          | Last non-private-use high surrogate
| `0000DB80` | `DB80` | `ED AE 80` | READY  | SURROGATE, HIGHCHAR, PRIVATE | First private-use high surrogate
| `0000DBFF` | `DBFF` | `ED AF BF` | READY  | SURROGATE, HIGHCHAR, PRIVATE | Last high surrogate
| `0000DC00` | `DC00` | `ED B0 80` | READY  | SURROGATE                    | First low surrogate
| `0000DFFF` | `DFFF` | `ED BF BF` | READY  | SURROGATE                    | Last low surrogate
| `0000E000` | `E000` | `EE 80 80` | READY  | PRIVATE                      | First BMP private use character
| `0000F8FF` | `F8FF` | `EF A3 BF` | READY  | PRIVATE                      | Last BMP private use character
| `0000F900` | `F900` | `EF A4 80` | READY  | NORMAL                       | Successor of last BMP private use character
| `0000FDCF` | `FDCF` | `EF B7 8F` | READY  | NORMAL                       | Predecessor of first BMP noncharacter
| `0000FDD0` | `FDD0` | `EF B7 90` | READY  | NONCHAR                      | First BMP noncharacter
| `0000FDEF` | `FDEF` | `EF B7 AF` | READY  | NONCHAR                      | Last nontrivial BMP noncharacter
| `0000FDF0` | `FDF0` | `EF B7 B0` | READY  | NORMAL                       | Successor of last nontrivial BMP noncharacter
| `0000FFFD` | `FFFD` | `EF BF BD` | READY  | NORMAL                       | Last BMP character
| `0000FFFE` | `FFFE` | `EF BF BE` | READY  | NONCHAR                      | Noncharacter
| `0000FFFF` | `FFFF` | `EF BF BF` | READY  | NONCHAR                      | Noncharacter; last 3‑byte UTF‑8 sequence; last 1‑word UTF‑16 sequence

## Non-BMP characters

| UTF‑32     | UTF‑16      | UTF‑8         | Errors | Properties        | Notes |
| ---------- | ----------- | ------------- | ------ | ----------------- | ----- |
| `00010000` | `D800 DC00` | `F0 90 80 80` | READY  | NORMAL, HIGHCHAR  | First plane 1 character; first 4‑byte UTF‑8 sequence; first 2‑word UTF‑16 sequence
| `000100FF` | `D800 DCFF` | `F0 90 83 BF` | READY  | NORMAL, HIGHCHAR  | -
| `00010100` | `D800 DD00` | `F0 90 84 80` | READY  | NORMAL, HIGHCHAR  | -
| `000101FF` | `D800 DDFF` | `F0 90 87 BF` | READY  | NORMAL, HIGHCHAR  | -
| `00010200` | `D800 DE00` | `F0 90 88 80` | READY  | NORMAL, HIGHCHAR  | -
| `000102FF` | `D800 DEFF` | `F0 90 8B BF` | READY  | NORMAL, HIGHCHAR  | -
| `00010300` | `D800 DF00` | `F0 90 8C 80` | READY  | NORMAL, HIGHCHAR  | -
| `000103FF` | `D800 DFFF` | `F0 90 8F BF` | READY  | NORMAL, HIGHCHAR  | Last plane 1 character using high surrogate D800
| `00010400` | `D801 DC00` | `F0 90 90 80` | READY  | NORMAL, HIGHCHAR  | First plane 1 character using high surrogate D801
| `000107FF` | `D801 DFFF` | `F0 90 9F BF` | READY  | NORMAL, HIGHCHAR  | Last plane 1 character using high surrogate D801
| `0001F800` | `D83E DC00` | `F0 9F A0 80` | READY  | NORMAL, HIGHCHAR  | First plane 1 character using high surrogate D83E
| `0001FBFF` | `D83E DFFF` | `F0 9F AF BF` | READY  | NORMAL, HIGHCHAR  | Last plane 1 character using high surrogate D83E
| `0001FC00` | `D83F DC00` | `F0 9F B0 80` | READY  | NORMAL, HIGHCHAR  | First plane 1 character using high surrogate D83F
| `0001FFFD` | `D83F DFFD` | `F0 9F BF BD` | READY  | NORMAL, HIGHCHAR  | Last plane 1 character
| `0001FFFE` | `D83F DFFE` | `F0 9F BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `0001FFFF` | `D83F DFFF` | `F0 9F BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `00020000` | `D840 DC00` | `F0 A0 80 80` | READY  | NORMAL, HIGHCHAR  | First plane 2 character
| `0002FFFD` | `D87F DFFD` | `F0 AF BF BD` | READY  | NORMAL, HIGHCHAR  | Last plane 2 character
| `0002FFFE` | `D87F DFFE` | `F0 AF BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `0002FFFF` | `D87F DFFF` | `F0 AF BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `00030000` | `D880 DC00` | `F0 B0 80 80` | READY  | NORMAL, HIGHCHAR  | First plane 3 character
| `0003FFFD` | `D8BF DFFD` | `F0 BF BF BD` | READY  | NORMAL, HIGHCHAR  | Last plane 3 character
| `0003FFFE` | `D8BF DFFE` | `F0 BF BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `0003FFFF` | `D8BF DFFF` | `F0 BF BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `00040000` | `D8C0 DC00` | `F1 80 80 80` | READY  | NORMAL, HIGHCHAR  | First plane 4 character
| `0004FFFD` | `D8FF DFFD` | `F1 8F BF BD` | READY  | NORMAL, HIGHCHAR  | Last plane 4 character
| `0004FFFE` | `D8FF DFFE` | `F1 8F BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `0004FFFF` | `D8FF DFFF` | `F1 8F BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `00050000` | `D900 DC00` | `F1 90 80 80` | READY  | NORMAL, HIGHCHAR  | First plane 5 character
| `0005FFFD` | `D93F DFFD` | `F1 9F BF BD` | READY  | NORMAL, HIGHCHAR  | Last plane 5 character
| `0005FFFE` | `D93F DFFE` | `F1 9F BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `0005FFFF` | `D93F DFFF` | `F1 9F BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `00060000` | `D940 DC00` | `F1 A0 80 80` | READY  | NORMAL, HIGHCHAR  | First plane 6 character
| `0006FFFD` | `D97F DFFD` | `F1 AF BF BD` | READY  | NORMAL, HIGHCHAR  | Last plane 6 character
| `0006FFFE` | `D97F DFFE` | `F1 AF BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `0006FFFF` | `D97F DFFF` | `F1 AF BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `00070000` | `D980 DC00` | `F1 B0 80 80` | READY  | NORMAL, HIGHCHAR  | First plane 7 character
| `0007FFFD` | `D9BF DFFD` | `F1 BF BF BD` | READY  | NORMAL, HIGHCHAR  | Last plane 7 character
| `0007FFFE` | `D9BF DFFE` | `F1 BF BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `0007FFFF` | `D9BF DFFF` | `F1 BF BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `00080000` | `D9C0 DC00` | `F2 80 80 80` | READY  | NORMAL, HIGHCHAR  | First plane 8 character
| `0008FFFD` | `D9FF DFFD` | `F2 8F BF BD` | READY  | NORMAL, HIGHCHAR  | Last plane 8 character
| `0008FFFE` | `D9FF DFFE` | `F2 8F BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `0008FFFF` | `D9FF DFFF` | `F2 8F BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `00090000` | `DA00 DC00` | `F2 90 80 80` | READY  | NORMAL, HIGHCHAR  | First plane 9 character
| `0009FFFD` | `DA3F DFFD` | `F2 9F BF BD` | READY  | NORMAL, HIGHCHAR  | Last plane 9 character
| `0009FFFE` | `DA3F DFFE` | `F2 9F BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `0009FFFF` | `DA3F DFFF` | `F2 9F BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `000A0000` | `DA40 DC00` | `F2 A0 80 80` | READY  | NORMAL, HIGHCHAR  | First plane 10 character
| `000AFFFD` | `DA7F DFFD` | `F2 AF BF BD` | READY  | NORMAL, HIGHCHAR  | Last plane 10 character
| `000AFFFE` | `DA7F DFFE` | `F2 AF BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `000AFFFF` | `DA7F DFFF` | `F2 AF BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `000B0000` | `DA80 DC00` | `F2 B0 80 80` | READY  | NORMAL, HIGHCHAR  | First plane 11 character
| `000BFFFD` | `DABF DFFD` | `F2 BF BF BD` | READY  | NORMAL, HIGHCHAR  | Last plane 11 character
| `000BFFFE` | `DABF DFFE` | `F2 BF BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `000BFFFF` | `DABF DFFF` | `F2 BF BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `000C0000` | `DAC0 DC00` | `F3 80 80 80` | READY  | NORMAL, HIGHCHAR  | First plane 12 character
| `000CFFFD` | `DAFF DFFD` | `F3 8F BF BD` | READY  | NORMAL, HIGHCHAR  | Last plane 12 character
| `000CFFFE` | `DAFF DFFE` | `F3 8F BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `000CFFFF` | `DAFF DFFF` | `F3 8F BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `000D0000` | `DB00 DC00` | `F3 90 80 80` | READY  | NORMAL, HIGHCHAR  | First plane 13 character
| `000DFFFD` | `DB3F DFFD` | `F3 9F BF BD` | READY  | NORMAL, HIGHCHAR  | Last plane 13 character
| `000DFFFE` | `DB3F DFFE` | `F3 9F BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `000DFFFF` | `DB3F DFFF` | `F3 9F BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `000E0000` | `DB40 DC00` | `F3 A0 80 80` | READY  | NORMAL, HIGHCHAR  | First plane 14 character
| `000EFFFD` | `DB7F DFFD` | `F3 AF BF BD` | READY  | NORMAL, HIGHCHAR  | Last plane 14 character
| `000EFFFE` | `DB7F DFFE` | `F3 AF BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `000EFFFF` | `DB7F DFFF` | `F3 AF BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `000F0000` | `DB80 DC00` | `F3 B0 80 80` | READY  | PRIVATE, HIGHCHAR | First plane 15 character
| `000FFFFD` | `DBBF DFFD` | `F3 BF BF BD` | READY  | PRIVATE, HIGHCHAR | Last plane 15 character
| `000FFFFE` | `DBBF DFFE` | `F3 BF BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `000FFFFF` | `DBBF DFFF` | `F3 BF BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `00100000` | `DBC0 DC00` | `F4 80 80 80` | READY  | PRIVATE, HIGHCHAR | First plane 16 character
| `001003FF` | `DBC0 DFFF` | `F4 80 8F BF` | READY  | PRIVATE, HIGHCHAR | Last plane 16 character using high surrogate D8C0
| `00100400` | `DBC1 DC00` | `F4 80 90 80` | READY  | PRIVATE, HIGHCHAR | First plane 16 character using high surrogate D8C1
| `001007FF` | `DBC1 DFFF` | `F4 80 9F BF` | READY  | PRIVATE, HIGHCHAR | Last plane 16 character using high surrogate D8C1
| `0010F800` | `DBFE DC00` | `F4 8F A0 80` | READY  | PRIVATE, HIGHCHAR | First plane 16 character using high surrogate D8FE
| `0010FBFF` | `DBFE DFFF` | `F4 8F AF BF` | READY  | PRIVATE, HIGHCHAR | Last plane 16 character using high surrogate D8FE
| `0010FC00` | `DBFF DC00` | `F4 8F B0 80` | READY  | PRIVATE, HIGHCHAR | First plane 16 character using high surrogate D8FF
| `0010FCFF` | `DBFF DCFF` | `F4 8F B3 BF` | READY  | PRIVATE, HIGHCHAR | -
| `0010FD00` | `DBFF DD00` | `F4 8F B4 80` | READY  | PRIVATE, HIGHCHAR | -
| `0010FDFF` | `DBFF DDFF` | `F4 8F B7 BF` | READY  | PRIVATE, HIGHCHAR | -
| `0010FE00` | `DBFF DE00` | `F4 8F B8 80` | READY  | PRIVATE, HIGHCHAR | -
| `0010FEFF` | `DBFF DEFF` | `F4 8F BB BF` | READY  | PRIVATE, HIGHCHAR | -
| `0010FF00` | `DBFF DF00` | `F4 8F BC 80` | READY  | PRIVATE, HIGHCHAR | -
| `0010FFFD` | `DBFF DFFD` | `F4 8F BF BD` | READY  | PRIVATE, HIGHCHAR | Last plane 16 character
| `0010FFFE` | `DBFF DFFE` | `F4 8F BF BE` | READY  | NONCHAR, HIGHCHAR | Noncharacter
| `0010FFFF` | `DBFF DFFF` | `F4 8F BF BF` | READY  | NONCHAR, HIGHCHAR | Noncharacter; last Unicode code point; last 2‑word UTF‑16 sequence

## Non-Unicode values

These are normally error states, but can be ignored as errors by setting CHK (input 2) LOW. These should not be used if you are working with Unicode text, but could be used if you want a UTF‑8-like encoding of integers for some reason.

| UTF‑32     | UTF‑16 | UTF‑8               | Errors        | Properties        | Notes |
| ---------- | ------ | ------------------- | ------------- | ----------------- | ----- |
| `00110000` | -      | `F4 90 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First non-Unicode value; first "plane 17" "character"
| `0011FFFD` | -      | `F4 9F BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 17" "character"
| `0011FFFE` | -      | `F4 9F BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 17" "noncharacter"
| `0011FFFF` | -      | `F4 9F BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 17" "noncharacter"
| `00120000` | -      | `F4 A0 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First "plane 18" "character"
| `0012FFFD` | -      | `F4 AF BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 18" "character"
| `0012FFFE` | -      | `F4 AF BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 18" "noncharacter"
| `0012FFFF` | -      | `F4 AF BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 18" "noncharacter"
| `00130000` | -      | `F4 B0 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First "plane 19" "character"
| `0013FFFD` | -      | `F4 BF BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 19" "character"
| `0013FFFE` | -      | `F4 BF BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 19" "noncharacter"
| `0013FFFF` | -      | `F4 BF BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 19" "noncharacter"
| `00140000` | -      | `F5 80 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First "plane 20" "character"
| `0014FFFD` | -      | `F5 8F BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 20" "character"
| `0014FFFE` | -      | `F5 8F BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 20" "noncharacter"
| `0014FFFF` | -      | `F5 8F BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 20" "noncharacter"
| `00150000` | -      | `F5 90 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First "plane 21" "character"
| `0015FFFD` | -      | `F5 9F BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 21" "character"
| `0015FFFE` | -      | `F5 9F BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 21" "noncharacter"
| `0015FFFF` | -      | `F5 9F BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 21" "noncharacter"
| `00160000` | -      | `F5 A0 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First "plane 22" "character"
| `0016FFFD` | -      | `F5 AF BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 22" "character"
| `0016FFFE` | -      | `F5 AF BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 22" "noncharacter"
| `0016FFFF` | -      | `F5 AF BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 22" "noncharacter"
| `00170000` | -      | `F5 B0 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First "plane 23" "character"
| `0017FFFD` | -      | `F5 BF BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 23" "character"
| `0017FFFE` | -      | `F5 BF BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 23" "noncharacter"
| `0017FFFF` | -      | `F5 BF BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 23" "noncharacter"
| `00180000` | -      | `F6 80 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First "plane 24" "character"
| `0018FFFD` | -      | `F6 8F BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 24" "character"
| `0018FFFE` | -      | `F6 8F BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 24" "noncharacter"
| `0018FFFF` | -      | `F6 8F BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 24" "noncharacter"
| `00190000` | -      | `F6 90 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First "plane 25" "character"
| `0019FFFD` | -      | `F6 9F BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 25" "character"
| `0019FFFE` | -      | `F6 9F BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 25" "noncharacter"
| `0019FFFF` | -      | `F6 9F BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 25" "noncharacter"
| `001A0000` | -      | `F6 A0 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First "plane 26" "character"
| `001AFFFD` | -      | `F6 AF BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 26" "character"
| `001AFFFE` | -      | `F6 AF BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 26" "noncharacter"
| `001AFFFF` | -      | `F6 AF BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 26" "noncharacter"
| `001B0000` | -      | `F6 B0 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First "plane 27" "character"
| `001BFFFD` | -      | `F6 BF BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 27" "character"
| `001BFFFE` | -      | `F6 BF BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 27" "noncharacter"
| `001BFFFF` | -      | `F6 BF BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 27" "noncharacter"
| `001C0000` | -      | `F7 80 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First "plane 28" "character"
| `001CFFFD` | -      | `F7 8F BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 28" "character"
| `001CFFFE` | -      | `F7 8F BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 28" "noncharacter"
| `001CFFFF` | -      | `F7 8F BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 28" "noncharacter"
| `001D0000` | -      | `F7 90 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First "plane 29" "character"
| `001DFFFD` | -      | `F7 9F BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 29" "character"
| `001DFFFE` | -      | `F7 9F BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 29" "noncharacter"
| `001DFFFF` | -      | `F7 9F BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 29" "noncharacter"
| `001E0000` | -      | `F7 A0 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First "plane 30" "character"
| `001EFFFD` | -      | `F7 AF BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 30" "character"
| `001EFFFE` | -      | `F7 AF BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 30" "noncharacter"
| `001EFFFF` | -      | `F7 AF BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 30" "noncharacter"
| `001F0000` | -      | `F7 B0 80 80`       | READY, NONUNI | PRIVATE, HIGHCHAR | First "plane 31" "character"
| `001FFFFD` | -      | `F7 BF BF BD`       | READY, NONUNI | PRIVATE, HIGHCHAR | Last "plane 31" "character"
| `001FFFFE` | -      | `F7 BF BF BE`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 31" "noncharacter"
| `001FFFFF` | -      | `F7 BF BF BF`       | READY, NONUNI | NONCHAR, HIGHCHAR | "Plane 31" "noncharacter"; last 4‑byte UTF‑8-like sequence
| `00200000` | -      | `F8 88 80 80 80`    | READY, NONUNI | PRIVATE, HIGHCHAR | First 5‑byte UTF‑8-like sequence
| `03FFFFFF` | -      | `FB BF BF BF BF`    | READY, NONUNI | NONCHAR, HIGHCHAR | Last 5‑byte UTF‑8-like sequence
| `04000000` | -      | `FC 84 80 80 80 80` | READY, NONUNI | PRIVATE, HIGHCHAR | First 6‑byte UTF‑8-like sequence
| `7FFFFFFF` | -      | `FD BF BF BF BF BF` | READY, NONUNI | NONCHAR, HIGHCHAR | Last non-Unicode value; last 6‑byte UTF‑8-like sequence

## Error states

These values are used for incomplete or invalid input states.

| UTF‑32     | UTF‑16    | UTF‑8               | Errors                 | Properties | Notes |
| ---------- | --------- | ------------------- | ---------------------- | ---------- | ----- |
| `80000000` | -         | -                   | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `DDD7FFFF` | -         | -                   | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `DDD80000` | `D800 00` | -                   | UNDERFLOW              | -          | First state for a high surrogate followed by only one byte of a lower surrogate
| `DDD8369C` | `D836 9C` | -                   | UNDERFLOW              | -          | -
| `DDD8C963` | `D8C9 63` | -                   | UNDERFLOW              | -          | -
| `DDD8FFFF` | `D8FF FF` | -                   | UNDERFLOW              | -          | -
| `DDD90000` | `D900 00` | -                   | UNDERFLOW              | -          | -
| `DDD9369C` | `D936 9C` | -                   | UNDERFLOW              | -          | -
| `DDD9C963` | `D9C9 63` | -                   | UNDERFLOW              | -          | -
| `DDD9FFFF` | `D9FF FF` | -                   | UNDERFLOW              | -          | -
| `DDDA0000` | `DA00 00` | -                   | UNDERFLOW              | -          | -
| `DDDA369C` | `DA36 9C` | -                   | UNDERFLOW              | -          | -
| `DDDAC963` | `DAC9 63` | -                   | UNDERFLOW              | -          | -
| `DDDAFFFF` | `DAFF FF` | -                   | UNDERFLOW              | -          | -
| `DDDB0000` | `DB00 00` | -                   | UNDERFLOW              | -          | -
| `DDDB369C` | `DB36 9C` | -                   | UNDERFLOW              | -          | -
| `DDDBC963` | `DBC9 63` | -                   | UNDERFLOW              | -          | -
| `DDDBFFFF` | `DBFF FF` | -                   | UNDERFLOW              | -          | Last state for a high surrogate followed by only one byte of a lower surrogate
| `DDDC0000` | -         | -                   | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `DDDDDCFF` | -         | -                   | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `DDDDDD00` | `00`      | -                   | UNDERFLOW              | -          | First state for only one byte of a UTF‑16 word
| `DDDDDD5A` | `5A`      | -                   | UNDERFLOW              | -          | -
| `DDDDDDA5` | `A5`      | -                   | UNDERFLOW              | -          | -
| `DDDDDDFF` | `FF`      | -                   | UNDERFLOW              | -          | Last state for only one byte of a UTF‑16 word
| `DDDDDE00` | -         | -                   | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `EFFFFFFF` | -         | -                   | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `F0000000` | -         | `FC 80 80 80 80 80` | READY, OVERLONG, ERROR | -          | 6‑byte overlong encoding of 1‑byte UTF‑8 sequence
| `F000007F` | -         | `FC 80 80 80 81 BF` | READY, OVERLONG, ERROR | -          | 6‑byte overlong encoding of 1‑byte UTF‑8 sequence
| `F0000080` | -         | `FC 80 80 80 82 80` | READY, OVERLONG, ERROR | -          | 6‑byte overlong encoding of 2‑byte UTF‑8 sequence
| `F00007FF` | -         | `FC 80 80 80 9F BF` | READY, OVERLONG, ERROR | -          | 6‑byte overlong encoding of 2‑byte UTF‑8 sequence
| `F0000800` | -         | `FC 80 80 80 A0 80` | READY, OVERLONG, ERROR | -          | 6‑byte overlong encoding of 3‑byte UTF‑8 sequence
| `F000FFFF` | -         | `FC 80 80 8F BF BF` | READY, OVERLONG, ERROR | -          | 6‑byte overlong encoding of 3‑byte UTF‑8 sequence
| `F0010000` | -         | `FC 80 80 90 80 80` | READY, OVERLONG, ERROR | -          | 6‑byte overlong encoding of 4‑byte UTF‑8 sequence
| `F01FFFFF` | -         | `FC 80 87 BF BF BF` | READY, OVERLONG, ERROR | -          | 6‑byte overlong encoding of 4‑byte UTF‑8 sequence
| `F0200000` | -         | `FC 80 88 80 80 80` | READY, OVERLONG, ERROR | -          | 6‑byte overlong encoding of 5‑byte UTF‑8 sequence
| `F3FFFFFF` | -         | `FC 83 BF BF BF BF` | READY, OVERLONG, ERROR | -          | 6‑byte overlong encoding of 5‑byte UTF‑8 sequence
| `F4000000` | -         | `FC 84 80 80 80 80` | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `F7FFFFFF` | -         | `FC 87 BF BF BF BF` | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `F8000000` | -         | `F8 80 80 80 80`    | READY, OVERLONG, ERROR | -          | 5‑byte overlong encoding of 1‑byte UTF‑8 sequence
| `F800007F` | -         | `F8 80 80 81 BF`    | READY, OVERLONG, ERROR | -          | 5‑byte overlong encoding of 1‑byte UTF‑8 sequence
| `F8000080` | -         | `F8 80 80 82 80`    | READY, OVERLONG, ERROR | -          | 5‑byte overlong encoding of 2‑byte UTF‑8 sequence
| `F80007FF` | -         | `F8 80 80 9F BF`    | READY, OVERLONG, ERROR | -          | 5‑byte overlong encoding of 2‑byte UTF‑8 sequence
| `F8000800` | -         | `F8 80 80 A0 80`    | READY, OVERLONG, ERROR | -          | 5‑byte overlong encoding of 3‑byte UTF‑8 sequence
| `F800FFFF` | -         | `F8 80 8F BF BF`    | READY, OVERLONG, ERROR | -          | 5‑byte overlong encoding of 3‑byte UTF‑8 sequence
| `F8010000` | -         | `F8 80 90 80 80`    | READY, OVERLONG, ERROR | -          | 5‑byte overlong encoding of 4‑byte UTF‑8 sequence
| `F81FFFFF` | -         | `F8 87 BF BF BF`    | READY, OVERLONG, ERROR | -          | 5‑byte overlong encoding of 4‑byte UTF‑8 sequence
| `F8200000` | -         | `F8 88 80 80 80`    | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `FBFFFFFF` | -         | `FB BF BF BF BF`    | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `FC000000` | -         | `FC 80 80 80 80`    | UNDERFLOW              | -          | 5‑byte truncation of 6‑byte UTF‑8 sequence
| `FDFFFFFF` | -         | `FD BF BF BF BF`    | UNDERFLOW              | -          | 5‑byte truncation of 6‑byte UTF‑8 sequence
| `FE000000` | -         | `FE 80 80 80 80`    | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `FFBFFFFF` | -         | `FF AF BF BF BF`    | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `FFC00000` | -         | `F0 80 80 80`       | READY, OVERLONG, ERROR | -          | 4‑byte overlong encoding of 1‑byte UTF‑8 sequence
| `FFC0007F` | -         | `F0 80 81 BF`       | READY, OVERLONG, ERROR | -          | 4‑byte overlong encoding of 1‑byte UTF‑8 sequence
| `FFC00080` | -         | `F0 80 82 80`       | READY, OVERLONG, ERROR | -          | 4‑byte overlong encoding of 2‑byte UTF‑8 sequence
| `FFC007FF` | -         | `F0 80 9F BF`       | READY, OVERLONG, ERROR | -          | 4‑byte overlong encoding of 2‑byte UTF‑8 sequence
| `FFC00800` | -         | `F0 80 A0 80`       | READY, OVERLONG, ERROR | -          | 4‑byte overlong encoding of 3‑byte UTF‑8 sequence
| `FFC0FFFF` | -         | `F0 8F BF BF`       | READY, OVERLONG, ERROR | -          | 4‑byte overlong encoding of 3‑byte UTF‑8 sequence
| `FFC10000` | -         | `F0 90 80 80`       | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `FFDFFFFF` | -         | `F7 BF BF BF`       | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `FFE00000` | -         | `F8 80 80 80`       | UNDERFLOW              | -          | 4‑byte truncation of 5‑byte UTF‑8 sequence
| `FFEFFFFF` | -         | `FB BF BF BF`       | UNDERFLOW              | -          | 4‑byte truncation of 5‑byte UTF‑8 sequence
| `FFF00000` | -         | `FC 80 80 80`       | UNDERFLOW              | -          | 4‑byte truncation of 6‑byte UTF‑8 sequence
| `FFF7FFFF` | -         | `FD BF BF BF`       | UNDERFLOW              | -          | 4‑byte truncation of 6‑byte UTF‑8 sequence
| `FFF80000` | -         | `FE 80 80 80`       | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `FFFDFFFF` | -         | `FF 9F BF BF`       | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `FFFE0000` | -         | `E0 80 80`          | READY, OVERLONG, ERROR | -          | 3‑byte overlong encoding of 1‑byte UTF‑8 sequence
| `FFFE007F` | -         | `E0 81 BF`          | READY, OVERLONG, ERROR | -          | 3‑byte overlong encoding of 1‑byte UTF‑8 sequence
| `FFFE0080` | -         | `E0 82 80`          | READY, OVERLONG, ERROR | -          | 3‑byte overlong encoding of 2‑byte UTF‑8 sequence
| `FFFE07FF` | -         | `E0 9F BF`          | READY, OVERLONG, ERROR | -          | 3‑byte overlong encoding of 2‑byte UTF‑8 sequence
| `FFFE0800` | -         | `E0 A0 80`          | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `FFFEFFFF` | -         | `EF BF BF`          | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `FFFF0000` | -         | `F0 80 80`          | UNDERFLOW              | -          | 3‑byte truncation of 4‑byte UTF‑8 sequence
| `FFFF7FFF` | -         | `F7 BF BF`          | UNDERFLOW              | -          | 3‑byte truncation of 4‑byte UTF‑8 sequence
| `FFFF8000` | -         | `F8 80 80`          | UNDERFLOW              | -          | 3‑byte truncation of 5‑byte UTF‑8 sequence
| `FFFFBFFF` | -         | `FB BF BF`          | UNDERFLOW              | -          | 3‑byte truncation of 5‑byte UTF‑8 sequence
| `FFFFC000` | -         | `FC 80 80`          | UNDERFLOW              | -          | 3‑byte truncation of 6‑byte UTF‑8 sequence
| `FFFFDFFF` | -         | `FD BF BF`          | UNDERFLOW              | -          | 3‑byte truncation of 6‑byte UTF‑8 sequence
| `FFFFE000` | -         | `FE 80 80`          | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `FFFFEFFF` | -         | `FE BF BF`          | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `FFFFF000` | -         | `C0 80`             | READY, OVERLONG, ERROR | -          | 2‑byte overlong encoding of 1‑byte UTF‑8 sequence
| `FFFFF07F` | -         | `C1 BF`             | READY, OVERLONG, ERROR | -          | 2‑byte overlong encoding of 1‑byte UTF‑8 sequence
| `FFFFF080` | -         | `C2 80`             | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `FFFFF7FF` | -         | `DF BF`             | READY, INVALID, ERROR  | -          | Cannot be produced from any UTF‑8 or UTF‑16 input, valid or not
| `FFFFF800` | -         | `E0 80`             | UNDERFLOW              | -          | 2‑byte truncation of 3‑byte UTF‑8 sequence
| `FFFFFBFF` | -         | `EF BF`             | UNDERFLOW              | -          | 2‑byte truncation of 3‑byte UTF‑8 sequence
| `FFFFFC00` | -         | `F0 80`             | UNDERFLOW              | -          | 2‑byte truncation of 4‑byte UTF‑8 sequence
| `FFFFFDFF` | -         | `F7 BF`             | UNDERFLOW              | -          | 2‑byte truncation of 4‑byte UTF‑8 sequence
| `FFFFFE00` | -         | `F8 80`             | UNDERFLOW              | -          | 2‑byte truncation of 5‑byte UTF‑8 sequence
| `FFFFFEFF` | -         | `FB BF`             | UNDERFLOW              | -          | 2‑byte truncation of 5‑byte UTF‑8 sequence
| `FFFFFF00` | -         | `FC 80`             | UNDERFLOW              | -          | 2‑byte truncation of 6‑byte UTF‑8 sequence
| `FFFFFF7F` | -         | `FD BF`             | UNDERFLOW              | -          | 2‑byte truncation of 6‑byte UTF‑8 sequence
| `FFFFFF80` | -         | `80`                | READY, INVALID, ERROR  | -          | Lone trailing byte of UTF‑8 sequence
| `FFFFFFBF` | -         | `BF`                | READY, INVALID, ERROR  | -          | Lone trailing byte of UTF‑8 sequence
| `FFFFFFC0` | -         | `C0`                | UNDERFLOW              | -          | Lone leading byte of 2‑byte UTF‑8 sequence
| `FFFFFFDF` | -         | `DF`                | UNDERFLOW              | -          | Lone leading byte of 2‑byte UTF‑8 sequence
| `FFFFFFE0` | -         | `E0`                | UNDERFLOW              | -          | Lone leading byte of 3‑byte UTF‑8 sequence
| `FFFFFFEF` | -         | `EF`                | UNDERFLOW              | -          | Lone leading byte of 3‑byte UTF‑8 sequence
| `FFFFFFF0` | -         | `F0`                | UNDERFLOW              | -          | Lone leading byte of 4‑byte UTF‑8 sequence
| `FFFFFFF7` | -         | `F7`                | UNDERFLOW              | -          | Lone leading byte of 4‑byte UTF‑8 sequence
| `FFFFFFF8` | -         | `F8`                | UNDERFLOW              | -          | Lone leading byte of 5‑byte UTF‑8 sequence
| `FFFFFFFB` | -         | `FB`                | UNDERFLOW              | -          | Lone leading byte of 5‑byte UTF‑8 sequence
| `FFFFFFFC` | -         | `FC`                | UNDERFLOW              | -          | Lone leading byte of 6‑byte UTF‑8 sequence
| `FFFFFFFD` | -         | `FD`                | UNDERFLOW              | -          | Lone leading byte of 6‑byte UTF‑8 sequence
| `FFFFFFFE` | -         | `FE`                | READY, INVALID, ERROR  | -          | Lone invalid byte in UTF‑8
| `FFFFFFFF` | -         | `FF`                | READY, INVALID, ERROR  | -          | Lone invalid byte in UTF‑8
