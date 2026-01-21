# Dynamic-Bitwise-Alphanumeric-Shellcode-Encoding-Scheme



Here is a comprehensive README.md file tailored to your repository. It incorporates the technical details, the unique two-stage decoding mechanism, and the experimental results from the text you provided.
You can copy and paste this directly into your repository.
# Dynamic Bit-Width Alphanumeric Shellcode Encoder

![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Platform](https://img.shields.io/badge/platform-linux--x86-lightgrey.svg) ![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)

## 📜 Abstract
This repository contains the implementation of a novel **Alphanumeric Shellcode Encoding Scheme** based on dynamic bit-width selection. Unlike traditional encoders (like Alpha3) that use fixed byte-level mapping ($2\times$ expansion), this approach treats the input as a continuous bit stream, dynamically extracting **5 or 6-bit sequences** to map them into valid alphanumeric ASCII ranges.

This method achieves a theoretical redundancy of **36.29%** (closer to the Shannon entropy limit) and outperforms Alpha3 in terms of payload density for shellcodes larger than **295 bytes**.

## 🚀 Key Features
* **Dynamic Bit-Width Selection:** Adaptively switches between 5-bit and 6-bit extraction to minimize waste.
* **Two-Stage Decoder:** Uses a highly optimized, bit-accumulating custom decoder stub, which is itself encoded using Alpha3 to ensure the entire payload remains alphanumeric.
* **In-Place Decoding:** The decoder reconstructs the original shellcode directly in memory, overwriting the encoded payload.
* **High Efficiency:** Superior compression for large payloads compared to Rix and Alpha3.

## 📂 Repository Structure

```text
├── encoder/
│   ├── encoder.py          # Main encoding script (Dynamic Bit-Width logic)
│   └── alpha3.py           # Alpha3 implementation for the second stage
├── decoder/
│   ├── decoder.asm         # Source assembly for the custom decoder stub
│   └── decoder_template.bin # Compiled binary of the decoder stub
├── tests/
│   ├── shellcodes/         # Raw shellcodes used for evaluation (from Shell-Storm)
│   ├── loaders/            # C programs to test/execute the generated shellcode
│   └── validation_script.py # Automated test runner
└── README.md

🛠️ Prerequisites
 * Python 3.x
 * NASM (Netwide Assembler) - for modifying/reassembling the decoder stub.
 * GCC - for compiling the test loaders.
 * Linux Environment (Tested on Ubuntu 24.04 LTS).
💻 Usage
1. Basic Encoding
To encode a raw shellcode binary file:
python3 encoder/encoder.py --input tests/shellcodes/execve.bin --output payload.txt

2. The Two-Stage Process (Internal Logic)
The encoder performs the following steps automatically:
 * Bit-Stream Encoding: The raw shellcode is encoded into an alphanumeric string P using the dynamic 5/6-bit algorithm.
 * Decoder Prep: The custom decoder.bin is prepended to P.
 * Stub Encoding: The custom decoder binary is passed through Alpha3 to make the decoder itself alphanumeric.
 * Final Output: [Alpha3 Encoded Stub] + [Dynamic Encoded Payload]
3. Testing the Output
To verify the shellcode works, use the provided C loader:
# Compile the loader
gcc -z execstack -fno-stack-protector tests/loaders/loader.c -o loader

# Run with your payload
./loader "$(cat payload.txt)"

📊 Performance & Evaluation
We compared this scheme against industry standards (Alpha3 and Rix) using shellcodes of varying sizes.
| Shellcode Name | Original Size | Our Scheme | Alpha3 | Rix |
|---|---|---|---|---|
| Hello World | 51 bytes | 256 | 130 | 259 |
| Reverse Bind Shell | 91 bytes | 315 | 210 | 560 |
| Connect Back SSL | 422 bytes | 810 | 872 | 1966 |
| Knock Knock + Execve | 566 bytes | 1016 | 1160 | 3255 |
Conclusion: While Alpha3 is efficient for small payloads (due to a smaller decoder stub), our scheme scales better. The "crossover point" is approximately 295 bytes, after which our dynamic bit-width selection yields a smaller total payload.
🧠 Technical Details
The Bit-Width Algorithm
The encoder analyzes the next 6 bits of the stream (x_6).
 * Check 6-bit Range: If x_6 \in [0x26, 0x3F], it maps to a-z.
 * Fallback to 5-bit: If not, it analyzes the first 5 bits (x_5).
   * If x_5 \in [0x06, 0x1F], it maps to A-Z.
   * If x_5 \in [0x00, 0x05], it maps to 0-5.
Custom Decoder Stub
The decoder uses a loop with SHL and ADC instructions to reconstruct bytes bit-by-bit in the EAX register. It utilizes optimizations like XCHG instead of MOV and implicit EAX opcodes to reduce the stub size to 74 bytes (before Alpha3 encoding).
⚠️ Disclaimer
This tool is intended for educational purposes and security research only. The author is not responsible for any misuse of the code provided in this repository. Ensure you have authorization before testing shellcode on any system.
📚 References
 * Alpha3: SkyLined, "Alpha3 - Alphanumeric Shellcode Encoder."
 * Rix: "Writing IA32 Alphanumeric Shellcodes," Phrack Magazine, Issue 57.
 * Key1: Liu et al., "Shortest Printable Shellcode Encoding Algorithm Based on Dynamic Bitwidth Selection," 2025.
<!-- end list -->

