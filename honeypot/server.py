import socket
import os
import datetime
import psycopg2

PORT = int(os.getenv("HONEYPOT_PORT", 2222))
DATABASE_URL = os.getenv("DATABASE_URL")

def log_to_neon(ip, port, payload):
    if not DATABASE_URL:
        print("[DB] No DATABASE_URL found. Skipping cloud telemetry.")
        return
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # Auto-create the table for your Next.js dashboard to read
        cur.execute("""
            CREATE TABLE IF NOT EXISTS honeypot_logs (
                id SERIAL PRIMARY KEY,
                ip_address VARCHAR(50),
                port INTEGER,
                payload TEXT,
                timestamp TIMESTAMP
            )
        """)
        
        cur.execute(
            "INSERT INTO honeypot_logs (ip_address, port, payload, timestamp) VALUES (%s, %s, %s, %s)",
            (ip, port, payload, datetime.datetime.now())
        )
        conn.commit()
        cur.close()
        conn.close()
        print("[DB] Payload successfully logged to Neon PostgreSQL!")
    except Exception as e:
        print(f"[DB Error] {e}")

def start_honeypot():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(("0.0.0.0", PORT))
    s.listen(5)
    print(f"[*] Micro-Honeypot active on port {PORT}")
    
    while True:
        conn, addr = s.accept()
        ip = addr[0]
        print(f"[ALERT] Connection attempt from {ip}")
        conn.send(b"Ubuntu 22.04 LTS (Trusty)\nLogin: ")
        
        try:
            payload = conn.recv(1024).decode('utf-8', errors='ignore').strip()
            print(f"[PAYLOAD] {ip} sent: {payload}")
            log_to_neon(ip, PORT, payload)
        except Exception as e:
            pass
        finally:
            conn.close()

if __name__ == "__main__":
    start_honeypot()
