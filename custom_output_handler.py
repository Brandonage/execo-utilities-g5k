# A simple handler for a process to print a pair of: host and process's stdout

from execo import ProcessOutputHandler

class PyConsoleOutputHandler(ProcessOutputHandler):
   def read_line(self, process, stream, string, eof, error):
       print(str(process.host) + ':' + string)