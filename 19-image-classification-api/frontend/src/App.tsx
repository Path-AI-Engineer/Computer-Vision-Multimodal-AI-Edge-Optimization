import { ChangeEvent, useEffect, useMemo, useState } from "react";
import {
  assetUrl,
  classify,
  classifySample,
  getJson,
  Prediction,
  Sample
} from "./api";

type View = "overview" | "classify" | "evaluation" | "errors" | "models" | "responsible";
type Metrics = {
  macro_f1: number;
  accuracy_top_1: number;
  accuracy_top_5: number;
  expected_calibration_error: number;
  evaluation_scope: string;
  test_status: string;
};
type ModelComparison = {
  selected_model: string;
  warning: string;
  models: Array<Record<string, string | number | boolean>>;
};
type ErrorGallery = {
  scope: string;
  items: Array<{
    sample_id: string;
    image_url: string;
    truth: string;
    prediction: string;
    confidence: number;
    correct: boolean;
    category: string;
  }>;
};

const navigation: Array<{ id: View; label: string; icon: string }> = [
  { id: "overview", label: "Overview", icon: "grid" },
  { id: "classify", label: "Classify", icon: "scan" },
  { id: "evaluation", label: "Evaluation", icon: "chart" },
  { id: "errors", label: "Error gallery", icon: "layers" },
  { id: "models", label: "Model comparison", icon: "branch" },
  { id: "responsible", label: "Responsible use", icon: "shield" }
];

function Icon({ name }: { name: string }) {
  const path = {
    grid: "M4 4h6v6H4zM14 4h6v6h-6zM4 14h6v6H4zM14 14h6v6h-6z",
    scan: "M4 8V4h4M16 4h4v4M20 16v4h-4M8 20H4v-4M8 12h8",
    chart: "M4 19V9m6 10V5m6 14v-7m4 7H2",
    layers: "m12 3 9 5-9 5-9-5 9-5Zm-9 10 9 5 9-5M3 17l9 5 9-5",
    branch: "M6 3v12a4 4 0 0 0 4 4h8M6 8h8a4 4 0 0 0 4-4V3",
    shield: "M12 3 4.5 6v5.5c0 4.7 3.2 8 7.5 9.5 4.3-1.5 7.5-4.8 7.5-9.5V6L12 3Z"
  }[name];
  return <svg aria-hidden="true" viewBox="0 0 24 24"><path d={path} /></svg>;
}

function Loading({ label = "Loading verified evidence" }: { label?: string }) {
  return <div className="loading"><span className="spinner" />{label}</div>;
}

function EvidenceBanner() {
  return (
    <div className="evidence-banner" role="note">
      <span className="signal" />
      <strong>Qualification evidence</strong>
      <span>Procedural validation data, not Oxford-IIIT Pet performance.</span>
      <code>TEST LOCKED</code>
    </div>
  );
}

