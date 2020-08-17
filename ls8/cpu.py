"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.memory = [] # holds a maximum of 256 bytes
        self.registers = [0] * 8 # 8 general purpose registers

        self.pc = 0 # program counter

    def ram_read(self, MAR): # MAR ( Memory Address Register)
        return self.registers[MAR]
    
    def ram_write(self, MDR, MAR): # MDR ( Memory Data Register )
        self.registers[MAR] = MDR

    def load(self):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:
        
        program = [
            # From print8.ls8
            0b10000010, # LDI R0,8
            0b00000000,
            0b00001000,
            0b01000111, # PRN R0
            0b00000000,
            0b00000001, # HLT
        ]

        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        # Read the value stored in the program counter to the IR 
        # ( IR Instruction Register )

        ir = self.pc

        # depending on the last 2 digits in a given opcode increment pc by that amt
        # read the last 2 digits of the ir 
        opcode = [int(n) for n in str(ir).strip()]

        if opcode[0] == 1:
            operand_a = self.memory[ir + 1]
            pc_move_amt = 2
 
        elif opcode[1] == 1:
            operand_a = self.memory[ir + 1]
            operand_b = self.memory[ir + 2]
            pc_move_amt = 3


        if self.memory[ir] == 0b00000001: # HLT
            running = False

        elif self.memory[ir] == 0b10000010: # LDI
            self.ram_write(operand_b, operand_a)