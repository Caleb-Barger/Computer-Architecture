"""CPU functionality."""

import sys

class CPU:
"""
      top of RAM
+-----------------------+
| FF  I7 vector         |    Interrupt vector table
| FE  I6 vector         |
| FD  I5 vector         |
| FC  I4 vector         |
| FB  I3 vector         |
| FA  I2 vector         |
| F9  I1 vector         |
| F8  I0 vector         |
| F7  Reserved          |
| F6  Reserved          |
| F5  Reserved          |
| F4  Key pressed       |    Holds the most recent key pressed on the keyboard
| F3  Start of Stack    |
| F2  [more stack]      |    Stack grows down
| ...                   |
| 01  [more program]    |
| 00  Program entry     |    Program loaded upward in memory starting at 0
+-----------------------+
    bottom of RAM
"""
    def __init__(self):
        """Construct a new CPU."""
        self.memory = [0] * 256 # holds a maximum of 256 bytes
        self.registers = [0] * 8 # 8 general purpose registers
        self.registers[7] = 0xf4 # this is where the stack will start
        
        self.pc = 0 # program counter

        # knows wheather it is running a program or not
        self.running = False

        # branchtable setup
        self.branchtable = {}
        self.branchtable[0b00000001] = self.hlt
        self.branchtable[0b10000010] = self.ldi
        self.branchtable[0b01000111] = self.prn
        self.branchtable[0b10100010] = self.mul
        self.branchtable[0b01000101] = self.push

    # Operation handlers
    def hlt(self, ir):
        self.running = False
    
    def ldi(self, ir):
        operand_a = self.memory[ir + 1]
        operand_b = self.memory[ir + 2]
        self.ram_write(operand_b, operand_a)

    def prn(self, ir):
        operand_a = self.memory[ir + 1]
        print(self.ram_read(operand_a))
    
    def mul(self, ir):
        operand_a = self.memory[ir + 1]
        operand_b = self.memory[ir + 2]
        self.ram_write(self.ram_read(operand_a) * self.ram_read(operand_b), operand_a)

    def push(self, ir):
        # decrement register
        self.registers[7] -= 1 

        # copy the value of sp into register
        self.registers[ir + 1] = self.memory[self.registers[7]] 

    def ram_read(self, MAR): # MAR ( Memory Address Register)
        return self.registers[MAR]
    
    def ram_write(self, MDR, MAR): # MDR ( Memory Data Register )
        self.registers[MAR] = MDR

    def load(self, filename): #TODO MAKE THIS BETTER!!!
        """Load a program into memory."""
        address = 0
        try:
            with open(filename) as f:
                for line in f:
                    line = line.strip()
                    temp = line.split()

                    if len(temp) == 0:
                        continue
                    if temp[0][0] == '#':
                        continue
                    try:
                        self.memory[address] = int(temp[0], 2)
                        # self.memory[address] = bin(int(temp[0], 2))
                    except ValueError:
                        print("Invalid Instruction")
                        sys.exit(1)

                    address += 1

        except FileNotFoundError:
            print(f"could not open {filename}")
            sys.exit(2)
        
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
        self.running = True
        while self.running:
            # Read the value stored in the program counter to the IR 
            # ( IR Instruction Register )
            ir = self.pc

            self.branchtable[self.memory[ir]](ir)

            # increment pc
            # mv_amt = (int(bin(self.memory[ir]), 2) >> 6) + 1
            mv_amt = (self.memory[ir] >> 6) + 1
            self.pc += mv_amt