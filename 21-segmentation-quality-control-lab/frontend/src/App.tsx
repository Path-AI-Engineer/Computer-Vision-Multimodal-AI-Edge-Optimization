import { useEffect, useMemo, useState } from "react";
import { loadWorkspace, resolveApiUrl, runInspection } from "./api/client";
import type {
  Candidate,
  CurrentModel,
  ErrorGallery,
  EvaluationSummary,
  Inspection,
  ModelComparison,
  Sample,
  ThresholdPoint
} from "./api/types";
import { DecisionBadge } from "./components/DecisionBadge";
import { Icon } from "./components/Icon";
import { ImageCanvas } from "./components/ImageCanvas";
import { MetricCard } from "./components/MetricCard";

type Page = "overview" | "inspect" | "thresholds" | "evaluation" | "errors" | "model";

interface Workspace {
  model: CurrentModel;
  summary: EvaluationSummary;
  thresholds: ThresholdPoint[];
  errors: ErrorGallery;
  comparison: ModelComparison;
  samples: Sample[];
}

const navigation: Array<{ id: Page; label: string; icon: Parameters<typeof Icon>[0]["name"] }> = [
  { id: "overview", label: "Overview", icon: "grid" },
  { id: "inspect", label: "Inspect surface", icon: "scan" },
  { id: "thresholds", label: "Threshold lab", icon: "sliders" },
  { id: "evaluation", label: "Evaluation", icon: "chart" },
  { id: "errors", label: "Error analysis", icon: "alert" },
  { id: "model", label: "Model record", icon: "model" }
];

function formatPercent(value: number, digits = 1) {
  return `${(value * 100).toFixed(digits)}%`;
}

function SectionHeading({ eyebrow, title, copy }: { eyebrow: string; title: string; copy: string }) {
  return (
    <header className="section-heading">
      <span className="eyebrow">{eyebrow}</span>
      <h1>{title}</h1>
      <p>{copy}</p>
    </header>
  );
}

function StatusStrip({ workspace }: { workspace: Workspace }) {
  return (
    <div className="status-strip" aria-label="Workspace status">
      <span><i className="status-dot" /> Bundle ready</span>
      <span>{workspace.model.model_version}</span>
      <span>{workspace.summary.profile.replaceAll("_", " ")}</span>
      <span className="locked">Official test locked</span>
    </div>
  );
}

function Overview({ workspace, openInspect }: { workspace: Workspace; openInspect: () => void }) {
  const { summary, comparison } = workspace;
  const executed = comparison.candidates.filter((candidate) => candidate.status.toLowerCase() === "executed");
  return (
    <div className="page-stack">
      <section className="hero-panel">
        <div>
          <span className="eyebrow">PIXEL EVIDENCE → PIECE POLICY</span>
          <h1>See the defect.<br /><em>Explain the decision.</em></h1>
          <p>Surface QC Lab turns a real segmentation probability map into an auditable ACCEPT, REVIEW or REJECT outcome.</p>
          <div className="hero-actions">
            <button className="button button-primary" onClick={openInspect}>Inspect a surface <Icon name="arrow" /></button>
            <a className="button button-secondary" href="/docs" target="_blank" rel="noreferrer">Open API contract</a>
          </div>
        </div>
        <div className="hero-orbit" aria-hidden="true">
          <div className="orbit orbit-one" />
          <div className="orbit orbit-two" />
          <div className="quality-core"><Icon name="layers" /><span>MASK</span><strong>QC</strong></div>
          <span className="orbit-label label-one">probability</span>
          <span className="orbit-label label-two">policy</span>
          <span className="orbit-label label-three">evidence</span>
        </div>
      </section>

      <section className="metric-grid">
        <MetricCard eyebrow="Macro Dice" value={formatPercent(summary.pixel_metrics.macro_dice)} detail="Validation images, including clean pieces" tone="good" />
        <MetricCard eyebrow="Defect recall" value={formatPercent(summary.piece_metrics.defect_recall)} detail={`${summary.defective_images} defective qualification pieces`} tone="good" />
        <MetricCard eyebrow="Pixel threshold" value={summary.pixel_threshold.toFixed(2)} detail="Selected on validation only" />
        <MetricCard eyebrow="Local p95" value={`${summary.latency.p95_ms.toFixed(1)} ms`} detail="CPU qualification, not a cloud SLA" />
      </section>

      <section className="two-column">
        <article className="panel pipeline-panel">
          <div className="panel-heading"><div><span className="eyebrow">RUNTIME CHAIN</span><h2>One evidence path</h2></div><Icon name="layers" /></div>
          <div className="pipeline">
            {["Validate image", "Pixel probability", "Threshold mask", "Measure area", "Apply policy"].map((step, index) => (
              <div className="pipeline-step" key={step}><span>{String(index + 1).padStart(2, "0")}</span><strong>{step}</strong>{index < 4 && <Icon name="arrow" />}</div>
            ))}
          </div>
        </article>
        <article className="panel boundary-panel">
          <div className="panel-heading"><div><span className="eyebrow">EVIDENCE BOUNDARY</span><h2>What this result means</h2></div><Icon name="shield" /></div>
          <p>The software vertical and Small U-Net are real. The current metrics come from deterministic procedural surfaces, not KSDD2.</p>
          <dl><div><dt>Official dataset</dt><dd>Not acquired</dd></div><div><dt>Official test</dt><dd>Locked</dd></div><div><dt>Industrial guarantee</dt><dd>Not claimed</dd></div></dl>
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading"><div><span className="eyebrow">MODEL LADDER</span><h2>Compared under one qualification scope</h2></div><span className="count-chip">{executed.length} executed</span></div>
        <div className="candidate-row">
          {comparison.candidates.map((candidate) => <CandidateCard candidate={candidate} key={candidate.model_id} />)}
        </div>
      </section>
    </div>
  );
}

