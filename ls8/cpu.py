"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.memory = [] # holds a maximum of 256 bytes
        self.registers = [0] * 8 # 8 general purpose registers

        self.pc = 0 # program counter

        # knows wheather it is running a program or not
        self.running = False

        # branchtable setup
        self.branchtable = {}
        self.branchtable[0b00000001] = self.hlt
        self.branchtable[0b10000010] = self.ldi
        self.branchtable[0b01000111] = self.prn
        self.branchtable[0b10100010] = self.mul

        # initalize the stack
        self.stack = Stack()

    # Operation handlers
    def hlt(self, ir):
        self.running = False
    
    def ldi(self, ir):
        operand_a = self.memory[ir + 1]
        operand_b = self.memory[ir + 2]
        self.ram_write(operand_b, operand_a)
        self.pc += 3

    def prn(self, ir):
        operand_a = self.memory[ir + 1]
        print(self.ram_read(operand_a))
        self.pc += 2
    
    def mul(self, ir):
        operand_a = self.memory[ir + 1]
        operand_b = self.memory[ir + 2]
        self.ram_write(self.ram_read(operand_a) * self.ram_read(operand_b), operand_a)
        self.pc += 3

    def ram_read(self, MAR): # MAR ( Memory Address Register)
        return self.registers[MAR]
    
    def ram_write(self, MDR, MAR): # MDR ( Memory Data Register )
        self.registers[MAR] = MDR

    def load(self, filename):
        """Load a program into memory."""
        # Read in filename's content
        with open(filename, 'r') as f:
            lines = f.readlines()

        instructions = []
        for elm in lines:
            temp = elm.split()
            instructions.append((int(temp[0], 2)))

        print(instructions)

        self.memory = instructions # this works for now?
        
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
