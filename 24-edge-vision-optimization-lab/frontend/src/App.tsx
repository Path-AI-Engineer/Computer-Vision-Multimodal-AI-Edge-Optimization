import { useEffect, useMemo, useState } from "react";
import { api } from "./api/client";
import type { BenchmarkRow, BenchmarkSummary, Environment, ParetoReport, ParityComparison, Prediction, PruningReport, Readiness, Sample, Variant } from "./api/types";
import { Icon, type IconName } from "./components/Icon";
import { MetricCard } from "./components/MetricCard";
import { ParetoPlot } from "./components/ParetoPlot";

type View = "overview" | "inference" | "variants" | "benchmark" | "evidence";

const navigation: { id: View; label: string; detail: string; icon: IconName }[] = [
  { id: "overview", label: "Decision desk", detail: "Measured trade-offs", icon: "overview" },
  { id: "inference", label: "Inference lab", detail: "Compare one sample", icon: "pulse" },
  { id: "variants", label: "Variant registry", detail: "Artifacts and status", icon: "layers" },
  { id: "benchmark", label: "Benchmark matrix", detail: "Quality and cost", icon: "chart" },
  { id: "evidence", label: "Evidence room", detail: "Parity and environment", icon: "shield" }
];

function percent(value: number) { return `${(value * 100).toFixed(1)}%`; }
function latency(value: number) { return value < 0.1 ? `${(value * 1000).toFixed(2)} μs` : `${value.toFixed(2)} ms`; }
function size(value: number | null) { return value == null ? "—" : value < 0.1 ? `${(value * 1024).toFixed(2)} KB` : `${value.toFixed(2)} MB`; }

function StatusBadge({ status }: { status: Variant["status"] }) {
  const label = status === "APPROVED_QUALIFICATION" ? "Approved" : status === "EXPERIMENTAL_QUALIFICATION" ? "Experimental" : "Not run";
  return <span className={`status-badge ${status.toLowerCase()}`}><i/>{label}</span>;
}

function Overview({ summary, pareto, environment, pruning, onOpenInference }: { summary: BenchmarkSummary; pareto: ParetoReport; environment: Environment; pruning: PruningReport; onOpenInference: () => void }) {
  const baseline = summary.variants.find((item) => item.variant_id === "pytorch-fp32")!;
  const fastest = [...summary.variants].sort((a, b) => a.p50_ms - b.p50_ms)[0];
  const smallest = [...summary.variants].sort((a, b) => a.size_mb - b.size_mb)[0];
  const frontierIds = new Set(pareto.frontier.map((item) => item.variant_id));
  return <main className="page overview-page">
    <header className="hero">
      <div className="hero-copy"><span className="kicker">Edge inference · measured, not assumed</span><h1>Optimize the cost.<br/><em>Protect the signal.</em></h1><p>Compare quality, latency and artifact size under one recorded CPU environment. Every recommendation exposes the evidence boundary behind it.</p><div className="hero-actions"><button className="primary-action" onClick={onOpenInference}><Icon name="play"/> Run sample inference</button><span><i/> Qualification bundle online</span></div></div>
      <div className="efficiency-orbit" aria-hidden="true"><div className="orbit-ring ring-one"/><div className="orbit-ring ring-two"/><div className="processor-core"><Icon name="cpu"/><span>CPU</span></div><span className="orbit-node node-one">F1</span><span className="orbit-node node-two">P50</span><span className="orbit-node node-three">INT8</span></div>
    </header>
    <section className="metric-grid">
      <MetricCard label="Reference quality" value={percent(baseline.macro_f1)} detail="FP32 macro F1" icon="shield" tone="blue"/>
      <MetricCard label="Fastest measured" value={latency(fastest.p50_ms)} detail={fastest.display_name} icon="bolt" tone="green"/>
      <MetricCard label="Smallest artifact" value={size(smallest.size_mb)} detail={smallest.display_name} icon="box" tone="violet"/>
      <MetricCard label="Unstructured speedup" value={`${pruning.observed_speedup.toFixed(2)}×`} detail="observed, not theoretical" icon="pulse" tone="amber"/>
    </section>
    <section className="dashboard-grid">
      <article className="panel pareto-panel"><div className="panel-heading"><div><span className="kicker">Multi-objective view</span><h2>The frontier, without a fake winner.</h2></div><span className="profile-chip"><Icon name="cpu"/>{environment.profile}</span></div><ParetoPlot rows={summary.variants} frontierIds={frontierIds}/><div className="plot-legend"><span><i className="frontier-dot"/>Pareto frontier</span><span><i/>Dominated variant</span><small>Circle size represents the qualification artifact size.</small></div></article>
      <aside className="panel recommendation-panel"><span className="kicker">Constraint-aware picks</span><h2>Deploy for the requirement.</h2>{Object.entries(pareto.recommendations).map(([profile, id]) => { const row = summary.variants.find((item) => item.variant_id === id); return <div className="recommendation" key={profile}><div><span>{profile.replaceAll("_", " ")}</span><strong>{row?.display_name}</strong></div><Icon name="chevron"/></div>; })}<div className="boundary-note"><Icon name="info"/><p>{summary.claim_boundary}</p></div></aside>
    </section>
  </main>;
}

