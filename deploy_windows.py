"""Double-click this file to deploy Netflix Studios Stage Estimator to Posit Connect."""
import subprocess, sys, os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Installing rsconnect...")
subprocess.check_call([sys.executable, "-m", "pip", "install", "rsconnect-python", "-q"])

print("Deploying to Posit Connect...")
subprocess.check_call([
    sys.executable, "-m", "rsconnect", "deploy", "streamlit",
    "--server", "https://posit-connect.prod.netflix.net",
    "--api-key", "KM53LSk2gQmqttwVGHtfs7Ot54hcK9i1",
    "--title", "Netflix Studios Stage Estimator",
    "--entrypoint", "stage_calculator_app.py",
    "--new", "."
])

print("\n✅ Done! Your permanent URL is printed above.")
input("Press Enter to close...")
