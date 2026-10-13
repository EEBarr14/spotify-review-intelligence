import { NextResponse } from "next/server";
import { loadDashboardData } from "@/lib/dashboard-queries";

export const dynamic = "force-dynamic";

export async function GET() {
  try {
    const data = await loadDashboardData();
    if (!data) {
      return NextResponse.json({ error: "No completed dashboard run is available." }, { status: 404 });
    }
    return NextResponse.json(data, {
      headers: { "Cache-Control": "public, max-age=300, stale-while-revalidate=3600" },
    });
  } catch (error) {
    console.error("dashboard_api_failed", error);
    return NextResponse.json({ error: "Dashboard data is temporarily unavailable." }, { status: 503 });
  }
}
