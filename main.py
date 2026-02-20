from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import speedtest
import sqlite3
import pandas as pd
from sklearn.ensemble import IsolationForest
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

def setup_database():
    conn = sqlite3.connect("speed_data.db")
    cursor = conn.cursor()
    # Table 1: Speed Tests
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS speed_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, download REAL, upload REAL,
            ping REAL, city TEXT, country TEXT, browser TEXT, source TEXT
        )
    ''')
    # Table 2: Analytics Logs (Now equipped with City and Country!)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT, timestamp TEXT, visitor_id TEXT, 
            session_id TEXT, action TEXT, details TEXT, city TEXT, country TEXT
        )
    ''')
    conn.commit()
    conn.close()

setup_database()

@app.get("/")
def home(): return {"message": "Server Running!"}

# --- UPGRADED: Log Event now captures Location ---
@app.get("/log-event")
def log_event(visitor_id: str, session_id: str, action: str, details: str = "", city: str = "Unknown", country: str = "Unknown"):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect("speed_data.db")
    cursor = conn.cursor()
    cursor.execute('INSERT INTO analytics_logs (timestamp, visitor_id, session_id, action, details, city, country) VALUES (?, ?, ?, ?, ?, ?, ?)', 
                  (current_time, visitor_id, session_id, action, details, city, country))
    conn.commit()
    conn.close()
    return {"status": "success"}

@app.get("/analytics-data")
def get_analytics():
    conn = sqlite3.connect("speed_data.db")
    df = pd.read_sql_query("SELECT * FROM analytics_logs ORDER BY id ASC", conn)
    conn.close()
    return df.to_dict(orient="records")

@app.get("/history")
def get_history():
    conn = sqlite3.connect("speed_data.db")
    df = pd.read_sql_query("SELECT * FROM speed_logs ORDER BY id ASC", conn)
    conn.close()
    return df.to_dict(orient="records")

@app.delete("/clear")
def clear_history():
    conn = sqlite3.connect("speed_data.db")
    conn.execute("DELETE FROM speed_logs")
    conn.execute("DELETE FROM analytics_logs")
    conn.commit()
    conn.close()
    return {"message": "All databases formatted!"}

@app.get("/run-test")
def perform_speed_test(city: str="Unknown", country: str="Unknown", browser: str="Unknown", source: str="Direct"):
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = round(st.download() / 1000000, 2)
    upload_speed = round(st.upload() / 1000000, 2)
    ping = round(st.results.ping)
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect("speed_data.db")
    conn.execute('''INSERT INTO speed_logs (timestamp, download, upload, ping, city, country, browser, source) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (current_time, download_speed, upload_speed, ping, city, country, browser, source))
    conn.commit()
    
    df = pd.read_sql_query("SELECT * FROM speed_logs", conn)
    conn.close()
    
    ai_message = "Gathering more data to establish your baseline..."
    status_color = "gray"
    if len(df) >= 3:
        model = IsolationForest(contamination='auto', random_state=42)
        df['ai_verdict'] = model.fit_predict(df[['download']])
        if df.iloc[-1]['ai_verdict'] == 1:
            ai_message = "Speeds are Optimal and consistent with your history."
            status_color = "green"
        else:
            ai_message = "Anomaly Detected! Speeds have dropped below your usual baseline."
            status_color = "red"
            
    return {"download": download_speed, "upload": upload_speed, "ping": ping, "timestamp": current_time, 
            "city": city, "country": country, "browser": browser, "source": source, "ai_message": ai_message, "status_color": status_color}