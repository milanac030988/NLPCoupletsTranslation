import subprocess
import time
import os
import sys
import signal
import psutil
from datetime import datetime, timedelta


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class ServiceStatus:
    STARTED = "started"
    STOPPED = "stopped"

class ServiceManager:
    
    def __init__(self):
        self.command = "uvicorn api.service:app --reload"
        self.process = None
        self.status = ServiceStatus.STOPPED
        self.find_existing_process()
        self.start_time = datetime.now()
        
    def find_existing_process(self):
        """
        Kiểm tra xem process với command cụ thể có đang chạy không.
        Nếu có, gán process đó vào thuộc tính self.process.
        """
        for proc in psutil.process_iter(['pid', 'cmdline']):
            try:
                # Kiểm tra nếu command của process giống với command cần tìm
                if proc.info['cmdline'] and self.command in ' '.join(proc.info['cmdline']):
                    self.process = proc
                    print(f"Process '{self.command}' đã tồn tại với PID {proc.pid}.")
                    self.status = ServiceStatus.STARTED
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def start_server(self):
        is_started = self.find_existing_process()
        if not is_started:
            # Start the FastAPI server
            self.process = subprocess.Popen(["uvicorn", "api.service:app", "--reload"])            
            print("API server started.")

        self.start_time = datetime.now()
        self.status = ServiceStatus.STARTED

    def stop_server(self):
        if self.process is not None:
            # Stop the server process
            self.process.send_signal(signal.SIGINT)  # Send SIGINT to gracefully stop the server
            self.process.wait()  # Wait for the process to terminate
            self.process = None
            self.status = ServiceStatus.STOPPED
            print("API server stopped.")

    def get_status(self):
        return self.status

    def get_start_time(self):
        return self.start_time

# Example usage:
if __name__ == "__main__":
    manager = ServiceManager()
    manager.start_server()

    # while True:
    #     cmd = input("Enter 'start' to start the server, 'stop' to stop the server, 'exit' to quit: ")

    #     if cmd == "start":
    #         manager.start_server()
    #     elif cmd == "stop":
    #         manager.stop_server()
    #     elif cmd == "exit":
    #         if manager.process is not None:
    #             manager.stop_server()
    #         break
    #     else:
    #         print("Invalid command.")
