"""CPU functionality."""

import sys

class CPU:
    def __init__(self):
        """Construct a new CPU."""
        self.memory = [0] * 256 # holds a maximum of 256 bytes
        self.registers = [0] * 8 # 8 general purpose registers
        self.registers[7] = 0xf4 # this is where the stack will start
        
        self.fl = 0b00000000 # initalize the flag LGE
        self.pc = 0 # program counter
        self.running = False

        # branchtable setup
        self.branchtable = {}
        self.branchtable[0b00000001] = self.hlt
        self.branchtable[0b10000010] = self.ldi
        self.branchtable[0b01000111] = self.prn
        self.branchtable[0b10100010] = self.mul
        self.branchtable[0b01000101] = self.push
        self.branchtable[0b01000110] = self.pop
        self.branchtable[0b01010000] = self.call
        self.branchtable[0b00010001] = self.ret
        self.branchtable[0b10100000] = self.add
        self.branchtable[0b10100111] = self.cmp
        self.branchtable[0b01010101] = self.jeq
        self.branchtable[0b01010110] = self.jne
        self.branchtable[0b01010100] = self.jmp


    # hlp_plz
    def _move_pc(self, ir):
        mv_amt = (self.memory[ir] >> 6) + 1
        self.pc += mv_amt

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
        self.registers[7] -= 1 

        self.memory[self.registers[7]] = self.registers[self.memory[ir + 1]]

    def pop(self, ir):
        self.registers[self.memory[ir + 1]] = self.memory[self.registers[7]]
        self.registers[7] += 1

    def call(self, ir):
        # the address directlly after call instruction is pushed onto the stack
        ret_addr = ir + 2
        self.registers[7] -= 1
        self.memory[self.registers[7]] = ret_addr

        # pc is set to the address in the given register
        # self.pc = self.registers[self.memory[ir + 1]]
        reg_num = self.memory[ir + 1]
        self.pc = self.registers[reg_num]

    def ret(self, ir):
        self.pop(ir)
        self.pc = self.registers[self.memory[ir + 1]]

    def add(self, ir):
        # 2 operands reg1 and reg2
        # store the result in reg1
        self.registers[self.memory[ir + 1]] = self.registers[self.memory[ir + 1]] + self.registers[self.memory[ir + 2]] 

    def cmp(self, ir):
        reg1_num = self.memory[ir + 1]
        reg2_num = self.memory[ir + 2]
        if self.registers[reg1_num] == self.registers[reg2_num]:
            self.fl = 0b00000001
        elif self.registers[reg1_num] < self.registers[reg2_num]:
            self.fl = 0b00000010
        else:
            self.fl = 0b00000100

    def jeq(self, ir):
        # (0b00000000 >> 2) & 1 == L
        # (0b00000000 >> 1) & 1 == G 
        # (0b00000000) & 1 == E
        
        # if the equal flag is true than
        # jump to the address stored at the given register
        if (self.fl >> 2) & 1 == 1:
            reg_num = self.memory[ir + 1]
            self.pc = self.registers[reg_num]
        else:
            self._move_pc(ir)

    def jne(self, ir):
        if self.fl & 1 == 0:
            reg_num = self.memory[ir + 1]
            self.pc = self.registers[reg_num]
        else:
            self._move_pc(ir)

    def jmp(self, ir): # jump to address at given register
        reg_num = self.memory[ir + 1]
        self.pc = self.registers[reg_num]

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
        
    # def alu(self, op, reg_a, reg_b):
    #     """ALU operations."""

    #     if op == "ADD":  
    #         self.reg[reg_a] += self.reg[reg_b]
    #     #elif op == "SUB": etc
    #     else:
    #         raise Exception("Unsupported ALU operation")

    # def trace(self):
    #     """
    #     Handy function to print out the CPU state. You might want to call this
    #     from run() if you need help debugging.
    #     """

    #     print(f"TRACE: %02X | %02X %02X %02X |" % (
    #         self.pc,
    #         #self.fl,
    #         #self.ie,
    #         self.ram_read(self.pc),
    #         self.ram_read(self.pc + 1),
    #         self.ram_read(self.pc + 2)
    #     ), end='')

    #     for i in range(8):
    #         print(" %02X" % self.reg[i], end='')

    #     print()

    def run(self):
        """Run the CPU."""
        self.running = True
        while self.running:
            ir = self.pc

            self.branchtable[self.memory[ir]](ir)

            # if not (self.memory[ir] >> 4) & 1:
            #     mv_amt = (self.memory[ir] >> 6) + 1
            #     self.pc += mv_amt
            if not (self.memory[ir] >> 4) & 1:
                self._move_pc(ir)