function CandidateCard({ candidate }: { candidate: Candidate }) {
  const executed = candidate.status.toLowerCase() === "executed";
  return (
    <article className={`candidate-card ${candidate.selected ? "candidate-selected" : ""}`}>
      <div><span className={`state-dot ${executed ? "state-executed" : "state-pending"}`} />{candidate.status}</div>
      <h3>{candidate.model_id.replaceAll("-", " ")}</h3>
      {candidate.pixel_metrics ? <strong>{formatPercent(candidate.pixel_metrics.macro_dice)} Dice</strong> : <p>{candidate.reason}</p>}
      {candidate.selected && <span className="selected-label"><Icon name="check" /> Selected bundle</span>}
    </article>
  );
}

function InspectPage({ workspace }: { workspace: Workspace }) {
  const [selected, setSelected] = useState(workspace.samples[0]?.sample_id ?? "");
  const [file, setFile] = useState<File | undefined>();
  const [threshold, setThreshold] = useState(workspace.summary.pixel_threshold);
  const [result, setResult] = useState<Inspection | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState("");

  async function execute() {
    setRunning(true);
    setError("");
    try {
      setResult(await runInspection({ sampleId: file ? undefined : selected, file, pixelThreshold: threshold }));
    } catch (requestError) {
      setError(requestError instanceof Error ? requestError.message : "Inspection failed.");
    } finally {
      setRunning(false);
    }
  }

  useEffect(() => { void execute(); }, []);

  return (
    <div className="page-stack">
      <SectionHeading eyebrow="LIVE BUNDLE INFERENCE" title="Inspect one surface." copy="Choose qualification evidence or upload a controlled image. Every rendered mask comes from the selected Small U-Net bundle." />
      <section className="inspect-layout">
        <aside className="panel source-panel">
          <div className="panel-heading"><div><span className="eyebrow">INPUT SOURCE</span><h2>Evidence tray</h2></div><span className="count-chip">{workspace.samples.length}</span></div>
          <div className="sample-grid">
            {workspace.samples.map((sample) => (
              <button className={`sample-card ${selected === sample.sample_id && !file ? "sample-active" : ""}`} key={sample.sample_id} onClick={() => { setSelected(sample.sample_id); setFile(undefined); }}>
                <img src={resolveApiUrl(sample.image_url)} alt={`Qualification surface ${sample.sample_id}`} />
                <span>{sample.sample_id}</span><small>{sample.defective ? "Known defect" : "Known clean"}</small>
              </button>
            ))}
          </div>
          <label className="upload-control">
            <Icon name="upload" /><span><strong>{file?.name ?? "Upload another surface"}</strong><small>PNG, JPEG or WebP · max 6 MB</small></span>
            <input type="file" accept="image/png,image/jpeg,image/webp" onChange={(event) => setFile(event.target.files?.[0])} />
          </label>
          <label className="range-label" htmlFor="inspection-threshold"><span>Pixel threshold</span><output>{threshold.toFixed(2)}</output></label>
          <input id="inspection-threshold" className="range" type="range" min="0.05" max="0.95" step="0.05" value={threshold} onChange={(event) => setThreshold(Number(event.target.value))} />
          <button className="button button-primary button-wide" onClick={execute} disabled={running}>{running ? "Running U-Net…" : "Run inspection"}<Icon name="arrow" /></button>
          {error && <div className="error-banner" role="alert">{error}</div>}
        </aside>

        <section className="results-column">
          {result ? <InspectionResult result={result} /> : <div className="panel empty-result"><div className="loader-ring" /><h2>Preparing evidence</h2><p>The approved bundle is loading.</p></div>}
        </section>
      </section>
    </div>
  );
}

