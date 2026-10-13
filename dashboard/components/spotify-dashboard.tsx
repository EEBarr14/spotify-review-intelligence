"use client";

import { useEffect, useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Activity, CircleDollarSign, Database, ShieldCheck } from "lucide-react";
import type { DashboardData } from "@/lib/dashboard-types";

type EvidenceItem = {
  reviewId: string;
  topic: string;
  intent: string;
  severity: number;
  sentiment: number;
  evidenceQuote: string;
};

const number = new Intl.NumberFormat("en-US");
const percent = new Intl.NumberFormat("en-US", { style: "percent", maximumFractionDigits: 1 });
const money = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", maximumFractionDigits: 2 });

function MetricCard({ label, value, note, icon: Icon }: {
  label: string;
  value: string;
  note: string;
  icon: typeof Database;
}) {
  return (
    <article className="rounded-3xl border border-white/70 bg-white/90 p-5 shadow-[0_18px_50px_rgba(15,23,42,0.08)] backdrop-blur">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">{label}</p>
          <p className="mt-2 text-3xl font-semibold tracking-tight text-slate-950">{value}</p>
        </div>
        <span className="rounded-2xl bg-[#e9fbed] p-3 text-[#0b7a37]"><Icon size={20} /></span>
      </div>
      <p className="mt-3 text-sm leading-6 text-slate-500">{note}</p>
    </article>
  );
}

function LoadingState() {
  return (
    <main className="min-h-screen bg-[#f4f7f3] px-6 py-16 text-slate-900">
      <div className="mx-auto max-w-6xl animate-pulse">
        <div className="h-5 w-44 rounded bg-slate-200" />
        <div className="mt-5 h-12 max-w-2xl rounded bg-slate-200" />
        <div className="mt-10 grid gap-5 md:grid-cols-4">
          {[0, 1, 2, 3].map((item) => <div key={item} className="h-40 rounded-3xl bg-white" />)}
        </div>
      </div>
    </main>
  );
}

