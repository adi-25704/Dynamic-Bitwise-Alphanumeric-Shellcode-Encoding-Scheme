import argparse
import sys
import os

# C 代码模板
# #include <windows.h>
#include <stdio.h>
template_c_code = """
# include <sys/mman.h>
char shellcode[] = "{shellcode}";
int main() { 
    mprotect((void *)((int)shellcode & ~4095), 4096, PROT_READ | PROT_WRITE | PROT_EXEC);
    (*(int (*)())shellcode)();
    return 0;
}
"""
# int main() {
#     // 获取 shellcode 的长度
#     size_t shellcode_len = sizeof(shellcode) - 1;

#     // 使用 VirtualProtect 修改内存保护属性
#     DWORD oldProtect;
#     if (!VirtualProtect(shellcode, shellcode_len, PAGE_EXECUTE_READWRITE, &oldProtect)) {
#         fprintf(stderr, "VirtualProtect failed: %d\\n", GetLastError());
#         return 1;
#     }
#     printf("shellcode now\\n");
#     // 执行 shellcode
#     int (*func)() = (int (*)())shellcode;
#     int result = func();

#     // 恢复原来的内存保护属性
#     if (!VirtualProtect(shellcode, shellcode_len, oldProtect, &oldProtect)) {
#         fprintf(stderr, "VirtualProtect failed: %d\\n", GetLastError());
#         return 1;
#     }

#     return result;
# }
# """

# 读取 .bin 文件
def read_bin_file(filename):
    try:
        # 打开文件
        with open(filename, 'rb') as file:
            # 读取文件内容
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
    # 获取不带扩展名的文件名
    base_name = os.path.splitext(os.path.basename(input_filename))[0]
    # 拼接新的输出文件名
    return f"./output/{base_name}_combined.bin"
def hexlify(e: bytes) -> str:
    res = ""
    for i in e:
        res += "\\x" + format(i, '02x')
    return res

# 检查字节是否在 [0x20, 0x7E] 范围内
def check_bytes_in_range(data: bytes):
    for byte in data:
        if not (0x20 <= byte <= 0x7E):
            raise ValueError(f"Byte {byte:#02x} is out of range [0x20, 0x7E].")

# 生成 C 代码并编译
def generateTemplate(e: bytes):
    shellcode_hex = hexlify(e)
    # print(f"shellcode = {shellcode_hex}")
    temp = template_c_code.replace("{shellcode}", shellcode_hex)
    with open("./output/temp.c", "w") as f:
        f.write(temp)
    os.system("gcc -m32 -no-pie -o ./output/temp.exe ./output/temp.c")

if __name__ == "__main__":
    # 读取编码后shellcode 文件
    # shellcode = read_bin_file("shellcode.bin")
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("Usage: python script.py <shellcode_file>")
        sys.exit(1)
    # 获取传入的文件名
    shellcode_file = sys.argv[1]
    # 读取 shellcode 文件
    shellcode = read_bin_file(shellcode_file)
    # print(f"shellcode = {shellcode}")

    # 读取解码器文件
    decoder_bytes = read_bin_file("Alphanumeric_decoder_Final.bin")
    # print(f"decoder_bytes = {decoder_bytes}")

    # 合并 shellcode 和解码器
    combined_shellcode = decoder_bytes + shellcode
    # print(f"combined_shellcode = {combined_shellcode}")
    # 获取输出文件名
    output_filename = get_output_filename(shellcode_file)
    # 确保输出目录存在
    os.makedirs(os.path.dirname(output_filename), exist_ok=True)
    # 将合并后的二进制数据写入到输出文件中
    with open(output_filename, "wb") as fout:
        fout.write(combined_shellcode)
    print(f"Combined shellcode saved to {output_filename}")

    # 检查 combined_shellcode 的每个字节是否在 [0x20, 0x7E] 范围内
    try:
        check_bytes_in_range(combined_shellcode)
        print("All bytes in combined_shellcode are within the range [0x20, 0x7E].")
    except ValueError as e:
        print(f"Error: {e}")
        # sys.exit(1)

    # 生成 C 代码
    generateTemplate(combined_shellcode)
    print("Generated C code and compiled to temp.exe")