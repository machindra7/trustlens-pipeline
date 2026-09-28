import json
import psycopg2

DB_URL = "postgresql://postgres:postgres@localhost:5432/trustlens"

def ingest():
    try:
        with open("findings.json", "r") as f:
            findings = json.load(f)
        
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        
        cursor.execute("TRUNCATE TABLE findings RESTART IDENTITY;")
        
        count = 0
        for item in findings:
            severity = item.get("severity_raw", "UNKNOWN")[:20]
            scanner = item.get("source_tool", "UNKNOWN").upper()[:50]
            rule_id = item.get("rule_id", "UNKNOWN")[:255]
            title = item.get("title", "No title")
            description = item.get("description", "No description")
            category = item.get("category", "vulnerability")
            
            location = item.get("location", {})
            file_path = location.get("file", "UNKNOWN") if location else "UNKNOWN"
            start_line = location.get("start_line") if location else None
            
            cursor.execute("""
                INSERT INTO findings (severity, scanner, rule_id, title, description, category, file_path, start_line)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (severity, scanner, rule_id, title, description, category, file_path, start_line))
            count += 1
            
        conn.commit()
        cursor.close()
        conn.close()
        print(f"✅ Successfully ingested {count} security findings.")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    ingest()