function InferenceLab({ variants, samples }: { variants: Variant[]; samples: Sample[] }) {
  const approved = variants.filter((item) => item.status === "APPROVED_QUALIFICATION");
  const [variantId, setVariantId] = useState(approved[0]?.variant_id ?? "");
  const [sampleId, setSampleId] = useState(samples[0]?.sample_id ?? "");
  const [result, setResult] = useState<Prediction | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const selected = samples.find((item) => item.sample_id === sampleId);
  async function run() { setBusy(true); setError(""); try { setResult(await api.predict(variantId, sampleId)); } catch (reason) { setError(reason instanceof Error ? reason.message : "Inference failed."); } finally { setBusy(false); } }
  return <main className="page inference-page"><header className="page-heading"><div><span className="kicker">One input · multiple runtime contracts</span><h1>Inspect a prediction.<br/><em>Then inspect its cost.</em></h1><p>The online path accepts only approved qualification variants. It never substitutes a NOT_RUN research artifact.</p></div></header>
    {error && <div className="error-banner"><Icon name="alert"/><div><strong>Prediction unavailable</strong><p>{error}</p></div></div>}
    <div className="inference-layout"><section className="panel sample-workbench"><div className="panel-heading"><div><span className="kicker">Public fixture</span><h2>Select visual evidence</h2></div><span className="count-chip">{samples.length} samples</span></div><div className="sample-grid">{samples.map((sample) => <button key={sample.sample_id} className={sample.sample_id === sampleId ? "sample-card selected" : "sample-card"} onClick={() => { setSampleId(sample.sample_id); setResult(null); }} aria-pressed={sample.sample_id === sampleId}><img src={sample.image_url} alt={`Generated ${sample.label} qualification sample`}/><span>{sample.sample_id}</span><strong>{sample.label}</strong></button>)}</div></section>
      <aside className="panel inference-console"><div className="selected-preview">{selected && <img src={selected.image_url} alt={`Selected ${selected.label} fixture`}/>}<div><span>Ground truth fixture</span><strong>{selected?.label ?? "Select a sample"}</strong><small>{selected?.split} split · generated</small></div></div><label htmlFor="variant-select">Approved runtime variant</label><select id="variant-select" value={variantId} onChange={(event) => { setVariantId(event.target.value); setResult(null); }}>{approved.map((variant) => <option key={variant.variant_id} value={variant.variant_id}>{variant.display_name} · {variant.precision}</option>)}</select><button className="primary-action wide" disabled={!sampleId || !variantId || busy} onClick={run}><Icon name="play"/>{busy ? "Evaluating…" : "Run qualification inference"}</button>
      {result ? <div className="prediction-output"><div className="output-heading"><div><span className="kicker">Ranked output</span><h3>{result.predictions[0].label}</h3></div><strong>{latency(result.observed_latency_ms)}</strong></div>{result.predictions.map((item, index) => <div className="probability-row" key={item.label}><span>0{index + 1}</span><strong>{item.label}</strong><div><i style={{ width: `${item.probability * 100}%` }}/></div><em>{percent(item.probability)}</em></div>)}<small>{result.model_version} · request latency is not the benchmark latency.</small></div> : <div className="empty-output"><Icon name="pulse"/><strong>No inference yet</strong><p>Choose one fixture and run an approved variant.</p></div>}</aside>
    </div>
  </main>;
}

