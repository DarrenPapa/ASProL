#!/usr/bin/python
import os, sys, traceback
#		ASProL - Arbitrarily Simple PROgramming Language
#		Version 0.1
#		written by Darren Chase Papa
#		a very simple and complex esoteric programming language
#		with memory handling with the memory array
#		Instruction types:
#			suffix `%` implementable in raw ASProL code
#			suffix `!` impossible to implement in ASProL without changing the interpreter
#			suffix `@` meant to modify the class (the current inter instance)
#			suffix `?` hot stuff (not fully supported)
#			suffix `|` advance memory manipulation
#			no suffix  normal instructions (primary instructions similar to the ones with the suffix `!`)
class inter:
	def __init__(self):
		self._memory = [0]*32000
		self._register = [0]*32
		self._ptrs = {}
		self._allocated = set()
		self._size = {}
		self._jtable = {}
		self._cstack = []
		self._maxc = 1000 # max calls without returning
		self._iters = 0 # keep track of simultaneous calls without returning
		self._togled = False
		self._startv = {}
		self._ptrs_v = {}
	def allocate_mem(self):
		for pos,val in enumerate(self._memory):
			if pos not in self._allocated and val == 0:
				self._allocated.add(pos)
				return pos
		else:
			self.err('[Error]: Allocation failed:\nMemory array is full.')
			return -1
	def get_mem(self,address):
		if not -1 < address < len(self._memory):
			return 0
		return self._memory[address]
	def write_mem(self,address,value):
		if not -1 < address < len(self._memory):
			self._memory = [0]*len(self._memory)
		self._memory[address] = value
	def r_get_mem(self,address):
		if not -1 < address < len(self._register):
			return 0
		return self._register[address]
	def r_write_mem(self,address,value):
		if not -1 < address < len(self._register):
			self._register = [0]*len(self.register_)
		self._register[address] = value
	def switch_mem(self): # togle between registers and memory space (for easier operations)
		ok = self._memory
		self._memory = self._register
		self._register = ok
		self._togled = not self._togled
	def _values(self,args):
		for pos,arg in enumerate(args):
			if arg.startswith('%') and arg[1:].isdigit():                                                            # Memory reference
				args[pos] = self.get_mem(int(arg[1:]))
			elif arg.count('-') <= 1 and arg.replace('-','').isdigit():                                              # Integer
				args[pos] = int(arg)
			elif arg.count('-') <= 1 and arg.count('.') <= 1 and arg.replace('-','').replace('.','').isdigit():      # Float
				args[pos] = float(arg)
			elif arg.startswith('*') and arg[1:] in self._ptrs:                                                      # Pointer's value
				args[pos] = self.get_mem(self._ptrs[arg[1:]])
			elif arg == '~allocate':                                                                                 # Implicit allocation (no control over address)
				args[pos] = self.allocate_mem()
			elif arg.startswith('&') and arg[1:] in self._ptrs:                                                      # Pointer reference
				args[pos] = arg[1:]
			elif arg in self._ptrs:                                                                                  # Pointer address
				args[pos] = self._ptrs[arg]
			elif arg.isidentifier():                                                                                 # Unknown identifier (ignored)
				pass
			elif arg.startswith('"') and arg.endswith('"'):                                                          # Strings [not used by anything (yet)]
				args[pos] = arg[1:-1]
			else:
				self.err('[Error]: Encountered invalid argument: '+arg)
		return tuple(args)
	def get_str(self,address):
		k = ord('×')
		string = ''
		for char in self._memory[address:]:
			if char == k:
				break
			string += chr(char)
		else:
			self.err('[Error]: String never ended with terminator `×`:\nMight be a memory leak.')
		return string
	def get_str_len(self,address):
		k = ord('×')
		string_len = 0
		for char in self._memory[address:]:
			if char == k:
				break
			string_len += 1
		else:
			self.err('[Error]: String never ended with terminator `×`:\nMight be a memory leak.')
		return string_len
	def new_str(self,address,string):
		for pos,char in enumerate(string+'×'):
			self._memory[pos+address] = ord(char)
	def clear_str(self,address):
		k = ord('×')
		for pos,char in enumerate(self._memory[address:]):
			if char == k:
				break
			self._memory[pos+address] = 0
		else:
			self.err('[Error]: String never ended with terminator `×`:\nMight be a memory leak.')
		self._memory[pos+address+1] = 0
	def run(self,code):
		prog = [
			(line.strip() if ';;' not in line else line[:line.index(';;')].strip())
				for line in code.split('\n')]
		self.p = 0
		# Redirecting where the program starts to define data
		# this can also be useful so that subroutine decleration arent at the top of the script
		if "_start-data_" in prog:
			self.p = prog.index("_start-data_")+1
		self._calls = []
		while self.p < len(prog):
			line = prog[self.p]
			if line == '':
				self.p += 1
				continue
			ins, *args = line.split()
			pargs = tuple(map(lambda x:x.strip().replace('\\n','\n').replace('¬¶¬',','),' '.join(args).replace('\\,','¬¶¬').split(',') if args else []))
			args = self._values(list(pargs))
			argc = len(args)
			## Memory operations
			if ins == 'add' and argc == 3:
				mem_addr_a, mem_addr_b, mem_addr_res = args
				self.write_mem(mem_addr_res,mem_addr_a+mem_addr_b)
			elif ins == 'inc' and argc == 1:
				self.write_mem(args[0],self.get_mem(args[0])+1)
			elif ins == 'dec' and argc == 1:
				self.write_mem(args[0],self.get_mem(args[0])-1)
			elif ins == 'sub' and argc == 3:
				mem_addr_a, mem_addr_b, mem_addr_res = args
				self.write_mem(mem_addr_res,mem_addr_a-mem_addr_b)
			elif ins == 'mul' and argc == 3:
				mem_addr_a, mem_addr_b, mem_addr_res = args
				self.write_mem(mem_addr_res,mem_addr_a*mem_addr_b)
			elif ins == 'div' and argc == 3:
				mem_addr_a, mem_addr_b, mem_addr_res = args
				self.write_mem(mem_addr_res,mem_addr_a/mem_addr_b)
			elif ins == 'fdiv' and argc == 3:
				mem_addr_a, mem_addr_b, mem_addr_res = args
				self.write_mem(mem_addr_res,mem_addr_a//mem_addr_b)
			elif ins == 'set' and argc == 2:
				self.write_mem(args[0],args[1])
			elif ins == 'setr' and argc == 2 and self._togled == False:
				self.r_write_mem(args[0],args[1])
			elif ins == 'igt' and argc == 3:
				self.write_mem(args[2],1 if args[0] > args[1] else 0)
			elif ins == 'ilt' and argc == 3:
				self.write_mem(args[2],1 if args[0] < args[1] else 0)
			elif ins == 'ieq' and argc == 3:
				self.write_mem(args[2],1 if args[0] == args[1] else 0)
			elif ins == 'ine' and argc == 3:
				self.write_mem(args[2],1 if args[0] != args[1] else 0)
			## Branching / jumps
			elif ins == 'jiz' and argc == 2:
				self.p = args[1]-1 if args[0] == 0 else self.p
				continue
			elif ins == 'jnz' and argc == 2:
				self.p = args[1]-1 if args[0] != 0 else self.p
				continue
			elif ins == 'jmp' and argc == 1:
				self.p = args[0]-1
				continue
			## Strings
			elif ins == "%sizeof_str" and argc == 2:
				self.write_mem(args[1],self.get_str_len(args[0]))
			elif ins == "%new_string" and argc == 2:
				self.new_str(args[0],args[1])
			elif ins == "%put_string" and argc == 1:
				k = ord('×')
				for char in self._memory[args[0]:]:
					if char == k:
						break
					print(chr(char),end='')
				else:
					self.err('[Error]: String never ended with terminator `×`:\nMight be a memory leak.')
			elif ins == "%str-eq" and argc == 3:
				string0 = self.get_str(args[0])
				string1 = self.get_str(args[1])
				if string0 == string1:
					self.write_mem(args[2],1)
				else:
					self.write_mem(args[2],0)
			elif ins == "%str-ne" and argc == 3:
				string0 = self.get_str(args[0])
				string1 = self.get_str(args[1])
				if string0 != string1:
					self.write_mem(args[2],1)
				else:
					self.write_mem(args[2],0)
			elif ins == "%into_int" and argc == 1:
				string = self.get_str(args[0])
				self.clear_str(args[0])
				self.write_mem(args[0],int(string))
			elif ins == "%str-copy" and argc == 2:
				source = args[0]
				destin = args[1]
				self.new_string(destin,self.get_str(args[0]))
			## Vectors (ints/floats only)
			elif ins == '%new_vector' and argc == 2:
				self._startv[args[0]] = args[1]
				self._ptrs_v[args[0]] = 0
			elif ins == '%append_vector' and argc == 2:
				if not args[0] in self._startv and args[0] in self._ptrs_v:
					self.err('[Error]: Vector doesnt exist or data is missing!')
				self.write_mem(self._startv[args[0]]+self._ptrs_v[args[0]],args[1])
				self._ptrs_v[args[0]] += 1
			elif ins == '%pop_vector' and argc == 2:
				if not args[1] in self._startv and args[1] in self._ptrs_v:
					self.err('[Error]: Vector doesnt exist or data is missing!')
				self._ptrs_v[args[1]] -= 1
				if self._ptrs_v[args[1]] < 0:
					self.err('[Error]: Underflow!')
				self.write_mem(args[0],self.get_mem(self._startv[args[1]]+self._ptrs_v[args[1]]))
				self.write_mem(self._startv[args[1]]+self._ptrs_v[args[1]],0)
			## Subroutines
			elif ins == '!sub' and argc == 1:
				self._jtable[args[0]] = self.p
				while self.p < len(prog):
					if prog[self.p] == '!ret':
						break
					self.p += 1
				else:
					self.err('[Error]: Subroutine comment wasnt closed!')
			elif ins == '!ret' and argc == 0:
				if self._cstack == []:
					self.err('[Error]: Invalid return!')
				self._iters = 0
				self.p = self._cstack.pop()
			elif ins == '!gosub' and argc == 1:
				if self._iters > self._maxc:
					self.err(f'[CRIT ERROR]: RECURSION ERROR IN SUBROUTINE: {args[0]}')
				if args[0] not in self._jtable:
					self.err(f'[Error]: Undefined subroutine: {args[0]}')
				self._iters += 1
				self._cstack.append(self.p)
				self.p = self._jtable.get(args[0],self.p)
			## IO
			elif ins == 'put' and argc != 0:
				for arg in args:
					print(chr(arg),end='')
			elif ins == "%put_value":
				print(*args)
			elif ins == 'ipt' and argc == 1:
				start = args[0]
				chars = input()
				for pos,char in enumerate(chars+'×'):
					self.write_mem(start+pos,ord(char))
			## Advance memory manipulation
			elif ins == "|load_mem" and argc == 1:
				self._memory = [0]*32000
				if os.isfile(args[0]):
					file=open(args[0],'r').read()
					for line in file.split('\n'):
						if line == '':
							continue
						addr, value = line.split()
						try:
							self._memory[int(addr)] = int(value)
						except ValueError:
							self._memory[int(addr)] = float(value)
				del file, line, addr, value
			elif ins == "|save_mem" and argc == 1:
				mem = ''
				for pos,value in enumerate(self._memory):
					if value == 0:
						continue
					mem += f'{pos} {value}\n'
				open(args[0],'w').write(mem)
				del mem, pos, value
			elif ins == "|registers" and argc == 0 and self._togled == False:
				self.switch_mem()
			elif ins == "|memory" and argc == 0 and self._togled == True:
				self.switch_mem()
			## Memory
			elif ins == "!pointer" and argc == 2:
				self._ptrs[args[0]] = args[1]
			elif ins == '!allocate' and argc == 1:     # Explicit allocation (control over memory address to allocate)
				if args[0] not in self._allocated:
					self._allocated.add(args[0])
				else:
					self.err(f'[Error]: Cant allocated allocated memory!')
			elif ins == "%malloc" and argc == 3:       # Also explicit allocation
				self._ptrs[args[2]] = args[0]
				self._size[args[2]] = args[1]
				for pos in range(args[1]+1):
					if args[0]+pos in self._allocated:
						self.err('[Error]: Can not allocate allocated memory!\nOverlap in allocation!')
					self._allocated.add(args[0]+pos)
			elif ins == "%auto_malloc" and argc == 2: # Implicit allocation (the starting address cannot be manually controlled)
				start = self.allocate_mem()
				self._ptrs[args[1]] = start
				self._size[args[1]] = args[0]
				for pos in range(1,args[0]+1):
					if start+pos in self._allocated:
						self.err('[Error]: Can not allocate allocated memory!\nOverlap in allocation!')
					self._allocated.add(start+pos)
			elif ins == "%free_malloc" and argc == 1: # Used for chunks of memory allocated by !malloc or %auto-malloc
				start = self._ptrs.get(args[0])
				size = self._size.get(args[0])
				for pos in range(size):
					if start+pos not in self._allocated:
						self.err('[Error]: Tried to free unallocated memory:\nMemory mught have been corrupted or fragmented!')
					self._allocated.remove(start+pos)
			elif ins == "!free" and argc == 1:        # Used to free singular memory addresses allocated by !allocate or by assigning ~allocate to a pointer
				if args[0] in self._allocated:
					self._allocated.remove(args[0])
				else:
					self.err('[Error]: Tried to free unallocated memory.')
			elif ins == "!forget" and argc == 1:
				if args[0] in self._ptrs:
					self._ptrs.pop(args[0])
				else:
					self.err('[Error]: Tried to forget undeclared pointer.')
			elif ins == '@purge_memory' and argc == 0:
				self._memory = [0]*32000
			elif ins == "@purge_all":
				self._memory = [0]*32000
				self._ptrs = {}
				self._allocated = set()
				self._size = {}
			## Miscalleneous
			elif ins == 'hlt' and argc == 0:
				exit()
			elif ins.startswith(';['):
				while self.p < len(prog):
					if prog[self.p] == '];':
						break
					self.p += 1
				else:
					self.err('[Error]: Multi-line comment wasnt closed!')
			## Redirecting
			elif ins == '_end-data_':
				self.p = 0
				continue
			elif ins == '_start-data_':
				self.err('[Error]: Can only redirect once!')
			else:
				self.err('[Error]: Invalid instruction: '+ins)
			self.p += 1
			self._calls.append((ins,(*args,),(*pargs,)))
	def err(self,msg=''):
		print('Most recent call last:')
		for pos,[ins,args,pargs] in enumerate(self._calls):
			if args != tuple() and pargs != tuple():
				print(f'Instruction [{str(pos).zfill(6)}]: {ins}\n   Unprocessed arguments: {pargs}\n     Processed arguments: {args}')
			else:
				print(f'Instruction [{str(pos).zfill(6)}]: {ins}\n     No arguments')
		print('======== [ Details ] ========\n'+msg+f'\nAt line {(self.p+1 if type(self.p) == int else self.p)}')
		sys.exit()
	def exit(self,msg=''):
		sys.exit(msg)
if len(sys.argv) < 2:
	kk = inter()
	kk.exit = lambda x:print(x)
	kk.err = kk.exit
	print('ASProL - REPL [0.1] Might be slower due to argument handling.')
	while True:
		act = input('Code >> ')
		if act == "exit":
			exit('[Done]')
		elif act in kk._ptrs:
			print(f'[REPL]  POINTER: {act} -> {kk._ptrs[act]}'+(': [ALLOCATED]' if kk._ptrs[act] in kk._allocated else ''))
		else:
			kk.run(act)
if not os.path.isfile(sys.argv[1]):
	exit('[Error]: Argument one must be file!')
ok = inter()
try:
	ok.run(open(sys.argv[1],'r').read())
except SystemExit:
	sys.exit()
except KeyboardInterrupt:
	print('[Exited]')
	sys.exit()
except:
	print(' [ INTERPRETER ERROR ] '.center(88,'#'))
	ok.err(traceback.format_exc())
