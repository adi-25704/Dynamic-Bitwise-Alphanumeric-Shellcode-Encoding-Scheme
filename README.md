# Dynamic-Bitwise-Alphanumeric-Shellcode-Encoding-Scheme


![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Platform](https://img.shields.io/badge/platform-linux--x86-lightgrey.svg) ![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

### Abstract
This repository contains the implementation of a novel **Alphanumeric Shellcode Encoding Scheme** based on dynamic bit-width selection. Unlike traditional encoders (like Alpha3) that use fixed byte-level mapping ($2\times$ expansion), this approach treats the input as a continuous bit stream, dynamically extracting **5 or 6-bit sequences** to map them into valid alphanumeric ASCII ranges.

This method achieves a theoretical redundancy of **36.29%** (closer to the Shannon entropy limit) and outperforms Alpha3 in terms of payload density for shellcodes larger than **295 bytes**.

### Key Features
* **Dynamic Bit-Width Selection:** Adaptively switches between 5-bit and 6-bit extraction to minimize waste.
* **Two-Stage Decoder:** Uses a optimized, bit-accumulating custom decoder stub, which is itself encoded using Alpha3 to ensure the entire payload remains alphanumeric.
* **In-Place Decoding:** The decoder reconstructs the original shellcode directly in memory, overwriting the encoded payload.
* **Higher Efficiency:** Superior compression for large payloads compared to Rix and Alpha3.

### Repository Structure
```text
├── Encode_Decode_Codes/
│   ├── Encoder.c          # Main encoding script (Dynamic Bit-Width logic)
│   └── Encoder.out
|   └── Alphanumeric_Decoder_Without_Alpha3.asm  # Uncompiled assembly code of only the custom decoder without Alpha3 stage
|   └── Alphanumeric_Decoder_Without_Alpha3.bin  # Compiled binary of the decoder stub
|   └── Alphanumeric_Decoder_With_Alpha3.bin    # Compiled binary of the decoder stub
|   └── run.py #python file to combine decoder with encoded payload
├── Final_Encoded_Test_Codes/
│   ├── *_encoded_combined.bin         # Source assembly for the custom decoder stub
│   └── test.c    # Template C code for the decoder stub
│   └── test.out
├── Original_ShellCodes/
|   ├── *.bin  # Raw shellcodes used for evaluation (Modified form of shellcodes taken from Shell-Storm)
└── README.md
```

### Prerequisites
 * Python 3.8+
 * NASM (Netwide Assembler) - for modifying/reassembling the decoder stub.
 * GCC - for compiling the test loaders.
 * Linux Environment (Tested on Ubuntu 24.04 LTS).
   
### Usage
1. Basic Encoding
* To encode a raw shellcode binary file:
```C language
./Encoder.out <shellcode.bin>
```
* The encoded output will be stored in ./temp/*_encoded.bin
2. Prepend the decoder
* To prepend the decoder:
```python
python3 run.py <shellcode_file>
```
* The complete file will be stored as ./output/*_combined.bin along with test.c and test.exe containing the compiled complete code.
3. Testing the Output
* To verify the shellcode works, use the provided C loader:
* Run the exe file generated for each shellcode.
```sh
./test.exe
```

### Performance & Evaluation
We compared this scheme against industry standards (Alpha3 and Rix) and other alphanumeric schemes using shellcodes of varying sizes.
| Sr | Shellcode Name | Orig. | Our Scheme | Alpha3 | A3+AF | Rix+AF | Rix |
|----|----------------|-------|------------|--------|-------|--------|-----|
| 1  | dup2 loop | 20 | 208 | 68 | 162 | 321 | 180 |
| 2  | Shell spawn | 27 | 218 | 82 | 175 | 334 | 175 |
| 3  | Hello World | 51 | 256 | 130 | 216 | 375 | 259 |
| 4  | Execute Command after setreuid | 59 | 264 | 146 | 226 | 385 | 326 |
| 5  | reverse bind shell | 91 | 315 | 210 | 279 | 438 | 560 |
| 6  | Add root with password | 101 | 331 | 230 | 297 | 456 | 591 |
| 7  | copy /etc/passwd to /temp | 110 | 343 | 248 | 310 | 469 | 735 |
| 8  | port bind shell | 204 | 483 | 436 | 460 | 619 | 1382 |
| 9  | append rsa key to /root/.ssh/authorized_keys2 | 295 | 617 | 618 | 500 | 659 | 935 |
| 10 | connect back with ssl | 422 | 810 | 872 | 696 | 855 | 1966 |
| 11 | spawn shell with chmod (777/etc/passwd and /etc/shadow) | 521 | 953 | 1070 | 929 | 1088 | 2341 |
| 12 | knock knock via /dev/dsp + setreuid(0,0) + execve | 566 | 1016 | 1160 | 1082 | 1241 | 3255 |

**Conclusion:** While Alpha3 is efficient for small payloads (due to a smaller decoder stub), our scheme scales better. The "crossover point" is approximately 295 bytes, after which our dynamic bit-width selection yields a smaller total payload. While the combination of Alpha3 and Alpha Freedom (A3+AF) remains competitive at larger sizes, our scheme performs comparably well.

### Technical Details
The Bit-Width Algorithm
The encoder analyzes the next 6 bits of the stream (x_6).
 * Check 6-bit Range: If x_6 \in [0x26, 0x3F], it maps to a-z.
 * Fallback to 5-bit: If not, it analyzes the first 5 bits (x_5).
   * If x_5 \in [0x06, 0x1F], it maps to A-Z.
   * If x_5 \in [0x00, 0x05], it maps to 0-5.
Custom Decoder Stub
The decoder uses a loop with SHL and ADC instructions to reconstruct bytes bit-by-bit in the EAX register. It utilizes optimizations like XCHG instead of MOV and implicit EAX opcodes to reduce the stub size to 74 bytes (before Alpha3 encoding).

### Disclaimer
This tool is intended for educational purposes and security research only. The author is not responsible for any misuse of the code provided in this repository. Ensure you have authorization before testing shellcode on any system.

### References
 [1] Hadrien Barral, Houda Ferradi, Rémi Géraud, Georges-Axel Jaloyan, and David Naccache. **ARMv8 Shellcodes from ‘A’ to ‘Z’.** In *International Conference on Information Security Practice and Experience*, Springer, 2016, pp. 354–377.

[2] A. Basu, A. Mathuria, and N. Chowdhary. **Automatic Generation of Compact Alphanumeric Shellcodes for x86.** In *International Conference on Information Systems Security (ICISS 2014)*, Lecture Notes in Computer Science, Vol. 8880, Springer, 2014, pp. 399–410. doi: https://doi.org/10.1007/978-3-319-13841-1_22

[3] Jian Lin, Guoan Liu, Rui Chang, and Ruimin Wang. **Proteus: An Automatical High-Efficiency Framework for Generating Compact and Printable Shellcode on ARMv8.** In *Proceedings of the 16th International Conference on Internetware*, 2025, pp. 198–208.

[4] Guoan Liu, Jian Lin, Weiyu Dong, Jiaan Liu, and Tieming Liu. **Shortest Printable Shellcode Encoding Algorithm Based on Dynamic Bitwidth Selection.** In *Australasian Conference on Information Security and Privacy*, Springer, 2025, pp. 447–458.

[5] Dhrumil Patel, Aditya Basu, and Anish Mathuria. **Automatic Generation of Compact Printable Shellcodes for x86.** In *14th USENIX Workshop on Offensive Technologies (WOOT ’20)*, 2020.

[6] Rix. **Writing ia32 Alphanumeric Shellcodes.**, *Phrack Magazine*, Issue 57, Article 15, August 2001. https://phrack.org/issues/57/15

[7] J. Salwan, **Shell-Storm: Shellcode Database.** Website, 2008–2025. https://www.shell-storm.org/shellcode/  

[8] SkyLined. **Alpha3 — Alphanumeric Architecture-Agnostic Shellcode Encoder.** Online tool / software release, 2004. https://github.com/SkyLined/alpha3  

[9] Yuanding Zhou. **Least Information Redundancy Algorithm of Printable Shellcode Encoding for x86.** In *European Symposium on Research in Computer Security*, Springer, 2023, pp. 361–376.
