-- Local visual-QA fixture only. Never apply this file to the hosted database.
DELETE FROM recommendation_claims;
DELETE FROM recommendations;
DELETE FROM evaluation_summary;
DELETE FROM issue_rankings;
DELETE FROM monthly_trends;
DELETE FROM intent_metrics;
DELETE FROM topic_metrics;
DELETE FROM review_results;
DELETE FROM runs;

INSERT OR REPLACE INTO runs VALUES
('preview-fixture', 660622, 100000, 100000, 13, 78099, 21901, 'Jev preview fixture', 'pending measured model', 4.37, 8120, '2026-10-08T12:00:00Z');

INSERT OR REPLACE INTO topic_metrics VALUES
('preview-fixture', 'playback', 24800, 15100, 3.7, -0.42),
('preview-fixture', 'access', 18300, 12100, 4.0, -0.51),
('preview-fixture', 'other', 17600, 9800, 3.2, -0.28),
('preview-fixture', 'catalog', 14200, 7100, 3.5, -0.33),
('preview-fixture', 'usability', 13100, 7900, 3.8, -0.47),
('preview-fixture', 'support', 12000, 3900, 2.7, 0.04);

INSERT OR REPLACE INTO intent_metrics VALUES
('preview-fixture', 'complaint', 49300),
('preview-fixture', 'praise', 27200),
('preview-fixture', 'request', 17100),
('preview-fixture', 'cancellation', 6400);

INSERT OR REPLACE INTO monthly_trends VALUES
('preview-fixture', '2023-06', 4100, 2100, 0.512, 3.4, -0.20, 0),
('preview-fixture', '2023-07', 12800, 7200, 0.563, 3.6, -0.28, 0),
('preview-fixture', '2023-08', 4800, 2500, 0.521, 3.5, -0.24, 0),
('preview-fixture', '2023-09', 6400, 3500, 0.547, 3.7, -0.30, 0),
('preview-fixture', '2023-10', 13400, 7900, 0.590, 3.8, -0.36, 0),
('preview-fixture', '2023-11', 5200, 2900, 0.558, 3.6, -0.27, 1);

INSERT OR REPLACE INTO issue_rankings VALUES
('preview-fixture', 1, 'issue_access', 12100, 48400, 4.00, 48400),
('preview-fixture', 2, 'issue_playback', 15100, 45800, 3.03, 45800),
('preview-fixture', 3, 'issue_usability', 7900, 30020, 3.80, 30020),
('preview-fixture', 4, 'issue_other', 9800, 27440, 2.80, 27440);

INSERT OR REPLACE INTO recommendations VALUES
('preview-recommendation', 'preview-fixture', 'The Business Question Comes First: Focus on Usability',
 'Preview only: focus product investigation on account-access failures because this fixture ranks them highest by reproducible severity-weighted complaint volume. Final wording will be generated from measured results and cited evidence.',
 'issue_access', '["playback reliability","usability"]',
 'These numbers are a local visual-QA fixture, not analytical results. The final recommendation will retain sampling, language, self-selection, and classification limitations.',
 'pending final memo model', '2026-10-08T12:01:00Z');

INSERT OR REPLACE INTO recommendation_claims VALUES
('preview-recommendation', 'C1', 'issue_access', 'priority score', '48,400 (preview)', '["preview-review-1"]'),
('preview-recommendation', 'C2', 'issue_access', 'complaint count', '12,100 (preview)', '["preview-review-1"]');

INSERT OR REPLACE INTO evaluation_summary VALUES
('preview-fixture', 50, 0.86, 0.90, 0.78, 0.34, 0.16, 4);

INSERT OR REPLACE INTO review_results VALUES
('preview-review-1', 'preview-fixture', 'preview-only', 'access', 'complaint', -0.8, 5, 0, 1, '2023-10-10 12:00:00', 'Preview evidence quote', NULL, 'preview-only');