function Overview({ metrics, onStart }: { metrics: Metrics | null; onStart: () => void }) {
  return (
    <section className="page overview-page">
      <div className="hero-grid">
        <div>
          <p className="eyebrow">Computer vision · Project 19</p>
          <h1>Inspect the prediction.<br /><span>Respect the boundary.</span></h1>
          <p className="lead">
            A fine-grained pet breed classification studio built around traceable artifacts,
            calibrated probabilities and explicit abstention.
          </p>
          <div className="hero-actions">
            <button className="primary" onClick={onStart}>Open classifier <span>→</span></button>
            <a className="secondary" href="/docs" target="_blank" rel="noreferrer">Explore API</a>
          </div>
        </div>
        <div className="vision-orbit" aria-label="Abstract feature extraction visualization">
          <div className="orbit orbit-a" /><div className="orbit orbit-b" />
          <div className="vision-core"><Icon name="scan" /></div>
          <span className="node node-a">RGB</span><span className="node node-b">HOG</span>
          <span className="node node-c">37</span>
        </div>
      </div>
      <EvidenceBanner />
      <div className="metric-grid">
        <Metric label="Breed labels" value="37" note="Cats and dogs" />
        <Metric label="Qualification macro F1" value={metrics ? pct(metrics.macro_f1) : "—"} note="Procedural validation" />
        <Metric label="Top-5 accuracy" value={metrics ? pct(metrics.accuracy_top_5) : "—"} note="Qualification only" />
        <Metric label="Official test" value="Locked" note="No leakage by design" tone="amber" />
      </div>
      <div className="two-column">
        <article className="panel statement">
          <p className="eyebrow">Decision surface</p>
          <h2>From image bytes to an auditable response.</h2>
          <div className="flow">
            {[
              ["01", "Validate", "JPEG, PNG or WebP; size and pixel limits"],
              ["02", "Transform", "EXIF-normalized RGB and versioned HOG"],
              ["03", "Calibrate", "Temperature-scaled probabilities"],
              ["04", "Respond", "Top-5, latency, versions and abstention"]
            ].map(([n, title, copy]) => <div className="flow-step" key={n}><span>{n}</span><div><b>{title}</b><small>{copy}</small></div></div>)}
          </div>
        </article>
        <article className="panel boundary-card">
          <p className="eyebrow">Evidence boundary</p>
          <h3>What this release proves</h3>
          <ul>
            <li>A deterministic 37-class qualification pipeline</li>
            <li>A deployable API and real inference artifact</li>
            <li>Calibration, latency and error-analysis surfaces</li>
          </ul>
          <h3>What it does not claim</h3>
          <ul className="muted-list">
            <li>Oxford-IIIT Pet benchmark performance</li>
            <li>Veterinary or identity-grade accuracy</li>
            <li>Executed ResNet or ViT comparison results</li>
          </ul>
        </article>
      </div>
    </section>
  );
}

function Metric({ label, value, note, tone }: { label: string; value: string; note: string; tone?: string }) {
  return <article className={`metric ${tone ?? ""}`}><small>{label}</small><strong>{value}</strong><span>{note}</span></article>;
}

function Classifier({ samples }: { samples: Sample[] }) {
  const [selected, setSelected] = useState<Sample | null>(samples[0] ?? null);
  const [preview, setPreview] = useState<string | null>(selected ? assetUrl(selected.image_url) : null);
  const [file, setFile] = useState<File | null>(null);
  const [prediction, setPrediction] = useState<Prediction | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!selected && samples.length) {
      setSelected(samples[0]);
      setPreview(assetUrl(samples[0].image_url));
    }
  }, [samples, selected]);

  function chooseSample(sample: Sample) {
    setSelected(sample); setFile(null); setPreview(assetUrl(sample.image_url)); setPrediction(null);
  }
  function chooseFile(event: ChangeEvent<HTMLInputElement>) {
    const next = event.target.files?.[0];
    if (!next) return;
    setFile(next); setSelected(null); setPreview(URL.createObjectURL(next)); setPrediction(null);
  }
  async function run() {
    setBusy(true); setError("");
    try {
      setPrediction(file ? await classify(file, file.name) : selected ? await classifySample(selected) : null);
    } catch (reason) { setError(reason instanceof Error ? reason.message : "Prediction failed"); }
    finally { setBusy(false); }
  }

  return (
    <section className="page">
      <header className="page-heading"><div><p className="eyebrow">Inference workspace</p><h1>Classify with context.</h1><p>Choose qualification evidence or upload your own image. The response preserves uncertainty.</p></div><span className="status-chip"><span className="signal" /> Bundle ready</span></header>
      <EvidenceBanner />
      {error && <div className="error-box" role="alert"><strong>Prediction unavailable</strong><span>{error}</span></div>}
      <div className="classify-grid">
        <article className="panel input-panel">
          <div className="panel-title"><div><p className="eyebrow">Input source</p><h2>Select evidence</h2></div><label className="upload-button">Upload image<input type="file" accept="image/png,image/jpeg,image/webp" onChange={chooseFile} /></label></div>
          <div className="preview-stage">{preview ? <img src={preview} alt="Selected inference input" /> : <span>No image selected</span>}<div className="scan-line" /></div>
          <div className="sample-strip" aria-label="Qualification samples">{samples.slice(0, 8).map(sample => <button className={selected?.sample_id === sample.sample_id ? "selected" : ""} key={sample.sample_id} onClick={() => chooseSample(sample)}><img src={assetUrl(sample.image_url)} alt={sample.label} /><span>{sample.label}</span></button>)}</div>
          <button className="primary wide" disabled={busy || (!file && !selected)} onClick={run}>{busy ? "Analyzing image…" : "Run classification"}<span>→</span></button>
        </article>
        <article className="panel prediction-panel">
          <p className="eyebrow">Model output</p><h2>Prediction</h2>
          {!prediction ? <div className="empty-state"><div className="pulse-ring"><Icon name="scan" /></div><strong>No inference yet</strong><span>Run a sample to inspect calibrated probabilities and abstention.</span></div> : <PredictionResult prediction={prediction} />}
        </article>
      </div>
    </section>
  );
}