function VariantRegistry({ variants }: { variants: Variant[] }) {
  return <main className="page"><header className="page-heading compact"><div><span className="kicker">Immutable compatibility contracts</span><h1>Every variant earns<br/><em>its registry status.</em></h1><p>Runtime, precision, preprocessing and environment travel with the artifact. Missing evidence remains visible.</p></div></header><section className="variant-cards">{variants.map((variant) => <article className={`variant-card ${variant.status === "NOT_RUN" ? "disabled" : ""}`} key={variant.variant_id}><div className="variant-card-head"><div className="variant-glyph"><Icon name={variant.precision === "INT8" ? "bolt" : "cpu"}/></div><StatusBadge status={variant.status}/></div><span className="variant-id">{variant.variant_id}</span><h2>{variant.display_name}</h2><p>{variant.optimization} · {variant.runtime}</p><dl><div><dt>Precision</dt><dd>{variant.precision}</dd></div><div><dt>Macro F1</dt><dd>{variant.quality ? percent(variant.quality.macro_f1) : "Not measured"}</dd></div><div><dt>P50 latency</dt><dd>{variant.latency ? latency(variant.latency.p50_ms) : "Not measured"}</dd></div><div><dt>Artifact size</dt><dd>{size(variant.artifact_size_mb)}</dd></div><div><dt>Sparsity</dt><dd>{variant.effective_sparsity == null ? "—" : percent(variant.effective_sparsity)}</dd></div><div><dt>Parameters</dt><dd>{variant.parameters?.toLocaleString() ?? "—"}</dd></div></dl><div className="variant-boundary"><Icon name="info"/><span>{variant.claim_boundary}</span></div></article>)}</section></main>;
}

function BenchmarkMatrix({ summary, pareto }: { summary: BenchmarkSummary; pareto: ParetoReport }) {
  const [precision, setPrecision] = useState("all");
  const rows = summary.variants.filter((item) => precision === "all" || item.precision === precision);
  const frontier = new Set(pareto.frontier.map((item) => item.variant_id));
  return <main className="page"><header className="page-heading compact"><div><span className="kicker">Paired environment · batch 1</span><h1>Compare what changed.<br/><em>Keep what did not.</em></h1><p>Quality is recalculated per variant and timings use the same host, warmup and iteration contract.</p></div><div className="filter-control"><label htmlFor="precision-filter">Precision</label><select id="precision-filter" value={precision} onChange={(event) => setPrecision(event.target.value)}><option value="all">All precisions</option><option value="FP32">FP32</option><option value="INT8">INT8</option></select></div></header><section className="panel benchmark-table-panel"><div className="table-scroll"><table><thead><tr><th>Variant</th><th>Status</th><th>Macro F1</th><th>Top-1</th><th>P50</th><th>P95</th><th>Size</th><th>Sparsity</th><th>Pareto</th></tr></thead><tbody>{rows.map((row) => <tr key={row.variant_id}><td><strong>{row.display_name}</strong><small>{row.runtime} · {row.precision}</small></td><td><StatusBadge status={row.status}/></td><td>{percent(row.macro_f1)}</td><td>{percent(row.top1_accuracy)}</td><td>{latency(row.p50_ms)}</td><td>{latency(row.p95_ms)}</td><td>{size(row.size_mb)}</td><td>{percent(row.effective_sparsity)}</td><td>{frontier.has(row.variant_id) ? <span className="pareto-badge"><Icon name="check"/>Yes</span> : "—"}</td></tr>)}</tbody></table></div></section><div className="boundary-strip"><Icon name="info"/><div><strong>Measurement boundary</strong><p>{summary.claim_boundary}</p></div></div></main>;
}

function EvidenceRoom({ environment, parity, pruning }: { environment: Environment; parity: ParityComparison[]; pruning: PruningReport }) {
  return <main className="page"><header className="page-heading compact"><div><span className="kicker">Reproducibility before acceleration</span><h1>Audit the environment.<br/><em>Read the failures.</em></h1><p>Export is not acceptance. Parity, observed latency and execution context decide whether an artifact is eligible.</p></div></header><section className="environment-banner"><div className="environment-icon"><Icon name="cpu"/></div><div><span className="kicker">Measured host</span><h2>{environment.hardware_model}</h2><p>{environment.os}</p></div><span className="profile-chip">{environment.profile}</span></section><div className="evidence-grid"><section className="panel"><div className="panel-heading"><div><span className="kicker">Runtime parity</span><h2>Oracle comparisons</h2></div></div><div className="parity-list">{parity.map((item) => <article key={item.candidate_variant}><span className={item.passed ? "parity-icon passed" : "parity-icon failed"}><Icon name={item.passed ? "check" : "alert"}/></span><div><strong>{item.candidate_variant}</strong><p>Top-1 agreement {percent(item.top1_agreement)} · max error {item.max_absolute_error.toFixed(4)}</p></div><em>{item.passed ? "PASS" : "REVIEW"}</em></article>)}</div></section><section className="panel"><div className="panel-heading"><div><span className="kicker">Benchmark contract</span><h2>Recorded controls</h2></div></div><dl className="environment-list"><div><dt>Provider</dt><dd>{environment.execution_provider}</dd></div><div><dt>Threads</dt><dd>{environment.threads}</dd></div><div><dt>Warmup</dt><dd>{environment.warmup_iterations} iterations</dd></div><div><dt>Measured</dt><dd>{environment.measured_iterations} iterations</dd></div><div><dt>Input</dt><dd>{environment.input_size.join(" × ")} · {environment.input_dtype}</dd></div><div><dt>Energy</dt><dd>{environment.energy}</dd></div></dl></section></div><section className="negative-result"><Icon name="alert"/><div><span className="kicker">Negative result retained</span><h2>{percent(pruning.effective_sparsity)} zero weights produced {pruning.observed_speedup.toFixed(2)}× observed speedup.</h2><p>{pruning.interpretation}</p></div></section><div className="boundary-strip"><Icon name="shield"/><div><strong>Host CPU is not an edge device</strong><p>{environment.claim_boundary}</p></div></div></main>;
}

