import subprocess
import os
import sys
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
if SOURCE not in sys.path:
    sys.path.append(SOURCE)
   #  print(sys.path)
env = os.environ.copy()
env["PYTHONPATH"] = os.pathsep.join(sys.path)
print(env.get("REFS_DIR"))
if __name__ == "__main__":
   process = subprocess.Popen(['streamlit', 'run', MAIN_PAGE], env=env)
