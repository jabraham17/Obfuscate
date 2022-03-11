
extern hello
main:
    mov rax, hello ; move label to register for call
    jmp 0x5 ; jmp over extra byte
    db 0xb8 ; extra byte, tells assembler this is a mov into eax
    call rax ; is 2 bytes long, hidden in mov
    dw 0x9090 ; padding bytes, only required if we want this to be "readable"