export default function App() {
  const [view, setView] = useState<View>("overview");
  const [menuOpen, setMenuOpen] = useState(false);
  const [ready, setReady] = useState<Readiness | null>(null);
  const [variants, setVariants] = useState<Variant[]>([]);
  const [samples, setSamples] = useState<Sample[]>([]);
  const [summary, setSummary] = useState<BenchmarkSummary | null>(null);
  const [pareto, setPareto] = useState<ParetoReport | null>(null);
  const [environment, setEnvironment] = useState<Environment | null>(null);
  const [parity, setParity] = useState<ParityComparison[]>([]);
  const [pruning, setPruning] = useState<PruningReport | null>(null);
  const [error, setError] = useState("");
  useEffect(() => { Promise.all([api.ready(), api.variants(), api.samples(), api.benchmark(), api.pareto(), api.environment(), api.parity(), api.pruning()]).then(([r, v, s, b, p, e, pa, pr]) => { setReady(r); setVariants(v); setSamples(s); setSummary(b); setPareto(p); setEnvironment(e); setParity(pa); setPruning(pr); }).catch((reason) => setError(reason instanceof Error ? reason.message : "Runtime unavailable.")); }, []);
  const current = useMemo(() => navigation.find((item) => item.id === view)!, [view]);
  const loaded = summary && pareto && environment && pruning;
  return <div className="app-shell"><aside className={menuOpen ? "sidebar open" : "sidebar"}><button className="sidebar-close" onClick={() => setMenuOpen(false)} aria-label="Close navigation"><Icon name="close"/></button><div className="brand"><div><Icon name="bolt"/></div><span><strong>EdgeForge</strong><small>Inference economics</small></span></div><span className="nav-label">Workspace</span><nav>{navigation.map((item) => <button key={item.id} className={item.id === view ? "active" : ""} onClick={() => { setView(item.id); setMenuOpen(false); }}><Icon name={item.icon}/><span><strong>{item.label}</strong><small>{item.detail}</small></span>{item.id === view && <i/>}</button>)}</nav><div className="sidebar-runtime"><span><i className={ready ? "online" : ""}/>{ready ? "Registry ready" : "Connecting"}</span><small>{ready?.approved_variants ?? 0} approved variants · rc.1</small></div></aside>{menuOpen && <button className="mobile-overlay" onClick={() => setMenuOpen(false)} aria-label="Close navigation overlay"/>}<section className="workspace"><header className="topbar"><button className="menu-button" onClick={() => setMenuOpen(true)} aria-label="Open navigation"><Icon name="menu"/></button><div><span>AI Engineer · Plan 04 · Project 24</span><strong>{current.label}</strong></div><div className="topbar-actions"><span className="runtime-pill"><i className={ready ? "online" : ""}/>{ready ? "Qualification online" : "Runtime unavailable"}</span><span className="version-pill">v1.0.0-rc.1</span></div></header>{error && <div className="global-error"><Icon name="alert"/><div><strong>Evidence unavailable</strong><p>{error}</p></div></div>}{!loaded && !error && <div className="loading-state"><span/><strong>Loading measured evidence…</strong></div>}{loaded && view === "overview" && <Overview summary={summary} pareto={pareto} environment={environment} pruning={pruning} onOpenInference={() => setView("inference")}/>} {view === "inference" && <InferenceLab variants={variants} samples={samples}/>} {view === "variants" && <VariantRegistry variants={variants}/>} {loaded && view === "benchmark" && <BenchmarkMatrix summary={summary} pareto={pareto}/>} {loaded && view === "evidence" && <EvidenceRoom environment={environment} parity={parity} pruning={pruning}/>}</section></div>;
}
