#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#ifdef _WIN32
#include <direct.h>  // For Windows
#else
#include <libgen.h>  // For POSIX systems
#endif
size_t encode_0(uint8_t *data_in, size_t len_in, uint8_t *data_out) {
    uint16_t val = 0;
    size_t bits = 0;
    size_t j = 0;
    for (size_t i = 0; i < len_in; i++) {
        val = (val << 8) | data_in[i];
        bits += 8;
        while (bits >= 7) {
            uint16_t tmp = val >> (bits - 7);
            size_t right_bits = 7;
            if ((tmp >= 0x40) & (tmp < 0x5e)) {
            } else {
                tmp = val >> (bits - 6);
                right_bits = 6;
            }
            data_out[j++] = tmp + 0x20;
            bits -= right_bits;
            val = val & ((1 << bits) - 1);
        }
    }
    if (bits != 0) {
        val = val << (6 - bits);
        data_out[j++] = val + 0x20;
    }
    data_out[j++] = 0x7e;
    return j; 
}
size_t encode(uint8_t *data_in, size_t len_in, uint8_t *data_out) {
    uint16_t val = 0;
    size_t bits = 0;
    size_t j = 0;
    for(size_t i = 0; i < len_in; i++)
    {
        val = (val<<8) | data_in[i];
        bits += 8;
        while (bits >= 6)
        {
            uint16_t tmp = val>>(bits-6); 
            size_t right_bits = 6;
            if((tmp >= 0x26))
            {
                
                data_out[j++] = tmp +0x3b;//tmp [0x26, 0x3f] -> //[0x61, 0x7a]
            }
            else 
            {
                tmp = val>>(bits-5); //tmp [0x00, 0x1f] 
                if((tmp >= 0x06))
                {
                    data_out[j++] = tmp + 0x3b; // [0x06,0x1f] -> [0x41, 0x5a]
                }
                else
                {
                    data_out[j++] = tmp + 0x30; //[0x00,0x05] -> [0x30, 0x35]
                }
                right_bits = 5;
            }
            bits -= right_bits;
            val = val&((1<<bits)-1);
        }
    }
    if(bits != 0)
    {
        val = val<<(5-bits);
        if((val >= 0x06))
        {
            data_out[j++] = val + 0x3b; // [0x06,0x1f] -> [0x41, 0x5a]
        }
        else
        {
            data_out[j++] = val + 0x30; //[0x00,0x05] -> [0x30, 0x35]
        }
    }
    data_out[j++] = 0x39;
    return j;
}
char* remove_extension(const char* filename) {
    const char* last_dot = strrchr(filename, '.');
    const char* last_slash = NULL;

#ifdef _WIN32
    // last_slash = strrchr(filename, '\\');  // Windows path separator
    last_slash = strrchr(filename, '/');  // Windows path separator
#else
    last_slash = strrchr(filename, '/');  // POSIX path separator
#endif

    const char* file_start = (last_slash) ? (last_slash + 1) : filename;

    if (last_dot && (last_dot > last_slash)) {
        size_t len = last_dot - file_start;
        char* result = malloc(len + 1);
        if (result) {
            memcpy(result, file_start, len);
            result[len] = '\0';
        }
        return result;
    }
    return strdup(file_start);
}

char* create_output_filename(const char* input_file) {
    char* file_without_extension = remove_extension(input_file);
    if (!file_without_extension) {
        return NULL;
    }

    size_t new_len = strlen(file_without_extension) + strlen("./temp/_encoded.bin") + 1;
    char* output_filename = malloc(new_len);
    if (!output_filename) {
        free(file_without_extension);
        return NULL;
    }

    snprintf(output_filename, new_len, "./temp/%s_encoded.bin", file_without_extension);
    free(file_without_extension);
    return output_filename;
}
int main(int argc, char *argv[]) {
    
    FILE *fin = fopen(argv[1], "rb");
    if (!fin) {
        perror("Failed to open input file");
        return 1;
    }

    fseek(fin, 0, SEEK_END);
    size_t len_in = ftell(fin);
    fseek(fin, 0, SEEK_SET);

    uint8_t *data_in = malloc(len_in);
    if (!data_in) {
        perror("Failed to allocate memory");
        fclose(fin);
        return 1;
    }

    size_t read_len = fread(data_in, 1, len_in, fin);
    if (read_len != len_in) {
        perror("Failed to read file content");
        free(data_in);
        fclose(fin);
        return 1;
    }
    fclose(fin);

    uint8_t *data_out = malloc(len_in * 2);
    if (!data_out) {
        perror("Failed to allocate memory for output");
        free(data_in);
        return 1;
    }

    size_t len_out = encode(data_in, len_in, data_out);

    // FILE *fout = fopen("shellcode.bin", "wb");
    char* output_file = create_output_filename(argv[1]);
    printf("output_file: %s\n", output_file);

    FILE *fout = fopen(output_file, "wb");
    if (!fout) {
        perror("Failed to open file for writing");
        free(data_in);
        free(data_out);
        return 1;
    }

    size_t write_len = fwrite(data_out, 1, len_out, fout);
    if (write_len != len_out) {
        perror("Failed to write output data");
        free(data_in);
        free(data_out);
        fclose(fout);
        return 1;
    }
    fclose(fout);

    free(data_in);
    free(data_out);

    printf("Encoding completed successfully.\n");
    return 0;
}
