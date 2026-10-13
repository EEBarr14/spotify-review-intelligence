import { and, asc, desc, eq } from "drizzle-orm";
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
import type { DashboardData } from "@/lib/dashboard-types";
import { ensureFinalDashboardSeeded } from "@/lib/final-dashboard-seed";

const publicEvidenceBlocklist = /\b(?:hack(?:ed|er|ing)?|scam(?:med|ming)?|fraud\w*|stole(?:n)?|steal(?:ing)?|breach(?:ed)?|spy|privacy|track(?:ed|er|ing)?|advertis(?:e|ing)|merchant|email|data|card|bank|permission|suicid(?:e|al)|kill(?:ed|ing)?|porn|racist|nazi|fuck|shit|trash|stupid|suck\w*)\b/i;
const publicContactPatterns = [
  /[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}/i,
  /https?:\/\/|www\./i,
  /(?:\+?[0-9][ .()_-]){7,}[0-9]/,
  /(?:^|[^0-9])(?:[0-9][ -]){12,18}[0-9](?:$|[^0-9])/,
];

function isSafePublicEvidence(text: string) {
  return text.length > 0
    && text.length <= 500
    && !publicEvidenceBlocklist.test(text)
    && !publicContactPatterns.some((pattern) => pattern.test(text));
}

export async function loadDashboardData(): Promise<DashboardData | null> {
  await ensureFinalDashboardSeeded();
  const db = getDb();
  const [run] = await db.select().from(runs).orderBy(desc(runs.generatedAt)).limit(1);
  if (!run) return null;

  const [topics, intents, trends, rankings, recommendationRows, evaluations] = await Promise.all([
    db.select().from(topicMetrics).where(eq(topicMetrics.runId, run.runId)).orderBy(desc(topicMetrics.reviewCount)),
    db.select().from(intentMetrics).where(eq(intentMetrics.runId, run.runId)).orderBy(desc(intentMetrics.reviewCount)),
    db.select().from(monthlyTrends).where(eq(monthlyTrends.runId, run.runId)).orderBy(asc(monthlyTrends.month)),
    db.select().from(issueRankings).where(eq(issueRankings.runId, run.runId)).orderBy(asc(issueRankings.rank)),
    db.select().from(recommendations).where(eq(recommendations.runId, run.runId)).orderBy(desc(recommendations.createdAt)).limit(1),
    db.select().from(evaluationSummary).where(eq(evaluationSummary.runId, run.runId)).limit(1),
  ]);

  const recommendation = recommendationRows[0];
  if (!recommendation) return null;
  const claims = await db
    .select()
    .from(recommendationClaims)
    .where(eq(recommendationClaims.recommendationId, recommendation.recommendationId))
    .orderBy(asc(recommendationClaims.claimId));

  return {
    run,
    topics: topics.map((value) => ({
      topic: value.topic,
      reviewCount: value.reviewCount,
      complaintCount: value.complaintCount,
      meanSeverity: value.meanSeverity,
      meanSentiment: value.meanSentiment,
    })),
    intents: intents.map((value) => ({ intent: value.intent, reviewCount: value.reviewCount })),
    trends: trends.map((value) => ({
      month: value.month,
      reviewCount: value.reviewCount,
      complaintCount: value.complaintCount,
      complaintShare: value.complaintShare,
      meanSeverity: value.meanSeverity,
      meanSentiment: value.meanSentiment,
      partialMonth: value.partialMonth,
    })),
    rankings: rankings.map((value) => ({
      rank: value.rank,
      issueId: value.issueId,
      complaintCount: value.complaintCount,
      severitySum: value.severitySum,
      meanSeverity: value.meanSeverity,
      priorityScore: value.priorityScore,
    })),
    recommendation: {
      recommendationId: recommendation.recommendationId,
      title: recommendation.title,
      summary: recommendation.summary,
      primaryIssueId: recommendation.primaryIssueId,
      alternatives: recommendation.alternatives,
      limitations: recommendation.limitations,
      model: recommendation.model,
      createdAt: recommendation.createdAt,
      claims: claims.map((claim) => ({
        claimId: claim.claimId,
        issueId: claim.issueId,
        metric: claim.metric,
        value: claim.value,
        evidenceReviewIds: JSON.parse(claim.evidenceReviewIds) as string[],
      })),
    },
    evaluation: evaluations[0] ?? null,
  };
}

export async function loadIssueEvidence(issueId: string) {
  await ensureFinalDashboardSeeded();
  const db = getDb();
  const [run] = await db.select().from(runs).orderBy(desc(runs.generatedAt)).limit(1);
  if (!run) return [];
  const topic = issueId.replace(/^issue_/, "");
  const candidates = await db
    .select({
      reviewId: reviewResults.reviewId,
      topic: reviewResults.topic,
      intent: reviewResults.intent,
      severity: reviewResults.severity,
      sentiment: reviewResults.sentiment,
      evidenceQuote: reviewResults.evidenceQuote,
    })
    .from(reviewResults)
    .where(and(
      eq(reviewResults.runId, run.runId),
      eq(reviewResults.topic, topic),
      eq(reviewResults.needsReview, false),
    ))
    .orderBy(desc(reviewResults.severity))
    .limit(100);
  return candidates.filter((row) => isSafePublicEvidence(row.evidenceQuote)).slice(0, 12);
}
