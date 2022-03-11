
extern hello
main:
    push r10 ; save register we are going to use, we can mess this up according to calling convention
    mov r10, hello ; move label to register for call
    jmp 0x5 ; jmp over extra byte
    db 0xe9 ; extra byte, tells assembler this is a jmp
    call r10 ; is 3 bytes long beacuse we use an extended register, completely hidden in jmp imm
    pop r10 ; shows up as pop rdx, as the first byte gets included in the jmp imm
