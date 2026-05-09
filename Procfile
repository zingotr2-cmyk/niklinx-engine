web: gunicorn app.routes_api:app -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --access-logfile -
dashboard: streamlit run app/dashboard.py --server.port=$DASHBOARD_PORT --server.headless=true --browser.gatherUsageStats=false
