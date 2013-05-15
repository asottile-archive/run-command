import cStringIO
import subprocess
import sys
import threading

NORMAL = 'NORMAL'
ERROR = 'ERROR'
KILLED_TIME = 'KILLED_TIME'
KILLED_LENGTH = 'KILLED_LENGTH'

class ExecutionOutput:
    def __init__(self):
        self.termination_reason = NORMAL
        self.process = None
        self.output = cStringIO.StringIO()
        self.returncode = -1
        self.exception = None

def run_command(cmd, timeout=sys.maxint, max_length=sys.maxint, stdin=None, **kwargs):
    '''Runs the given cmd and retrieves output somewhat asynchronously.

    Returns termination_reason, return_code, output

        termination_reason is one of NORMAL, KILLED_TIME, KILLED_LENGTH
        return_code is the exit code of the command
        output is the output of the command, if it was trimmed for length it will be trimmed
            to the line before the length was exceeded.

    Args:
        cmd - Array of command arguments to pass.
        timeout - Timeout in seconds to wait for the command to finish.  Default unbounded.
        max_length - Max length in characters of the output to allow. Default unbounded.
        stdin - String of input to stream to the process.
        **kwargs - Passed to Popen.
    '''

    # output will hold the stdout from the process's call.
    try:
        out = ExecutionOutput()

        def execute_command():
            try:
                stdin_param = subprocess.PIPE if stdin else None

                out.process = subprocess.Popen(
                    cmd,
                    stdin=stdin_param,
                    stdout=subprocess.PIPE,
                    **kwargs
                )

                if stdin:
                    out.process.stdin.write(stdin)
                    out.process.stdin.close()

                # Originally this read line by line but if the line had
                #  infinite length then there were bad bad times here.
                try:
                    if max_length == sys.maxint:
                        output = out.process.stdout.read()
                    else:
                        output = out.process.stdout.read(max_length + 1)
                finally:
                    out.output.write(output[:max_length:])

                if len(output) > max_length:
                    out.termination_reason = KILLED_LENGTH
                    out.process.terminate()

                # This is needed to get the return code
                out.process.wait()
            except Exception as e:
                out.exception = e

        thread = threading.Thread(target=execute_command)
        thread.start()

        thread.join(timeout)

        if thread.is_alive():
            out.termination_reason = KILLED_TIME
            out.process.terminate()
            thread.join()

        # In the case we blew up in our thread
        if out.exception:
           return ERROR, -1, repr(out.exception)

        return out.termination_reason, out.process.returncode, out.output.getvalue()
    finally:
        out.output.close()
