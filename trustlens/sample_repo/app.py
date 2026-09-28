#!/usr/bin/env python
"""
Intentionally vulnerable Python application for testing
Contains OWASP Top 10 vulnerabilities
"""
import sqlite3
import os
import pickle
from flask import Flask, request

app = Flask(__name__)


# ============================================
# VULNERABILITY 1: Hard-coded password in source code
# ============================================
DATABASE_PASSWORD = "super_secret_password_12345"
API_KEY = "sk-123456789abcdefghijk"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"


# ============================================
# VULNERABILITY 2: SQL Injection
# ============================================
@app.route("/user/<user_id>")
def get_user(user_id):
    """
    VULNERABLE: Direct SQL injection - user_id is directly interpolated
    """
    db = sqlite3.connect("app.db")
    cursor = db.cursor()
    
    # VULNERABLE: user_id is directly concatenated into SQL query
    query = f"SELECT * FROM users WHERE id = {user_id}"
    
    cursor.execute(query)
    user = cursor.fetchone()
    db.close()
    
    return user


@app.route("/search")
def search():
    """
    VULNERABLE: SQL injection via query parameter
    """
    search_term = request.args.get("q", "")
    
    db = sqlite3.connect("app.db")
    cursor = db.cursor()
    
    # VULNERABLE: search_term is directly interpolated
    query = "SELECT * FROM products WHERE name LIKE '%" + search_term + "%'"
    
    cursor.execute(query)
    results = cursor.fetchall()
    db.close()
    
    return results


# ============================================
# VULNERABILITY 3: Insecure deserialization (pickle)
# ============================================
@app.route("/deserialize", methods=["POST"])
def deserialize_data():
    """
    VULNERABLE: Using pickle.loads on untrusted data
    This allows arbitrary code execution
    """
    data = request.data
    
    # CRITICAL VULNERABILITY: pickle.loads can execute arbitrary code
    deserialized = pickle.loads(data)
    
    return {"result": deserialized}


# ============================================
# VULNERABILITY 4: Insufficient logging and monitoring
# ============================================
@app.route("/login", methods=["POST"])
def login():
    """
    VULNERABLE: No logging of login attempts
    """
    username = request.form.get("username")
    password = request.form.get("password")
    
    # VULNERABLE: No logging of failed login attempts
    # VULNERABLE: No rate limiting
    # VULNERABLE: No account lockout mechanism
    
    if username == "admin" and password == DATABASE_PASSWORD:
        return {"status": "success", "token": "INSECURE_TOKEN_123"}
    
    return {"status": "failed"}, 401


# ============================================
# VULNERABILITY 5: Broken access control
# ============================================
@app.route("/admin/users")
def admin_users():
    """
    VULNERABLE: No authentication or authorization check
    """
    # VULNERABLE: No check if user is admin
    # VULNERABLE: No session validation
    
    db = sqlite3.connect("app.db")
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()
    db.close()
    
    return users


# ============================================
# VULNERABILITY 6: Use of eval() on user input
# ============================================
@app.route("/calculate", methods=["POST"])
def calculate():
    """
    CRITICAL VULNERABILITY: Using eval() on user input
    This allows arbitrary code execution
    """
    expression = request.form.get("expression", "")
    
    # CRITICAL: eval() executes arbitrary Python code
    # Attacker can execute: "__import__('os').system('rm -rf /')"
    result = eval(expression)
    
    return {"result": result}


# ============================================
# VULNERABILITY 7: Exposure of sensitive information
# ============================================
@app.route("/debug")
def debug_info():
    """
    VULNERABLE: Exposing sensitive information
    """
    return {
        "database_password": DATABASE_PASSWORD,
        "api_key": API_KEY,
        "aws_key": AWS_ACCESS_KEY,
        "environment": os.environ,  # VULNERABLE: Exposing all env vars
        "debug_mode": True,  # VULNERABLE: Debug mode enabled
    }


# ============================================
# VULNERABILITY 8: Insecure random number generation
# ============================================
import random

def generate_token():
    """
    VULNERABLE: Using random instead of secrets module
    """
    # VULNERABLE: random is not cryptographically secure
    token = "".join([str(random.randint(0, 9)) for _ in range(32)])
    return token


# ============================================
# VULNERABILITY 9: XXE (XML External Entity) Injection
# ============================================
import xml.etree.ElementTree as ET

@app.route("/parse-xml", methods=["POST"])
def parse_xml():
    """
    VULNERABLE: Parsing XML without disabling external entities
    """
    xml_data = request.data
    
    # VULNERABLE: No protection against XXE
    root = ET.fromstring(xml_data)
    
    return {"parsed": ET.tostring(root)}


# ============================================
# VULNERABILITY 10: Using outdated library versions
# ============================================
# Requirements file (if it existed) would list:
# Flask==1.0.0  # VULNERABLE: Very old version
# requests==2.6.0  # VULNERABLE: Very old version
# Werkzeug==0.11.0  # VULNERABLE: Very old version


if __name__ == "__main__":
    # VULNERABILITY: Debug mode enabled in production
    app.run(debug=True, host="0.0.0.0", port=5000)
