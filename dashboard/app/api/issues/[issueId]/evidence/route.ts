import { NextRequest, NextResponse } from "next/server";
import { loadIssueEvidence } from "@/lib/dashboard-queries";

export const dynamic = "force-dynamic";

export async function GET(
  _request: NextRequest,
  context: { params: Promise<{ issueId: string }> },
) {
  const { issueId } = await context.params;
  if (!/^issue_(access|usability|playback|downloads|catalog|billing|support|other)$/.test(issueId)) {
    return NextResponse.json({ error: "Unknown issue ID." }, { status: 400 });
  }
  try {
    const evidence = await loadIssueEvidence(issueId);
    return NextResponse.json({ issueId, evidence });
  } catch (error) {
    console.error("issue_evidence_api_failed", error);
    return NextResponse.json({ error: "Evidence is temporarily unavailable." }, { status: 503 });
  }
}
