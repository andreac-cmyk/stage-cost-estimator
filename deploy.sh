#!/bin/bash
# Netflix Studios Stage Estimator — One-click deploy to Posit Connect
# Run this from the same folder as stage_calculator_app.py

echo "🎬 Deploying Netflix Studios Stage Estimator..."
echo ""

# Check if rsconnect is installed
if ! command -v rsconnect &> /dev/null; then
    echo "Installing rsconnect-python..."
    pip install rsconnect-python
fi

# Deploy
rsconnect deploy streamlit \
  --server https://posit-connect.prod.netflix.net \
  --api-key "${CONNECT_API_KEY:-KM53LSk2gQmqttwVGHtfs7Ot54hcK9i1}" \
  --title "Netflix Studios Stage Estimator" \
  --entrypoint stage_calculator_app.py \
  --new \
  .

echo ""
echo "✅ Done! Your permanent URL is shown above."
