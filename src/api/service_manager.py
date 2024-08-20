import subprocess
import time
import os
import sys
import signal

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class ServiceManager:
    def __init__(self):
        self.process = None

    def start_server(self):
        if self.process is None:
            # Start the FastAPI server
            self.process = subprocess.Popen(["uvicorn", "api.service:app", "--reload"])
            print("API server started.")

    def stop_server(self):
        if self.process is not None:
            # Stop the server process
            self.process.send_signal(signal.SIGINT)  # Send SIGINT to gracefully stop the server
            self.process.wait()  # Wait for the process to terminate
            self.process = None
            print("API server stopped.")

# Example usage:
if __name__ == "__main__":
    manager = ServiceManager()

    while True:
        cmd = input("Enter 'start' to start the server, 'stop' to stop the server, 'exit' to quit: ")

        if cmd == "start":
            manager.start_server()
        elif cmd == "stop":
            manager.stop_server()
        elif cmd == "exit":
            if manager.process is not None:
                manager.stop_server()
            break
        else:
            print("Invalid command.")
