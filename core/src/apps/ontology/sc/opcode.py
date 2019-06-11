# OpCode constants
PUSH0 = 0x00  # An empty array of bytes is pushed onto the stack.
PUSHBYTES75 = 0x4B
PUSHDATA1 = (
    0x4C
)  # The next byte contains the number of bytes to be pushed onto the stack.
PUSHDATA2 = (
    0x4D
)  # The next two bytes contain the number of bytes to be pushed onto the stack.
PUSHDATA4 = (
    0x4E
)  # The next four bytes contain the number of bytes to be pushed onto the stack.
PUSHM1 = 0x4F  # The number -1 is pushed onto the stack.
PUSH1 = 0x51  # The number 1 is pushed onto the stack.

# Flow control
SYSCALL = 0x68
DUPFROMALTSTACK = 0x6A

# Stack
TOALTSTACK = (
    0x6B
)  # Puts the input onto the top of the alt stack. Removes it from the main stack.
FROMALTSTACK = (
    0x6C
)  # Puts the input onto the top of the main stack. Removes it from the alt stack.
SWAP = 0x7C  # The top two items on the stack are swapped.

# Array
PACK = 0xC1
NEWSTRUCT = 0xC6
APPEND = 0xC8
