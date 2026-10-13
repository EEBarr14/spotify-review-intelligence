export type DashboardData = {
  run: {
    runId: string;
    sourceRows: number;
    sampledNonempty: number;
    completed: number;
    quarantined: number;
    uniqueTexts: number;
    cacheReuseRows: number;
    provider: string;
    model: string;
    costUsd: number;
    elapsedSeconds: number;
    generatedAt: string;
  };
  topics: Array<{
    topic: string;
    reviewCount: number;
    complaintCount: number;
    meanSeverity: number;
    meanSentiment: number;
  }>;
  intents: Array<{ intent: string; reviewCount: number }>;
  trends: Array<{
    month: string;
    reviewCount: number;
    complaintCount: number;
    complaintShare: number;
    meanSeverity: number;
    meanSentiment: number;
    partialMonth: boolean;
  }>;
  rankings: Array<{
    rank: number;
    issueId: string;
    complaintCount: number;
    severitySum: number;
    meanSeverity: number;
    priorityScore: number;
  }>;
  recommendation: {
    recommendationId: string;
    title: string;
    summary: string;
    primaryIssueId: string;
    alternatives: string;
    limitations: string;
    model: string;
    createdAt: string;
    claims: Array<{
      claimId: string;
      issueId: string;
      metric: string;
      value: string;
      evidenceReviewIds: string[];
    }>;
  };
  evaluation: {
    goldenSize: number;
    topicAccuracy: number;
    intentAccuracy: number;
    severityExactAccuracy: number;
    severityMae: number;
    sentimentMae: number;
    ambiguousCases: number;
  } | null;
};
