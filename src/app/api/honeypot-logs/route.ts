import { NextResponse } from 'next/server';
import { Pool } from 'pg';

// Disable Node TLS rejection for Neon serverless connections
process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

const connectionString = process.env.DATABASE_URL;

export async function GET() {
  if (!connectionString) {
    console.error("[API Error] DATABASE_URL is not set in environment.");
    return NextResponse.json(
      { success: false, error: "DATABASE_URL missing" },
      { status: 500 }
    );
  }

  const pool = new Pool({
    connectionString,
    ssl: { rejectUnauthorized: false }
  });

  try {
    const client = await pool.connect();
    const result = await client.query(
      'SELECT id, ip_address, port, payload, timestamp FROM honeypot_logs ORDER BY timestamp DESC LIMIT 20'
    );
    client.release();
    await pool.end();

    return NextResponse.json({ success: true, logs: result.rows });
  } catch (error: any) {
    console.error("[API Neon DB Error]:", error.message);
    await pool.end();
    return NextResponse.json(
      { success: false, error: error.message },
      { status: 500 }
    );
  }
}