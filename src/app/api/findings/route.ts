import { NextResponse } from "next/server";
import { db } from "../../../db";
import { findings } from "../../../db/schema";
import { desc } from "drizzle-orm";

export async function GET() {
  try {
    const data = await db.select().from(findings).orderBy(desc(findings.severity));
    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json({ error: "Failed to fetch findings" }, { status: 500 });
  }
}