function PredictionResult({ prediction }: { prediction: Prediction }) {
  return <div className="result"><div className="result-head"><div><small>Primary class</small><h3>{prediction.class_name}</h3><span>{prediction.species}</span></div><div className={`confidence ${prediction.abstained ? "abstained" : ""}`}><strong>{pct(prediction.confidence)}</strong><small>{prediction.abstained ? "Abstained" : "Above threshold"}</small></div></div><div className="ranking">{prediction.top_k.map((item, index) => <div className="rank" key={item.class_id}><span>{String(index + 1).padStart(2, "0")}</span><div><div><b>{item.class_name}</b><small>{pct(item.probability)}</small></div><i style={{ width: `${item.probability * 100}%` }} /></div></div>)}</div><div className="request-meta"><span>Latency <b>{prediction.latency_ms} ms</b></span><span>Artifact <b>{prediction.model_version}</b></span><span>Input <b>{prediction.input.width} × {prediction.input.height}</b></span><span>Request <b>{prediction.request_id.slice(0, 8)}</b></span></div><div className="warning-note">{prediction.warnings[0]}</div></div>;
}

function Evaluation({ metrics }: { metrics: Metrics | null }) {
  return <section className="page"><header className="page-heading"><div><p className="eyebrow">Evaluation evidence</p><h1>Measure without overclaiming.</h1><p>Every displayed result names its data boundary and locked-test state.</p></div></header><EvidenceBanner />{!metrics ? <Loading /> : <><div className="metric-grid"><Metric label="Macro F1" value={pct(metrics.macro_f1)} note="Qualification validation" /><Metric label="Top-1" value={pct(metrics.accuracy_top_1)} note="37-class task" /><Metric label="Top-5" value={pct(metrics.accuracy_top_5)} note="Ranking coverage" /><Metric label="Calibration error" value={metrics.expected_calibration_error.toFixed(3)} note="Lower is better" /></div><div className="two-column visual-evidence"><article className="panel"><p className="eyebrow">Confusion structure</p><h2>37 × 37 matrix</h2><img src={assetUrl("/reports/confusion_matrix.png")} alt="Qualification confusion matrix" /></article><article className="panel"><p className="eyebrow">Probability quality</p><h2>Reliability diagram</h2><img src={assetUrl("/reports/reliability_diagram.png")} alt="Qualification reliability diagram" /></article></div></>}</section>;
}

function Errors({ gallery }: { gallery: ErrorGallery | null }) {
  return <section className="page"><header className="page-heading"><div><p className="eyebrow">Failure analysis</p><h1>Study the weak decisions.</h1><p>Misclassifications and lowest-confidence correct cases remain visible.</p></div></header><EvidenceBanner />{!gallery ? <Loading /> : <div className="error-gallery">{gallery.items.map(item => <article className="error-item" key={item.sample_id}><img src={assetUrl(item.image_url)} alt={`Actual ${item.truth}`} /><div><span className={item.correct ? "correct" : "incorrect"}>{item.correct ? "Low confidence" : "Mismatch"}</span><h3>{item.prediction}</h3><p>Actual: {item.truth}</p><small>{pct(item.confidence)} confidence</small></div></article>)}</div>}</section>;
}

function Models({ comparison }: { comparison: ModelComparison | null }) {
  return <section className="page"><header className="page-heading"><div><p className="eyebrow">Candidate registry</p><h1>Separate code from evidence.</h1><p>Implemented candidates are not presented as evaluated models.</p></div></header>{!comparison ? <Loading /> : <><div className="model-summary"><span>Selected qualification model</span><strong>{comparison.selected_model}</strong><p>{comparison.warning}</p></div><div className="model-table"><div className="model-row header"><span>Candidate</span><span>Family</span><span>Status</span><span>Macro F1</span></div>{comparison.models.map(model => <div className="model-row" key={String(model.model_id)}><strong>{String(model.model_id)}</strong><span>{String(model.family).replaceAll("_", " ")}</span><span className={`model-status ${String(model.status)}`}>{String(model.status).replaceAll("_", " ")}</span><span>{typeof model.macro_f1 === "number" ? pct(model.macro_f1) : "Not reported"}</span></div>)}</div></>}</section>;
}

