import seed from "@/data/final-dashboard-seed.json";
import { getDb } from "@/db";
import {
  evaluationSummary,
  intentMetrics,
  issueRankings,
  monthlyTrends,
  recommendationClaims,
  recommendations,
  reviewResults,
  runs,
  topicMetrics,
} from "@/db/schema";

let seedPromise: Promise<void> | null = null;

export function ensureFinalDashboardSeeded(): Promise<void> {
  if (seedPromise) return seedPromise;
  seedPromise = (async () => {
    const db = getDb();
    // D1 batch() is atomic. A canceled first request must not leave a partial
    // seed that looks complete merely because the run row was inserted first.
    // Keep wider rows in small statements to stay below SQLite's bind limit.
    await db.batch([
      db.insert(runs).values(seed.runs).onConflictDoNothing(),
      db.insert(topicMetrics).values(seed.topic_metrics).onConflictDoNothing(),
      db.insert(intentMetrics).values(seed.intent_metrics).onConflictDoNothing(),
      ...chunk(seed.monthly_trends, 10).map((rows) =>
        db.insert(monthlyTrends).values(rows).onConflictDoNothing()
      ),
      db.insert(issueRankings).values(seed.issue_rankings).onConflictDoNothing(),
      db.insert(recommendations).values(seed.recommendations).onConflictDoNothing(),
      db.insert(recommendationClaims).values(seed.recommendation_claims).onConflictDoNothing(),
      db.insert(evaluationSummary).values(seed.evaluation_summary).onConflictDoNothing(),
      ...chunk(seed.review_results, 5).map((rows) =>
        db.insert(reviewResults).values(rows).onConflictDoNothing()
      ),
    ]);
  })().catch((error) => {
    seedPromise = null;
    throw error;
  });
  return seedPromise;
}

function chunk<T>(values: T[], size: number): T[][] {
  const result: T[][] = [];
  for (let index = 0; index < values.length; index += size) {
    result.push(values.slice(index, index + size));
  }
  return result;
}
