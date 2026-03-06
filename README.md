# Netflix Studios Stage Estimator

## Deploy to Posit Connect (permanent URL)

### Option 1: Run deploy script
```bash
cd deploy_stage_estimator
bash deploy.sh
```

### Option 2: Manual deploy
```bash
pip install rsconnect-python
rsconnect deploy streamlit \
  --server https://posit-connect.prod.netflix.net \
  --api-key YOUR_API_KEY \
  --title "Netflix Studios Stage Estimator" \
  --entrypoint stage_calculator_app.py \
  --new .
```

### Option 3: Posit Connect UI
1. Go to https://posit-connect.prod.netflix.net
2. Click Publish → Upload
3. Upload all files in this folder

## Run locally
```bash
pip install streamlit pandas plotly
streamlit run stage_calculator_app.py
```