function Responsible() {
  return <section className="page"><header className="page-heading"><div><p className="eyebrow">Responsible use</p><h1>Confidence is not certainty.</h1><p>This interface is designed to expose limitations before it invites a decision.</p></div></header><div className="responsibility-grid">{[["01", "Demonstration scope", "The active artifact was trained on procedural qualification imagery. It validates engineering, not real-world breed recognition."],["02", "Abstention first", "Predictions below the configured confidence threshold are explicitly withheld instead of being forced into a confident label."],["03", "No sensitive use", "Do not use this system for veterinary care, identity, safety, ownership disputes or consequential decisions."],["04", "Dataset protocol", "Oxford-IIIT Pet trainval and test boundaries are represented in configuration, but official benchmark evidence is not claimed."],["05", "Explainability boundary", "Grad-CAM belongs to CNN and ResNet candidates. The active HOG-linear bundle does not fabricate a heatmap."],["06", "Reproducible evidence", "Artifacts carry versions, hashes, preprocessing signatures, environment metadata and an explicit evidence scope."]].map(([n, title, copy]) => <article className="panel principle" key={n}><span>{n}</span><h2>{title}</h2><p>{copy}</p></article>)}</div></section>;
}

export function App() {
  const [view, setView] = useState<View>("overview");
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [samples, setSamples] = useState<Sample[]>([]);
  const [gallery, setGallery] = useState<ErrorGallery | null>(null);
  const [comparison, setComparison] = useState<ModelComparison | null>(null);
  const [apiReady, setApiReady] = useState(false);
  const [globalError, setGlobalError] = useState("");

  useEffect(() => {
    Promise.all([
      getJson<{ status: string }>("/ready"),
      getJson<Metrics>("/v1/evaluation/summary"),
      getJson<{ items: Sample[] }>("/v1/samples"),
      getJson<ErrorGallery>("/v1/evaluation/errors"),
      getJson<ModelComparison>("/v1/evaluation/models")
    ]).then(([ready, metricData, sampleData, errorData, models]) => {
      setApiReady(ready.status === "ready"); setMetrics(metricData); setSamples(sampleData.items); setGallery(errorData); setComparison(models);
    }).catch(reason => setGlobalError(reason instanceof Error ? reason.message : "API unavailable"));
  }, []);

  const content = useMemo(() => {
    if (view === "overview") return <Overview metrics={metrics} onStart={() => setView("classify")} />;
    if (view === "classify") return <Classifier samples={samples} />;
    if (view === "evaluation") return <Evaluation metrics={metrics} />;
    if (view === "errors") return <Errors gallery={gallery} />;
    if (view === "models") return <Models comparison={comparison} />;
    return <Responsible />;
  }, [view, metrics, samples, gallery, comparison]);

  return <div className="app-shell"><aside><div className="brand"><div className="brand-mark"><Icon name="scan" /></div><div><strong>Vision Ledger</strong><span>Pet intelligence</span></div></div><p className="nav-label">Workspace</p><nav>{navigation.map(item => <button key={item.id} className={view === item.id ? "active" : ""} onClick={() => setView(item.id)}><Icon name={item.icon} /><span>{item.label}</span></button>)}</nav><div className="sidebar-status"><span className={apiReady ? "signal" : "signal offline"} /><div><strong>{apiReady ? "Workspace ready" : "Setup required"}</strong><small>HOG qualification · v1</small></div></div></aside><main><header className="topbar"><div><small>AI Engineer · Project 19</small><strong>{navigation.find(item => item.id === view)?.label}</strong></div><div className="top-status"><span className={apiReady ? "signal" : "signal offline"} />{apiReady ? "Local engine" : "Engine offline"}</div></header>{globalError && <div className="global-error"><strong>Evidence service unavailable</strong><span>{globalError}</span></div>}{content}</main></div>;
}

function pct(value: number): string { return `${(value * 100).toFixed(1)}%`; }
