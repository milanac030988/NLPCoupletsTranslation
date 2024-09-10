import subprocess
import os
import sys
import argparse
from src.data.download_data_models import download_data
# def signal_handler(sig, frame, obj):
#    """
# Handle signals from the operating system.

# **Arguments:**

# * ``sig``

#   / *Condition*: required / *Type*: int /

#   The signal number received from the OS.

# * ``frame``

#   / *Condition*: required / *Type*: frame object /

#   The current stack frame.

# * ``obj``

#   / *Condition*: required / *Type*: object /

#   The object that is handling the signal.

# **Returns:**

# (*no returns*)
#    """
#    # This function will be called when a SIGINT signal (Ctrl+C) is received
#    print("Ctrl+C pressed - Cleaning up...")
#    print(f"Signal {sig} received, performing cleanup...")
#    with open("D:\\testlog.txt", "a") as test:
#         test.write("=======> Cleaning up...")
#    # Perform any necessary cleanup here
#    # For example, call the cleanup method of the object
#    del obj
#    # Exit the program
#    exit(0)
# scripts_path = os.path.join(os.path.dirname(sys.executable), 'Scripts')
# os.environ['PATH'] += os.pathsep + scripts_path

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SOURCE = os.path.join(SCRIPT_DIR, 'src')
MAIN_PAGE = os.path.join(SCRIPT_DIR, "src/gui/main_page.py")
SERVICE_API_MANAGER = os.path.join(SCRIPT_DIR, "src/api/service_manager.py")
DOWNLOAD_SCRIPT = os.path.join(SCRIPT_DIR, "src/data/download_data_models.py")

if SOURCE not in sys.path:
    sys.path.append(SOURCE)
   #  print(sys.path)
env = os.environ.copy()
env["PYTHONPATH"] = os.pathsep.join(sys.path)
print(env.get("REFS_DIR"))

def parse_arguments():
   # Initialize the argument parser
   parser = argparse.ArgumentParser(description="Download raw data và models.")
    
   # Define command-line arguments
   parser.add_argument('--download-data', action='store_true', default=False,  help="Cần download data về.")
   
   # Parse the arguments
   args = parser.parse_args()

   # Return parsed arguments
   return args

if __name__ == "__main__":
   print("start app translation")
   download_data()   
   run_type = os.environ.get("RUNTYPE", "webapp")
   
   if run_type == "webapp":
      web_app_port = os.environ.get("PORT", "8501")
      web_app_address = os.environ.get("ADDRESS", "0.0.0.0")
      subprocess.run(['streamlit', 'run', MAIN_PAGE, f"--server.address={web_app_address}", f"--server.port={web_app_port}"], env=env)
   else:
      subprocess.run(['python', SERVICE_API_MANAGER], env=env)
   # output, error = app_proc.communicate()
   # if app_proc.returncode != 0: 
   #    print(f"Exit with code: {app_proc.returncode}")
