import subprocess
import os
import sys
import argparse
from src.data.download_data_models import download_data


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
   
   download_data()   
   run_type = os.environ.get("RUNTYPE", "webapp")
   
   if run_type == "webapp":
      web_app_port = os.environ.get("PORT", "8501")
      web_app_address = os.environ.get("ADDRESS", "0.0.0.0")
      print(f"[->] Khởi chạy Translation Webapp tại {web_app_address}:{web_app_port}...")
      subprocess.run(['streamlit', 'run', MAIN_PAGE, f"--server.address={web_app_address}", f"--server.port={web_app_port}"], env=env)
   else:
      print(f"[->] Khởi chạy Translation service...")
      subprocess.run([sys.executable, SERVICE_API_MANAGER], env=env)
   # output, error = app_proc.communicate()
   # if app_proc.returncode != 0: 
   #    print(f"Exit with code: {app_proc.returncode}")
