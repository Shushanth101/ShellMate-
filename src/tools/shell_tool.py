import sys
import os
import threading
import uuid
import time
import re


if sys.platform == "win32":
    try:
        import winpty
    except ImportError:
        pass

def strip_ansi(text):
    """
    More robust ANSI stripping using a comprehensive regex.
    """
    if not text:
        return ""
    
    ansi_regex = r'(?:\x1B[@-_]|[\x80-\x9F])[0-?]*[ -/]*[@-~]|\x1B\][^\x07\x1B]*[\x07\x1B]|\x1B[()]?[A-Z0-9]'
    text = re.sub(ansi_regex, '', text)
    
    # Final cleanup of any stray escape chars or bracket residues
    text = text.replace('\x1B', '').replace('\u001b', '')
    # Remove carriage returns and handle line endings properly
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    return text

class ShellTool:
    """
    A single class to manage interactive shell sessions (WinPTY on Windows, PTY on Linux/Mac).
    It manages background reading, ANSI stripping, and output buffering.
    """
    def __init__(self):
        self.processes = {}  
        self.shell = "powershell.exe" if sys.platform == "win32" else "bash"

    def run_command(self, command_line, cwd=None):
        """
        Executes a command in a persistent shell session.
        """
        command_id = str(uuid.uuid4())
        
        if cwd is None:
            cwd = os.getcwd()

        try:
            if sys.platform == "win32":
                # Windows: WinPTY
                p = winpty.PtyProcess.spawn(self.shell, cwd=cwd)
            else:
                # POSIX: pty
                import pty
                
                master_fd, slave_fd = pty.openpty()
                pid = os.fork()
                if pid == 0:
                    os.chdir(cwd)
                    os.execvp(self.shell, [self.shell])
                else:
                    p = {
                        "pid": pid,
                        "fd": master_fd
                    }

            # Prepare process state
            process_state = {
                "id": command_id,
                "platform_process": p,
                "status": "running",
                "buffer": "",
                "lock": threading.Lock()
            }
            self.processes[command_id] = process_state

            # Start reader thread
            t = threading.Thread(target=self._reader_thread, args=(command_id,), daemon=True)
            t.start()
            
            # Send the initial command
            newline = "\r\n" if sys.platform == "win32" else "\n"
            self.send_command_input(command_id, command_line + newline)

            return {
                "commandId": command_id,
                "status": "running"
            }

        except Exception as e:
            return {"error": str(e)}

    def _reader_thread(self, command_id):
        """
        Reads from the PTY, strips ANSI, and appends to the buffer.
        """
        state = self.processes.get(command_id)
        if not state:
            return
            
        p = state["platform_process"]

        try:
            while True:
                data = None
                if sys.platform == "win32":
                    if not p.isalive():
                        break
                    # WinPTY read returns text
                    try:
                        data = p.read(1024)
                    except Exception:
                        break
                else:
                    import select
                    # Check if data is available
                    rlist, _, _ = select.select([p["fd"]], [], [], 0.1)
                    if rlist:
                        raw_data = os.read(p["fd"], 1024)
                        if isinstance(raw_data, bytes):
                             data = raw_data.decode(errors="ignore")
                    else:
                        # No data, continue loop
                        continue
                
                if data:
                    # Strip ANSI immediately
                    clean_data = strip_ansi(data)
                    with state["lock"]:
                        state["buffer"] += clean_data
                else:
                    # If read returned empty but process alive, small sleep
                    time.sleep(0.05)

        except Exception as e:
            with state["lock"]:
                state["buffer"] += f"\n[Internal Error: {e}]\n"
        finally:
            state["status"] = "terminated"

    def get_command_status(self, command_id, char_limit=1000):
        """
        Returns the command status and the tail of the output buffer.
        """
        state = self.processes.get(command_id)
        if not state:
            return {"error": f"Process {command_id} not found"}

        with state["lock"]:
            full_output = state["buffer"]
            status = state["status"]
            
        if len(full_output) > char_limit:
            output_chunk = full_output[-char_limit:]
        else:
            output_chunk = full_output

        return {
            "commandId": command_id,
            "status": status,
            "output": output_chunk
        }

    def send_command_input(self, command_id, input_text):
        """
        Sends text to the running process.
        """
        state = self.processes.get(command_id)
        if not state or state["status"] != "running":
            return {"error": "Process not found or already finished"}
        
        # Heuristic: if input looks like text (not special keys), ensure newline
        if not input_text.startswith("\x1b"):
             if not input_text.endswith("\n") and not input_text.endswith("\r"):
                 input_text += "\n"
        
        # WinPTY prefers \r\n
        if sys.platform == "win32" and not input_text.startswith("\x1b"):
             input_text = input_text.replace("\n", "\r\n")

        p = state["platform_process"]
        try:
            if sys.platform == "win32":
                p.write(input_text)
            else:
                os.write(p["fd"], input_text.encode())
            return {"success": True}
        except Exception as e:
            return {"error": str(e)}

    def terminate_command(self, command_id):
        """
        Terminates the shell process.
        """
        state = self.processes.get(command_id)
        if not state:
            return {"error": "Process not found"}
            
        p = state["platform_process"]
        
        try:
            if sys.platform == "win32":
                p.close()
            else:
                import signal
                os.kill(p["pid"], signal.SIGTERM)
                os.close(p["fd"])
        except Exception:
            pass
            
        state["status"] = "terminated"
        return {"success": True}

    def read_terminal(self, command_id):
        """
        Returns the entire output buffer.
        """
        state = self.processes.get(command_id)
        if not state:
            return {"error": f"Process {command_id} not found"}
        
        with state["lock"]:
            raw_output = state["buffer"]
            
        return {
            "commandId": command_id,
            "output": raw_output,
            "raw_length": len(raw_output)
        }