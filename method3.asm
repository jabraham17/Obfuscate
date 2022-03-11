
extern hello
main:
    jmp 0xb ; jump over avx512
    db 0x62 ; avx512 instruction, does garbage but is a newer instructon so may confuse assembler, hides the call label
    db 0x71 
    db 0x45
    db 0x48
    db 0xe3
    db 0x2c
    db 0x25
    mov rax, hello ; move label to register for call
    jmp 0x5 ; jmp over extra byte
    db 0xb8 ; extra byte, tells assembler this is a mov into eax
    call rax ; is 2 bytes long, hidden in mov
    dw 0x9090 ; padding bytes, only required if we want this to be "readable"