function InspectionResult({ result }: { result: Inspection }) {
  const panels = [
    ["Source image", result.image_uri, false],
    ["Pixel probability", result.mask_probability_uri, false],
    [`Binary mask · ${result.pixel_threshold.toFixed(2)}`, result.binary_mask_uri, true],
    ["Decision overlay", result.overlay_uri, false]
  ] as const;
  return (
    <>
      <section className="decision-console panel">
        <div><span className="eyebrow">INSPECTION OUTCOME</span><div className="decision-line"><DecisionBadge decision={result.decision} /><span>{result.defect_detected ? "Defect evidence retained" : "No retained defect component"}</span></div></div>
        <div className="decision-stats"><div><span>Defect area</span><strong>{result.defect_area_px} px</strong></div><div><span>Relative area</span><strong>{formatPercent(result.defect_area_ratio, 3)}</strong></div><div><span>Components</span><strong>{result.component_count}</strong></div><div><span>Latency</span><strong>{result.latency_ms.toFixed(1)} ms</strong></div></div>
      </section>
      <section className="evidence-grid">
        {panels.map(([label, src, pixelated]) => <article className="evidence-frame" key={label}><header><span>{label}</span><i /></header><ImageCanvas src={src} label={label} pixelated={pixelated} /></article>)}
      </section>
      <section className="comparison-panel panel">
        <div className="panel-heading"><div><span className="eyebrow">SAME IMAGE · TWO PATHS</span><h2>Classical baseline vs selected model</h2></div></div>
        <div className="comparison-images"><article><header><span>OpenCV morphology</span><DecisionBadge decision={result.baseline_decision} /></header><ImageCanvas src={result.baseline_overlay_uri} label="OpenCV baseline overlay" /></article><article><header><span>Small U-Net</span><DecisionBadge decision={result.decision} /></header><ImageCanvas src={result.overlay_uri} label="Small U-Net overlay" /></article></div>
      </section>
      <p className="request-line">Request <code>{result.request_id.slice(0, 12)}</code> · {result.model_version}</p>
    </>
  );
}

function ThresholdLab({ workspace }: { workspace: Workspace }) {
  const max = Math.max(...workspace.thresholds.map((point) => point.macro_dice));
  return (
    <div className="page-stack">
      <SectionHeading eyebrow="VALIDATION-ONLY CALIBRATION" title="One slider. Two different decisions." copy="The pixel threshold creates a binary mask. The piece policy then interprets retained area. They are versioned separately." />
      <section className="threshold-layout">
        <article className="panel chart-panel">
          <div className="panel-heading"><div><span className="eyebrow">THRESHOLD SWEEP</span><h2>Macro pixel metrics</h2></div><span className="selected-threshold">Selected {workspace.summary.pixel_threshold.toFixed(2)}</span></div>
          <div className="threshold-chart" role="img" aria-label="Dice and recall by pixel threshold">
            {workspace.thresholds.map((point) => (
              <div className={`threshold-column ${point.threshold === workspace.summary.pixel_threshold ? "threshold-selected" : ""}`} key={point.threshold}>
                <div className="bar-stack"><i className="bar bar-recall" style={{ height: `${(point.macro_recall / max) * 100}%` }} title={`Recall ${formatPercent(point.macro_recall)}`} /><i className="bar bar-dice" style={{ height: `${(point.macro_dice / max) * 100}%` }} title={`Dice ${formatPercent(point.macro_dice)}`} /></div>
                <span>{point.threshold.toFixed(1)}</span>
              </div>
            ))}
          </div>
          <div className="chart-legend"><span><i className="legend-dice" /> Dice</span><span><i className="legend-recall" /> Recall</span></div>
        </article>
        <aside className="panel policy-card">
          <span className="eyebrow">PIECE POLICY</span><h2>Area becomes action</h2>
          <div className="policy-rule accept-rule"><span>ACCEPT</span><strong>&lt; {formatPercent(workspace.model.inspection_policy.review_area_ratio, 2)}</strong><p>No retained component exceeds review area.</p></div>
          <div className="policy-rule review-rule"><span>REVIEW</span><strong>{formatPercent(workspace.model.inspection_policy.review_area_ratio, 2)}–{formatPercent(workspace.model.inspection_policy.reject_area_ratio, 1)}</strong><p>Human review remains part of the policy.</p></div>
          <div className="policy-rule reject-rule"><span>REJECT</span><strong>≥ {formatPercent(workspace.model.inspection_policy.reject_area_ratio, 1)}</strong><p>Large retained defect area triggers rejection.</p></div>
          <p className="policy-footnote">Components smaller than {workspace.model.inspection_policy.minimum_component_area_px} px are removed before policy evaluation.</p>
        </aside>
      </section>
    </div>
  );
}

