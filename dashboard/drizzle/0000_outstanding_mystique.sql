CREATE TABLE `evaluation_summary` (
	`run_id` text PRIMARY KEY NOT NULL,
	`golden_size` integer NOT NULL,
	`topic_accuracy` real NOT NULL,
	`intent_accuracy` real NOT NULL,
	`severity_exact_accuracy` real NOT NULL,
	`severity_mae` real NOT NULL,
	`sentiment_mae` real NOT NULL,
	`ambiguous_cases` integer NOT NULL
);
--> statement-breakpoint
CREATE TABLE `intent_metrics` (
	`run_id` text NOT NULL,
	`intent` text NOT NULL,
	`review_count` integer NOT NULL,
	PRIMARY KEY(`run_id`, `intent`)
);
--> statement-breakpoint
CREATE TABLE `issue_rankings` (
	`run_id` text NOT NULL,
	`rank` integer NOT NULL,
	`issue_id` text NOT NULL,
	`complaint_count` integer NOT NULL,
	`severity_sum` integer NOT NULL,
	`mean_severity` real NOT NULL,
	`priority_score` integer NOT NULL,
	PRIMARY KEY(`run_id`, `issue_id`)
);
--> statement-breakpoint
CREATE TABLE `monthly_trends` (
	`run_id` text NOT NULL,
	`month` text NOT NULL,
	`review_count` integer NOT NULL,
	`complaint_count` integer NOT NULL,
	`complaint_share` real NOT NULL,
	`mean_severity` real NOT NULL,
	`mean_sentiment` real NOT NULL,
	`partial_month` integer NOT NULL,
	PRIMARY KEY(`run_id`, `month`)
);
--> statement-breakpoint
CREATE TABLE `recommendation_claims` (
	`recommendation_id` text NOT NULL,
	`claim_id` text NOT NULL,
	`issue_id` text NOT NULL,
	`metric` text NOT NULL,
	`value` text NOT NULL,
	`evidence_review_ids` text NOT NULL,
	PRIMARY KEY(`recommendation_id`, `claim_id`)
);
--> statement-breakpoint
CREATE TABLE `recommendations` (
	`recommendation_id` text PRIMARY KEY NOT NULL,
	`run_id` text NOT NULL,
	`title` text NOT NULL,
	`summary` text NOT NULL,
	`primary_issue_id` text NOT NULL,
	`alternatives` text NOT NULL,
	`limitations` text NOT NULL,
	`model` text NOT NULL,
	`created_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `review_results` (
	`review_id` text PRIMARY KEY NOT NULL,
	`run_id` text NOT NULL,
	`source_sha256` text NOT NULL,
	`topic` text NOT NULL,
	`intent` text NOT NULL,
	`sentiment` real NOT NULL,
	`severity` integer NOT NULL,
	`needs_review` integer NOT NULL,
	`review_rating` integer NOT NULL,
	`review_timestamp` text NOT NULL,
	`evidence_quote` text NOT NULL,
	`cache_source_id` text,
	`label_config` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `runs` (
	`run_id` text PRIMARY KEY NOT NULL,
	`source_rows` integer NOT NULL,
	`sampled_nonempty` integer NOT NULL,
	`completed` integer NOT NULL,
	`quarantined` integer NOT NULL,
	`unique_texts` integer NOT NULL,
	`cache_reuse_rows` integer NOT NULL,
	`provider` text NOT NULL,
	`model` text NOT NULL,
	`cost_usd` real NOT NULL,
	`elapsed_seconds` real NOT NULL,
	`generated_at` text NOT NULL
);
--> statement-breakpoint
CREATE TABLE `topic_metrics` (
	`run_id` text NOT NULL,
	`topic` text NOT NULL,
	`review_count` integer NOT NULL,
	`complaint_count` integer NOT NULL,
	`mean_severity` real NOT NULL,
	`mean_sentiment` real NOT NULL,
	PRIMARY KEY(`run_id`, `topic`)
);
