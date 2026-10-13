import { integer, primaryKey, real, sqliteTable, text } from "drizzle-orm/sqlite-core";

export const runs = sqliteTable("runs", {
  runId: text("run_id").primaryKey(),
  sourceRows: integer("source_rows").notNull(),
  sampledNonempty: integer("sampled_nonempty").notNull(),
  completed: integer("completed").notNull(),
  quarantined: integer("quarantined").notNull(),
  uniqueTexts: integer("unique_texts").notNull(),
  cacheReuseRows: integer("cache_reuse_rows").notNull(),
  provider: text("provider").notNull(),
  model: text("model").notNull(),
  costUsd: real("cost_usd").notNull(),
  elapsedSeconds: real("elapsed_seconds").notNull(),
  generatedAt: text("generated_at").notNull(),
});

export const reviewResults = sqliteTable("review_results", {
  reviewId: text("review_id").primaryKey(),
  runId: text("run_id").notNull(),
  sourceSha256: text("source_sha256").notNull(),
  topic: text("topic").notNull(),
  intent: text("intent").notNull(),
  sentiment: real("sentiment").notNull(),
  severity: integer("severity").notNull(),
  needsReview: integer("needs_review", { mode: "boolean" }).notNull(),
  reviewRating: integer("review_rating").notNull(),
  reviewTimestamp: text("review_timestamp").notNull(),
  evidenceQuote: text("evidence_quote").notNull(),
  cacheSourceId: text("cache_source_id"),
  labelConfig: text("label_config").notNull(),
});

export const topicMetrics = sqliteTable(
  "topic_metrics",
  {
    runId: text("run_id").notNull(),
    topic: text("topic").notNull(),
    reviewCount: integer("review_count").notNull(),
    complaintCount: integer("complaint_count").notNull(),
    meanSeverity: real("mean_severity").notNull(),
    meanSentiment: real("mean_sentiment").notNull(),
  },
  (table) => [primaryKey({ columns: [table.runId, table.topic] })],
);

export const intentMetrics = sqliteTable(
  "intent_metrics",
  {
    runId: text("run_id").notNull(),
    intent: text("intent").notNull(),
    reviewCount: integer("review_count").notNull(),
  },
  (table) => [primaryKey({ columns: [table.runId, table.intent] })],
);

export const monthlyTrends = sqliteTable(
  "monthly_trends",
  {
    runId: text("run_id").notNull(),
    month: text("month").notNull(),
    reviewCount: integer("review_count").notNull(),
    complaintCount: integer("complaint_count").notNull(),
    complaintShare: real("complaint_share").notNull(),
    meanSeverity: real("mean_severity").notNull(),
    meanSentiment: real("mean_sentiment").notNull(),
    partialMonth: integer("partial_month", { mode: "boolean" }).notNull(),
  },
  (table) => [primaryKey({ columns: [table.runId, table.month] })],
);

export const issueRankings = sqliteTable(
  "issue_rankings",
  {
    runId: text("run_id").notNull(),
    rank: integer("rank").notNull(),
    issueId: text("issue_id").notNull(),
    complaintCount: integer("complaint_count").notNull(),
    severitySum: integer("severity_sum").notNull(),
    meanSeverity: real("mean_severity").notNull(),
    priorityScore: integer("priority_score").notNull(),
  },
  (table) => [primaryKey({ columns: [table.runId, table.issueId] })],
);

export const recommendations = sqliteTable("recommendations", {
  recommendationId: text("recommendation_id").primaryKey(),
  runId: text("run_id").notNull(),
  title: text("title").notNull(),
  summary: text("summary").notNull(),
  primaryIssueId: text("primary_issue_id").notNull(),
  alternatives: text("alternatives").notNull(),
  limitations: text("limitations").notNull(),
  model: text("model").notNull(),
  createdAt: text("created_at").notNull(),
});

export const recommendationClaims = sqliteTable(
  "recommendation_claims",
  {
    recommendationId: text("recommendation_id").notNull(),
    claimId: text("claim_id").notNull(),
    issueId: text("issue_id").notNull(),
    metric: text("metric").notNull(),
    value: text("value").notNull(),
    evidenceReviewIds: text("evidence_review_ids").notNull(),
  },
  (table) => [primaryKey({ columns: [table.recommendationId, table.claimId] })],
);

export const evaluationSummary = sqliteTable("evaluation_summary", {
  runId: text("run_id").primaryKey(),
  goldenSize: integer("golden_size").notNull(),
  topicAccuracy: real("topic_accuracy").notNull(),
  intentAccuracy: real("intent_accuracy").notNull(),
  severityExactAccuracy: real("severity_exact_accuracy").notNull(),
  severityMae: real("severity_mae").notNull(),
  sentimentMae: real("sentiment_mae").notNull(),
  ambiguousCases: integer("ambiguous_cases").notNull(),
});
