# -*- coding: utf-8 -*-
import readline

class AutoCompletion(object):
	def __init__(self):
		self.setup()
	def setup(self):
		readline.set_completer(self.complete)
		readline.parse_and_bind('tab: complete')
		readline.set_completer_delims(' \t\n;')
		readline.parse_and_bind('set enable-keypad on')
	def complete(self, text, state):
		if state == 0:
			original_line = readline.get_line_buffer()
			line = original_line.lstrip()
			stripped = len(original_line) - len(line)
			start_index = readline.get_begidx() - stripped
			end_index = readline.get_endidx() - stripped
			if start_index > 0:
				cmd, args = self.parse_line(line)
			else:
				complete_func = self.raw_command_completer
			self.completion_matches = complete_func(text, line, start_index, end_index)
		try:
			return self.completion_matches[state]
		except:
			return None
	
	def raw_command_completer(self, text, line, start_index, end_index):
		return filter(lambda entry: entry.startswith(text), self.suggested_commands())
	
	def completer(self, *ignored):
		return []
	def suggested_commands(self, *ignored):
		return [command.rsplit("_").pop() for command in dir(self) if command.startswith("cmd_")]
	def parse_line(self, cmd_line):
		cmd, _, arg = cmd_line.strip().partition(" ")
		return cmd, arg.strip()
