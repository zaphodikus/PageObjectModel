import subprocess
import threading
import io


class WebServer(object):

    stdout_result = 1
    stderr_result = 1
    stop = False
    stdout_buffer = io.StringIO()
    stderr_buffer = io.StringIO()

    def stdout_thread(self, pipe):
        #global stdout_result
        while True:
            out = pipe.stdout.read(1)
            WebServer.stdout_result = pipe.poll()
            if out == [] and WebServer.stdout_result is not None:
                break

            if out != []:
                #sys.stdout.write("".join(chr(x) for x in out))
                #sys.stdout.flush()
                WebServer.stdout_buffer.write("".join(chr(x) for x in out))
            if WebServer.stop:
                print("== STDOUT ==")
                WebServer.stdout_buffer.seek(0)
                print(WebServer.stdout_buffer.read())
                break

    def stderr_thread(self, pipe):
        while True:
            err = pipe.stderr.read(1)
            WebServer.stderr_result = pipe.poll()
            if err == [] and WebServer.stderr_result is not None:
                break

            if err != []:
                #sys.stderr.write("".join(chr(x) for x in err))
                #sys.stderr.flush()
                WebServer.stderr_buffer.write("".join(chr(x) for x in err))

            if WebServer.stop:
                print("== STDERR ==")
                WebServer.stderr_buffer.seek(0)
                print(WebServer.stderr_buffer.read())
                break

    def exec_command(self, command, cwd=None):
        if cwd is not None:
            print
            '[' + ' '.join(command) + '] in ' + cwd
        else:
            print
            '[' + ' '.join(command) + ']'

        self.p = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd
        )


        self.out_thread = threading.Thread(name='stdout_thread', target=self.stdout_thread, args=(self.p,))
        self.err_thread = threading.Thread(name='stderr_thread', target=self.stderr_thread, args=(self.p,))

        self.err_thread.start()
        self.out_thread.start()

    def terminate_command(self):
        self.p.terminate()
        WebServer.stop = True
        self.out_thread.join()
        self.err_thread.join()