function EvaluationPage({ workspace }: { workspace: Workspace }) {
  const { summary, comparison } = workspace;
  return (
    <div className="page-stack">
      <SectionHeading eyebrow="QUALIFICATION EVIDENCE" title="Pixel quality and piece risk stay separate." copy="Clean images remain in the macro average. Operational error rates are reported beside segmentation metrics, never merged into one score." />
      <section className="metric-grid">
        <MetricCard eyebrow="Macro IoU" value={formatPercent(summary.pixel_metrics.macro_iou)} detail="Pixel overlap across every validation image" />
        <MetricCard eyebrow="PR AUC" value={formatPercent(summary.pixel_metrics.pr_auc ?? 0)} detail="Probability ranking under imbalance" />
        <MetricCard eyebrow="False accept" value={formatPercent(summary.piece_metrics.false_accept_rate)} detail="Defective pieces incorrectly accepted" tone="good" />
        <MetricCard eyebrow="False reject" value={formatPercent(summary.piece_metrics.false_reject_rate)} detail="Clean pieces incorrectly flagged" tone="good" />
      </section>
      <section className="panel comparison-table-panel">
        <div className="panel-heading"><div><span className="eyebrow">CANDIDATE REGISTER</span><h2>Executed and excluded candidates</h2></div><span className="count-chip">validation scope</span></div>
        <div className="comparison-table" role="table">
          <div className="comparison-row comparison-head" role="row"><span>Candidate</span><span>Status</span><span>Dice</span><span>Defect recall</span><span>Selection</span></div>
          {comparison.candidates.map((candidate) => <div className="comparison-row" role="row" key={candidate.model_id}><strong>{candidate.model_id}</strong><span>{candidate.status}</span><span>{candidate.pixel_metrics ? formatPercent(candidate.pixel_metrics.macro_dice) : "—"}</span><span>{candidate.piece_metrics ? formatPercent(candidate.piece_metrics.defect_recall) : "—"}</span><span>{candidate.selected ? "Selected" : candidate.reason ?? "Reference"}</span></div>)}
        </div>
      </section>
      <section className="panel validation-scope"><Icon name="shield" /><div><span className="eyebrow">DO NOT CROSS THIS LINE</span><h2>{summary.warning}</h2><p>KSDD2 training, transfer candidates and official test execution remain open work.</p></div></section>
    </div>
  );
}

function ErrorsPage({ workspace }: { workspace: Workspace }) {
  const { errors } = workspace;
  return (
    <div className="page-stack">
      <SectionHeading eyebrow="FAILURE ANALYSIS" title="Errors are evidence, including zero observed errors." copy="The gallery is generated from validation predictions. It never fabricates a failure example to make the interface look busier." />
      <section className="error-summary"><MetricCard eyebrow="False accepts" value={String(errors.false_accepts)} detail="Observed validation failures" tone={errors.false_accepts ? "warning" : "good"} /><MetricCard eyebrow="False rejects" value={String(errors.false_rejects)} detail="Observed validation failures" tone={errors.false_rejects ? "warning" : "good"} /><MetricCard eyebrow="Evaluation scope" value="12 pieces" detail={errors.scope.replaceAll("_", " ")} /></section>
      <section className="panel honest-empty">
        {errors.errors.length === 0 ? <><div className="empty-mark"><Icon name="check" /></div><span className="eyebrow">NO SELECTED-MODEL ERRORS OBSERVED</span><h2>The procedural validation slice produced no false accept or false reject.</h2><p>This is not proof of generalization. The slice contains only twelve deterministic qualification images; KSDD2 may expose materially different failures.</p></> : errors.errors.map((error) => <article key={error.sample_id}><strong>{error.error_type}</strong><span>{error.sample_id}</span></article>)}
      </section>
    </div>
  );
}

