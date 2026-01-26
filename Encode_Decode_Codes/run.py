import argparse
import sys
import os

# C code template with placeholder for shellcode
# Type python3 run.py <shellcode_file> to generate a combined shellcode file and C code
# Here shellcode file is the encoded shellcode which comes as an output from Encoder.c file.

template_c_code = """
# include <sys/mman.h>
char shellcode[] = "{shellcode}";
int main() { 
    mprotect((void *)((int)shellcode & ~4095), 4096, PROT_READ | PROT_WRITE | PROT_EXEC);
    (*(int (*)())shellcode)();
    return 0;
}
"""
def read_bin_file(filename):
    try:

        with open(filename, 'rb') as file:
            data = file.read()
            return data
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None
    except PermissionError:
        print(f"Error: Permission denied to read '{filename}'.")
        return None
    except Exception as e:
        print(f"Error: An unexpected error occurred while reading '{filename}': {e}")
        return None
def get_output_filename(input_filename):

    base_name = os.path.splitext(os.path.basename(input_filename))[0]
    return f"./output/{base_name}_combined.bin"
def hexlify(e: bytes) -> str:
    res = ""
    for i in e:
        res += "\\x" + format(i, '02x')
    return res

def check_bytes_in_range(data: bytes):
    for byte in data:
        if not (0x20 <= byte <= 0x7E):
            raise ValueError(f"Byte {byte:#02x} is out of range [0x20, 0x7E].")

def generateTemplate(e: bytes):
    shellcode_hex = hexlify(e)

    temp = template_c_code.replace("{shellcode}", shellcode_hex)
    with open("./output/test.c", "w") as f:
        f.write(temp)
    os.system("gcc -m32 -no-pie -o ./output/test.exe ./output/test.c")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script.py <shellcode_file>")
        sys.exit(1)
    shellcode_file = sys.argv[1]

    shellcode = read_bin_file(shellcode_file)

    decoder_bytes = read_bin_file("Alphanumeric_Decoder_With_Alpha3.bin")

    combined_shellcode = decoder_bytes + shellcode

    output_filename = get_output_filename(shellcode_file)
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    with open(output_filename, "wb") as fout:
        fout.write(combined_shellcode)
    print(f"Combined shellcode saved to {output_filename}")

    try:
        check_bytes_in_range(combined_shellcode)
        print("All bytes in combined_shellcode are within the range [0x20, 0x7E].")
    except ValueError as e:
        print(f"Error: {e}")

    generateTemplate(combined_shellcode)
    print("Generated C code and compiled to test.exe")