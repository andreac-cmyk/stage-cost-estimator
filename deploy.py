#!/usr/bin/env python3
"""Deploy Netflix Studios Stage Cost Estimator to Posit Connect."""
import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("Deploying Netflix Studios Stage Cost Estimator to Posit Connect...")
print("This may take a minute...\n")

result = subprocess.run([
    sys.executable, "-m", "rsconnect", "deploy", "streamlit",
    "--server", "https://posit-connect.prod.netflix.net",
    "--api-key", "KM53LSk2gQmqttwVGHtfs7Ot54hcK9i1",
    "--title", "Netflix Studios Stage Cost Estimator",
    "--entrypoint", "stage_calculator_app.py",
    "--new", "."
])

if result.returncode == 0:
    print("\n✅ Successfully deployed!")
else:
    print(f"\n❌ Deploy failed with code {result.returncode}")

input("\nPress Enter to close...")