function ModelPage({ workspace }: { workspace: Workspace }) {
  const { model } = workspace;
  return (
    <div className="page-stack">
      <SectionHeading eyebrow="IMMUTABLE MODEL RECORD" title="The mask travels with its context." copy="Architecture, normalization, selected thresholds, policy and evidence boundary are loaded from the same hash-verified bundle." />
      <section className="model-layout">
        <article className="panel model-identity"><div className="model-monogram">U</div><span className="eyebrow">SELECTED BUNDLE</span><h2>{model.architecture}</h2><p>{model.model_version}</p><code>{model.checkpoint_sha256.slice(0, 24)}…</code><div className="model-meta"><div><span>Parameters</span><strong>{model.training.parameters.toLocaleString()}</strong></div><div><span>Input</span><strong>{model.input_size.join(" × ")}</strong></div><div><span>Best epoch</span><strong>{model.training.best_epoch}</strong></div><div><span>Train time</span><strong>{model.training.training_seconds.toFixed(1)} s</strong></div></div></article>
        <article className="panel limitation-card"><span className="eyebrow">LIMITATIONS</span><h2>Read before reuse</h2><ul>{model.limitations.map((limitation) => <li key={limitation}><Icon name="alert" />{limitation}</li>)}</ul></article>
      </section>
      <section className="panel training-curve-panel"><div className="panel-heading"><div><span className="eyebrow">TRAINING TRACE</span><h2>Loss by epoch</h2></div><span className="count-chip">seed 21021</span></div><div className="loss-trace">{model.training.history.map((epoch) => <div key={epoch.epoch}><span>{epoch.epoch}</span><i className="loss-train" style={{ height: `${epoch.train_loss * 70}%` }} /><i className="loss-validation" style={{ height: `${epoch.validation_loss * 70}%` }} /><small>{epoch.validation_loss.toFixed(3)}</small></div>)}</div><div className="chart-legend"><span><i className="legend-train" /> Training</span><span><i className="legend-validation" /> Validation</span></div></section>
    </div>
  );
}

export default function App() {
  const [page, setPage] = useState<Page>("overview");
  const [workspace, setWorkspace] = useState<Workspace | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    loadWorkspace().then(setWorkspace).catch((requestError) => setError(requestError instanceof Error ? requestError.message : "Workspace unavailable."));
  }, []);

  const currentLabel = useMemo(() => navigation.find((item) => item.id === page)?.label ?? "Workspace", [page]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand"><div className="brand-mark"><Icon name="scan" /></div><div><strong>Surface QC</strong><span>Inspection intelligence</span></div></div>
        <nav aria-label="Workspace navigation">{navigation.map((item) => <button key={item.id} className={page === item.id ? "nav-active" : ""} onClick={() => setPage(item.id)}><Icon name={item.icon} /><span>{item.label}</span>{page === item.id && <i />}</button>)}</nav>
        <div className="sidebar-status"><span><i /> Model service</span><strong>{workspace ? "Ready" : "Connecting"}</strong><small>Plan 04 · Project 21</small></div>
      </aside>
      <main>
        <header className="topbar"><div><span>AI ENGINEER · PROJECT 21</span><strong>{currentLabel}</strong></div><div className="topbar-actions"><span className="environment"><i /> Local evidence</span><span className="operator">QC</span></div></header>
        <div className="content">
          {error && <div className="fatal-state"><Icon name="alert" /><h1>Evidence workspace unavailable</h1><p>{error}</p><button className="button button-primary" onClick={() => window.location.reload()}>Retry</button></div>}
          {!workspace && !error && <div className="loading-state"><div className="loader-ring" /><span>Verifying bundle hashes</span><h1>Preparing the inspection lab.</h1></div>}
          {workspace && <><StatusStrip workspace={workspace} />{page === "overview" && <Overview workspace={workspace} openInspect={() => setPage("inspect")} />}{page === "inspect" && <InspectPage workspace={workspace} />}{page === "thresholds" && <ThresholdLab workspace={workspace} />}{page === "evaluation" && <EvaluationPage workspace={workspace} />}{page === "errors" && <ErrorsPage workspace={workspace} />}{page === "model" && <ModelPage workspace={workspace} />}</>}
        </div>
      </main>
    </div>
  );
}
