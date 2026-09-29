import json
import psycopg2
import sys
import os

# We changed the function to accept two arguments from main.py
def run_ingestion(json_file_path, database_url):
    try:
        # Now it dynamically reads whatever file path main.py tells it to
        with open(json_file_path, "r") as f:
            findings = json.load(f)
        
        # Now it dynamically connects to whatever database URL was passed in
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # NOTE: TRUNCATE clears the entire table. 
        # If you plan to store multiple projects in this one database, 
        # you will eventually want to change this to only DELETE rows matching a specific project name.
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
        print(f"❌ Error during database ingestion: {e}")

# This keeps the file usable if you still want to run it completely on its own
if __name__ == "__main__":
    # If run directly, it will look for command line arguments or use defaults
    default_path = sys.argv[1] if len(sys.argv) > 1 else "findings.json"
    default_db = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/trustlens")
    
    run_ingestion(default_path, default_db)