export default function SpotifyDashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/dashboard", { cache: "no-store" })
      .then(async (response) => {
        if (!response.ok) throw new Error((await response.json()).error ?? "Dashboard request failed");
        return response.json() as Promise<DashboardData>;
      })
      .then(setData)
      .catch((reason: Error) => setError(reason.message));
  }, []);

  useEffect(() => {
    if (!data?.recommendation.primaryIssueId) return;
    fetch(`/api/issues/${encodeURIComponent(data.recommendation.primaryIssueId)}/evidence`, { cache: "no-store" })
      .then(async (response) => {
        if (!response.ok) throw new Error("Evidence request failed");
        return response.json() as Promise<{ evidence: EvidenceItem[] }>;
      })
      .then((payload) => setEvidence(payload.evidence.slice(0, 3)))
      .catch(() => setEvidence([]));
  }, [data?.recommendation.primaryIssueId]);

  const maxPriority = useMemo(
    () => Math.max(1, ...(data?.rankings.map((item) => item.priorityScore) ?? [])),
    [data],
  );

  if (error) {
    return (
      <main className="grid min-h-screen place-items-center bg-[#f4f7f3] px-6 text-slate-900">
        <div className="max-w-xl rounded-3xl border border-amber-200 bg-white p-8 shadow-xl">
          <p className="text-xs font-semibold uppercase tracking-[0.16em] text-amber-700">Data connection</p>
          <h1 className="mt-3 text-3xl font-semibold">The dashboard is ready for its final dataset.</h1>
          <p className="mt-4 leading-7 text-slate-600">{error}</p>
        </div>
      </main>
    );
  }
  if (!data) return <LoadingState />;

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,#e1f8e8_0,#f4f7f3_36%,#edf1f7_100%)] text-slate-900">
      <header className="border-b border-slate-200/80 bg-[#081b17] text-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4 lg:px-10">
          <div className="flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-full bg-[#1ed760] font-black text-[#081b17]">S</span>
            <p className="font-semibold">Spotify Review Intelligence</p>
          </div>
          <div className="hidden text-right text-xs text-emerald-100/70 sm:block">
            <p>{data.run.provider} · {data.run.model}</p>
            <p>Updated {new Date(data.run.generatedAt).toLocaleDateString()}</p>
          </div>
        </div>
      </header>

      <section
        aria-hidden="true"
        className="relative h-40 overflow-hidden border-b border-emerald-950/40 bg-[#031813] sm:h-52 lg:h-64"
      >
        <div
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: "url('/spotify-soundwave-header.png')" }}
        />
        <div className="absolute inset-0 bg-[linear-gradient(180deg,rgba(3,24,19,0.06)_0%,rgba(3,24,19,0.12)_62%,rgba(3,24,19,0.72)_100%)]" />
      </section>

      <div className="mx-auto max-w-7xl px-6 py-10 lg:px-10">
        <section className="grid items-end gap-8 lg:grid-cols-[1.25fr_0.75fr]">
          <div>
            <p className="text-sm font-bold uppercase tracking-[0.2em] text-[#0b7a37]">Product priority analysis</p>
            <h1 className="mt-3 max-w-4xl text-4xl font-semibold leading-tight tracking-[-0.035em] text-slate-950 sm:text-6xl">
              The Business Question Comes First
            </h1>
            <p className="mt-5 max-w-3xl text-lg leading-8 text-slate-600">
              Where should Spotify focus next-quarter product effort? This dashboard connects a representative review sample to reproducible issue rankings and traceable evidence.
            </p>
          </div>
          <aside className="rounded-3xl border border-emerald-200 bg-[#e9fbed] p-6">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-[#0b7a37]">Method</p>
            <p className="mt-3 text-sm leading-7 text-slate-700">
              {number.format(data.run.sampledNonempty)} reviews selected with a fixed SHA-256 seed across the complete 18-month source window. First and last calendar months are partial.
            </p>
          </aside>
        </section>

        <section className="mt-10 grid gap-5 sm:grid-cols-2 xl:grid-cols-4">
          <MetricCard icon={Database} label="Completed reviews" value={number.format(data.run.completed)} note={`${number.format(data.run.sourceRows)} source rows were ingested and profiled.`} />
          <MetricCard icon={Activity} label="Exact-text reuse" value={number.format(data.run.cacheReuseRows)} note={`${number.format(data.run.uniqueTexts)} unique texts required model decisions.`} />
          <MetricCard icon={CircleDollarSign} label="Classification spend" value={money.format(data.run.costUsd)} note="Measured API spend, excluding local compute and hosting." />
          <MetricCard icon={ShieldCheck} label="Golden topic agreement" value={data.evaluation ? percent.format(data.evaluation.topicAccuracy) : "Pending"} note={data.evaluation ? `${data.evaluation.goldenSize} hand-labeled cases; diagnostic, not population accuracy.` : "Added after the frozen Jev evaluation."} />
        </section>

        <section className="mt-8 grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
          <article className="min-w-0 rounded-3xl border border-white/70 bg-white p-6 shadow-[0_18px_50px_rgba(15,23,42,0.07)]">
            <div className="flex flex-wrap items-end justify-between gap-3">
              <div>
                <p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">What reviewers discuss</p>
                <h2 className="mt-2 text-2xl font-semibold tracking-tight">Topic volume and complaint load</h2>
              </div>
              <p className="text-xs text-slate-400">Counts include every sampled review ID</p>
            </div>
            <div className="mt-6 h-[340px] min-w-0">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={data.topics} margin={{ left: 0, right: 12, top: 10, bottom: 4 }}>
                  <CartesianGrid stroke="#e2e8f0" vertical={false} />
                  <XAxis dataKey="topic" tick={{ fill: "#475569", fontSize: 12 }} tickLine={false} axisLine={false} />
                  <YAxis tick={{ fill: "#64748b", fontSize: 12 }} tickLine={false} axisLine={false} width={52} />
                  <Tooltip cursor={{ fill: "#f1f5f9" }} />
                  <Bar dataKey="reviewCount" name="All reviews" fill="#9ac5ab" radius={[6, 6, 0, 0]} />
                  <Bar dataKey="complaintCount" name="Complaints and cancellations" fill="#127a46" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </article>

          <article className="rounded-3xl bg-[#0a2820] p-7 text-white shadow-[0_18px_50px_rgba(7,35,28,0.2)]">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-[#65e596]">AI-generated recommendation</p>
            <h2 className="mt-3 text-3xl font-semibold tracking-tight">
              The Business Question Comes First: Focus on Usability
            </h2>
            <p className="mt-5 text-base leading-8 text-emerald-50/85">{data.recommendation.summary}</p>
            <div className="mt-6 space-y-3 border-t border-emerald-100/15 pt-5">
              {data.recommendation.claims.map((claim) => (
                <div key={claim.claimId} className="flex items-start justify-between gap-5 text-sm">
                  <span className="capitalize text-emerald-50/70">{claim.metric.replaceAll("_", " ")}</span>
                  <span className="text-right font-mono text-[#65e596]">{claim.metric === "mean_severity" ? Number(claim.value).toFixed(2) : number.format(Number(claim.value))}</span>
                </div>
              ))}
            </div>
            <p className="mt-6 text-xs leading-6 text-emerald-100/55">
              Generated by {data.recommendation.model} from saved aggregates and bounded evidence. No live model call occurs when this page loads.
            </p>
          </article>
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-[0.72fr_1.28fr]">
          <article className="rounded-3xl border border-emerald-200 bg-[#e9fbed] p-7">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-[#0b7a37]">Decision rule</p>
            <h2 className="mt-3 text-2xl font-semibold tracking-tight text-slate-950">Volume × reported impact</h2>
            <p className="mt-4 text-sm leading-7 text-slate-700">
              Priority is the sum of 1–5 severity scores across reviews classified as complaints or cancellations. It is a reproducible triage signal, not a forecast of revenue or churn.
            </p>
            <p className="mt-4 text-sm leading-7 text-slate-700">
              The broad “other” bucket remains visible for auditability but should not be treated as one product feature. Access is the recommended secondary watch item because its mean complaint severity is highest.
            </p>
          </article>

          <article className="rounded-3xl border border-white/70 bg-white p-7 shadow-[0_18px_50px_rgba(15,23,42,0.07)]">
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">Traceable evidence</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight">What high-severity usability reviews actually said</h2>
            <div className="mt-5 grid gap-3">
              {evidence.length ? evidence.map((item) => (
                <blockquote key={item.reviewId} className="rounded-2xl border border-slate-200 bg-slate-50 p-5">
                  <p className="text-sm leading-7 text-slate-700">“{item.evidenceQuote}”</p>
                  <footer className="mt-3 flex flex-wrap gap-2 text-xs text-slate-500">
                    <span className="rounded-full bg-white px-3 py-1">Severity {item.severity}/5</span>
                    <span className="rounded-full bg-white px-3 py-1 capitalize">{item.intent}</span>
                    <span className="rounded-full bg-white px-3 py-1 font-mono">{item.reviewId.slice(0, 8)}…</span>
                  </footer>
                </blockquote>
              )) : <p className="text-sm text-slate-500">Evidence is loading from the review-results database.</p>}
            </div>
          </article>
        </section>

        <section className="mt-8 min-w-0 rounded-3xl border border-white/70 bg-white p-6 shadow-[0_18px_50px_rgba(15,23,42,0.07)]">
          <div>
            <p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">Trend</p>
            <h2 className="mt-2 text-2xl font-semibold tracking-tight">Monthly complaint share</h2>
            <p className="mt-2 text-sm text-slate-500">Complaint and cancellation reviews divided by all sampled reviews in each month.</p>
          </div>
          <div className="mt-6 h-[310px] min-w-0">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={data.trends} margin={{ left: 0, right: 20, top: 10, bottom: 4 }}>
                <CartesianGrid stroke="#e2e8f0" vertical={false} />
                <XAxis dataKey="month" tick={{ fill: "#64748b", fontSize: 11 }} tickLine={false} axisLine={false} />
                <YAxis tickFormatter={(value) => percent.format(value)} tick={{ fill: "#64748b", fontSize: 11 }} tickLine={false} axisLine={false} width={52} />
                <Tooltip formatter={(value) => percent.format(Number(value))} />
                <Line type="monotone" dataKey="complaintShare" name="Complaint share" stroke="#127a46" strokeWidth={3} dot={{ r: 3, fill: "#127a46" }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="mt-8 rounded-3xl border border-white/70 bg-white p-6 shadow-[0_18px_50px_rgba(15,23,42,0.07)]">
          <div className="flex flex-wrap items-end justify-between gap-3">
            <div>
              <p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-500">Reproducible baseline</p>
              <h2 className="mt-2 text-2xl font-semibold tracking-tight">Issue ranking</h2>
            </div>
            <p className="text-sm text-slate-500">Priority score = severity sum</p>
          </div>
          <div className="mt-6 overflow-x-auto">
            <table className="w-full min-w-[720px] border-separate border-spacing-y-2 text-sm">
              <thead className="text-left text-xs uppercase tracking-[0.12em] text-slate-400">
                <tr><th className="px-4 py-2">Rank</th><th className="px-4 py-2">Issue</th><th className="px-4 py-2">Complaints</th><th className="px-4 py-2">Mean severity</th><th className="px-4 py-2">Priority</th></tr>
              </thead>
              <tbody>
                {data.rankings.map((item) => (
                  <tr key={item.issueId} className="bg-slate-50">
                    <td className="rounded-l-2xl px-4 py-4 font-semibold text-slate-500">{item.rank}</td>
                    <td className="px-4 py-4 font-semibold capitalize">{item.issueId.replace("issue_", "")}</td>
                    <td className="px-4 py-4">{number.format(item.complaintCount)}</td>
                    <td className="px-4 py-4">{item.meanSeverity.toFixed(2)}</td>
                    <td className="rounded-r-2xl px-4 py-4">
                      <div className="flex items-center gap-3">
                        <div className="h-2 flex-1 overflow-hidden rounded-full bg-slate-200"><div className="h-full rounded-full bg-[#1db954]" style={{ width: `${(item.priorityScore / maxPriority) * 100}%` }} /></div>
                        <span className="w-16 text-right font-mono">{number.format(item.priorityScore)}</span>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

        <footer className="py-10 text-sm leading-7 text-slate-500">
          <p><strong className="text-slate-700">Limitations.</strong> {data.recommendation.limitations}</p>
          <p className="mt-2">Public app reviews are self-selected historical evidence. Cancellation language is intent, not observed churn, and the dataset contains no revenue or customer-plan outcomes. The Golden-50 agreement metrics come from the pre-freeze Jev v1 contract; the final v2 contract separately passed all five adversarial cases.</p>
        </footer>
      </div>
    </main>
  );
}
