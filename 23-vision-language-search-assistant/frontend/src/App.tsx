import { useEffect, useMemo, useRef, useState, type FormEvent } from "react";
import { api } from "./api/client";
import type {
  CorpusItem,
  ErrorItem,
  EvaluationSummary,
  IndexBenchmark,
  IndexManifest,
  IndexMode,
  ModelBundle,
  SearchMode,
  SearchResponse,
  SearchResult,
  SearchState,
  SessionReply,
  View
} from "./api/types";
import { Icon } from "./components/Icon";
import { MetricCard } from "./components/MetricCard";

const suggestions = [
  "dog running on a beach",
  "people moving through a city at night",
  "food prepared indoors",
  "animals near blue water"
];

const navItems: { id: View; label: string; detail: string; icon: Parameters<typeof Icon>[0]["name"] }[] = [
  { id: "search", label: "Retrieval studio", detail: "Text and image search", icon: "search" },
  { id: "assistant", label: "Refinement room", detail: "Grounded sessions", icon: "spark" },
  { id: "benchmark", label: "Benchmark", detail: "Methods and indexes", icon: "chart" },
  { id: "errors", label: "Failure atlas", detail: "Adversarial queries", icon: "alert" },
  { id: "model", label: "System cards", detail: "Versions and limits", icon: "layers" }
];

function formatPercent(value: number) {
  return `${(value * 100).toFixed(value === 1 ? 0 : 1)}%`;
}

function ResultCard({ result, active, onSelect }: { result: SearchResult; active?: boolean; onSelect?: () => void }) {
  return (
    <article className={`result-card${active ? " active" : ""}`}>
      <button className="result-visual" onClick={onSelect} aria-label={`Select ${result.image_id}`}>
        <img src={result.image_url} alt={result.evidence_captions[0]?.text ?? result.image_id} />
        <span className="rank-badge">#{result.rank}</span>
        <span className="score-badge">{result.score.toFixed(3)}</span>
      </button>
      <div className="result-body">
        <div className="result-meta">
          <code>{result.image_id}</code>
          <span>{result.category}</span>
        </div>
        <p>{result.evidence_captions[0]?.text}</p>
        <div className="evidence-row">
          <span>S {result.score_breakdown.semantic.toFixed(2)}</span>
          <span>L {result.score_breakdown.lexical.toFixed(2)}</span>
          <span>H {result.score_breakdown.hybrid.toFixed(2)}</span>
        </div>
      </div>
    </article>
  );
}

function Segmented<T extends string>({ value, options, onChange, label }: { value: T; options: { value: T; label: string }[]; onChange: (value: T) => void; label: string }) {
  return (
    <div className="segmented" aria-label={label} role="group">
      {options.map((option) => (
        <button key={option.value} className={value === option.value ? "selected" : ""} onClick={() => onChange(option.value)} aria-pressed={value === option.value}>
          {option.label}
        </button>
      ))}
    </div>
  );
}

function SearchWorkspace({
  corpus,
  response,
  loading,
  query,
  setQuery,
  mode,
  setMode,
  indexMode,
  setIndexMode,
  alpha,
  setAlpha,
  category,
  setCategory,
  onSearch,
  onVisualSearch,
  onUpload,
  error
}: {
  corpus: CorpusItem[];
  response: SearchResponse | null;
  loading: boolean;
  query: string;
  setQuery: (value: string) => void;
  mode: SearchMode;
  setMode: (value: SearchMode) => void;
  indexMode: IndexMode;
  setIndexMode: (value: IndexMode) => void;
  alpha: number;
  setAlpha: (value: number) => void;
  category: string;
  setCategory: (value: string) => void;
  onSearch: () => void;
  onVisualSearch: (imageId: string) => void;
  onUpload: (file: File) => void;
  error: string;
}) {
  const [inputMode, setInputMode] = useState<"text" | "image">("text");
  const [selected, setSelected] = useState(corpus[0]?.image_id ?? "");
  const uploadRef = useRef<HTMLInputElement>(null);
  const categories = useMemo(() => ["all", ...new Set(corpus.map((item) => item.category))], [corpus]);
  const selectedItem = corpus.find((item) => item.image_id === selected);

  function submit(event: FormEvent) {
    event.preventDefault();
    if (inputMode === "text") onSearch();
    else if (selected) onVisualSearch(selected);
  }

  return (
    <div className="page search-page">
      <header className="page-heading search-heading">
        <div>
          <span className="kicker">Shared-space retrieval</span>
          <h1>Find the frame.<br /><em>Keep the evidence.</em></h1>
          <p>Search a sealed visual corpus with text or another image. Every result exposes its image ID, component scores and stored captions.</p>
        </div>
        <div className="orbital-mark" aria-hidden="true"><span /><span /><span /></div>
      </header>

      <section className="search-console panel">
        <div className="console-topline">
          <Segmented value={inputMode} onChange={setInputMode} label="Input source" options={[{ value: "text", label: "Text query" }, { value: "image", label: "Visual query" }]} />
          <div className="index-state"><span className="status-dot" /> {indexMode} index · {corpus.length} vectors</div>
        </div>
        <form onSubmit={submit}>
          {inputMode === "text" ? (
            <div className="search-field">
              <Icon name="search" />
              <label htmlFor="retrieval-query" className="sr-only">Describe an observable scene</label>
              <input id="retrieval-query" value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Describe an observable scene…" maxLength={320} />
              <span className="shortcut">⌘ K</span>
              <button className="primary-action" type="submit" disabled={loading || !query.trim()}>{loading ? "Ranking…" : "Search"}<Icon name="chevron" /></button>
            </div>
          ) : (
            <div className="visual-query-row">
              <div className="selected-visual">
                {selectedItem && <img src={selectedItem.image_url} alt={selectedItem.captions[0].text} />}
                <div><span>Query image</span><strong>{selectedItem?.image_id ?? "Select an image"}</strong></div>
              </div>
              <button className="secondary-action" type="button" onClick={() => uploadRef.current?.click()}><Icon name="upload" /> Upload image</button>
              <input ref={uploadRef} className="sr-only" type="file" accept="image/png,image/jpeg,image/webp" onChange={(event) => { const file = event.target.files?.[0]; if (file) onUpload(file); }} />
              <button className="primary-action" type="submit" disabled={loading || !selected}>Find similar<Icon name="chevron" /></button>
            </div>
          )}
        </form>
        {inputMode === "image" && (
          <div className="seed-strip" aria-label="Qualification images">
            {corpus.slice(0, 8).map((item) => <button key={item.image_id} onClick={() => setSelected(item.image_id)} className={selected === item.image_id ? "selected" : ""}><img src={item.image_url} alt=""/><span>{item.image_id}</span></button>)}
          </div>
        )}
        <div className="query-settings">
          <div><label>Retrieval method</label><Segmented value={mode} onChange={setMode} label="Retrieval method" options={[{ value: "bm25", label: "Caption" }, { value: "semantic", label: "Semantic" }, { value: "hybrid", label: "Hybrid" }]} /></div>
          <div><label>Index strategy</label><Segmented value={indexMode} onChange={setIndexMode} label="Index strategy" options={[{ value: "exact", label: "Exact" }, { value: "approximate", label: "Approx" }]} /></div>
          <div className="range-setting"><label htmlFor="alpha">Semantic weight <strong>{alpha.toFixed(2)}</strong></label><input id="alpha" type="range" min="0" max="1" step="0.05" value={alpha} onChange={(event) => setAlpha(Number(event.target.value))} disabled={mode !== "hybrid"} /></div>
          <div><label htmlFor="category">Category</label><select id="category" value={category} onChange={(event) => setCategory(event.target.value)}>{categories.map((item) => <option key={item} value={item}>{item}</option>)}</select></div>
        </div>
      </section>

      {error && <div className="error-banner" role="alert"><Icon name="alert"/><div><strong>Retrieval unavailable</strong><span>{error}</span></div></div>}

      <div className="suggestions"><span>Try an evaluated query</span>{suggestions.map((item) => <button key={item} onClick={() => { setQuery(item); setInputMode("text"); }}>{item}</button>)}</div>

      <section className="results-section" aria-live="polite">
        <div className="section-title">
          <div><span className="kicker">Ranked evidence</span><h2>{response ? `${response.results.length} traceable results` : "Start with a query"}</h2></div>
          {response && <div className="run-facts"><span>{response.latency_ms.toFixed(2)} ms</span><span>{response.mode}</span><span>{response.index_mode}</span></div>}
        </div>
        {response ? (
          <>
            <div className="result-grid">{response.results.map((result) => <ResultCard key={result.image_id} result={result} onSelect={() => onVisualSearch(result.image_id)} />)}</div>
            <div className="evidence-boundary"><Icon name="info"/><div><strong>Evidence boundary</strong><p>{response.evidence_boundary}</p>{response.upload_boundary && <p>{response.upload_boundary}</p>}</div></div>
          </>
        ) : <div className="empty-state"><Icon name="image"/><strong>No ranking yet</strong><span>Use text, a corpus image or a temporary upload.</span></div>}
      </section>
    </div>
  );
}

function AssistantWorkspace({ mode, indexMode, corpus }: { mode: SearchMode; indexMode: IndexMode; corpus: CorpusItem[] }) {
  const [state, setState] = useState<SearchState | null>(null);
  const [message, setMessage] = useState("animals near water");
  const [turns, setTurns] = useState<{ role: "user" | "assistant"; text: string; reply?: SessionReply }[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function ensureSession() {
    if (state) return state;
    const created = await api.createSession(mode, indexMode);
    setState(created);
    return created;
  }

  async function send(event?: FormEvent) {
    event?.preventDefault();
    if (!message.trim() || busy) return;
    const outgoing = message.trim();
    setMessage("");
    setTurns((current) => [...current, { role: "user", text: outgoing }]);
    setBusy(true);
    setError("");
    try {
      const session = await ensureSession();
      const reply = await api.sendMessage(session.session_id, outgoing);
      setState(reply.state);
      setTurns((current) => [...current, { role: "assistant", text: reply.answer, reply }]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The assistant request failed.");
    } finally {
      setBusy(false);
    }
  }

  async function reset() {
    if (!state) return;
    setBusy(true);
    try {
      const reply = await api.sendMessage(state.session_id, "reset");
      setState(reply.state);
      setTurns((current) => [...current, { role: "assistant", text: reply.answer, reply }]);
    } finally { setBusy(false); }
  }

  const latestSearch = [...turns].reverse().find((turn) => turn.reply?.search)?.reply?.search;
  return (
    <div className="page assistant-page">
      <header className="page-heading compact-heading">
        <div><span className="kicker">Stateful, not speculative</span><h1>Refine without losing<br/><em>the evidence trail.</em></h1><p>Each turn updates a typed SearchState. The response is rendered only from retrieved IDs, scores and captions.</p></div>
        <button className="secondary-action" onClick={reset} disabled={!state || busy}><Icon name="reset"/> Reset state</button>
      </header>
      <div className="assistant-layout">
        <section className="conversation-panel panel">
          <div className="conversation-header"><div><span className="status-dot"/><strong>{state ? "Session active" : "Ephemeral session"}</strong></div><code>{state?.session_id.slice(0, 8) ?? "not-created"}</code></div>
          <div className="messages" aria-live="polite">
            {turns.length === 0 && <div className="assistant-intro"><div className="assistant-symbol"><Icon name="spark"/></div><strong>Start with an observable request.</strong><p>Then try “exclude cat”, “only night”, “explain” or “reset”.</p></div>}
            {turns.map((turn, index) => <div key={`${turn.role}-${index}`} className={`message ${turn.role}`}><span>{turn.role === "user" ? "You" : "Lensline"}</span><p>{turn.text}</p>{turn.reply && <small>{turn.reply.reason_code} · {turn.reply.intent}</small>}</div>)}
            {busy && <div className="message assistant loading-message"><span>Lensline</span><p>Updating search state and ranking evidence…</p></div>}
          </div>
          {error && <div className="inline-error" role="alert">{error}</div>}
          <form className="message-composer" onSubmit={send}>
            <label htmlFor="assistant-message" className="sr-only">Search or refinement message</label>
            <input id="assistant-message" value={message} onChange={(event) => setMessage(event.target.value)} maxLength={320} placeholder="Search, refine, exclude or explain…" />
            <button type="submit" disabled={busy || !message.trim()} aria-label="Send message"><Icon name="send"/></button>
          </form>
        </section>
        <aside className="state-panel panel">
          <span className="kicker">Live SearchState</span>
          <h2>Visible constraints</h2>
          <dl><div><dt>Positive query</dt><dd>{state?.positive_query || "—"}</dd></div><div><dt>Model</dt><dd>{state?.model_version ?? "qualification-dual-encoder-v1"}</dd></div><div><dt>Index</dt><dd>{state?.index_mode ?? indexMode}</dd></div><div><dt>Top K</dt><dd>{state?.top_k ?? 6}</dd></div></dl>
          <div className="state-group"><label>Exclusions</label><div className="chip-row">{state?.negative_terms.length ? state.negative_terms.map((term) => <span className="chip negative" key={term}>{term}</span>) : <span className="empty-chip">None applied</span>}</div></div>
          <div className="state-group"><label>Previous evidence</label><div className="chip-row">{state?.previous_result_ids.length ? state.previous_result_ids.map((id) => <span className="chip" key={id}>{id}</span>) : <span className="empty-chip">No ranked IDs yet</span>}</div></div>
        </aside>
      </div>
      {latestSearch && <section className="assistant-results"><div className="section-title"><div><span className="kicker">Latest retrieval</span><h2>Cited visual evidence</h2></div></div><div className="result-grid compact">{latestSearch.results.slice(0, 4).map((result) => <ResultCard key={result.image_id} result={result} />)}</div></section>}
      {!latestSearch && corpus.length > 0 && <div className="micro-note"><Icon name="info"/> Sessions are local to this API process and expire automatically.</div>}
    </div>
  );
}

function BenchmarkWorkspace({ evaluation, index }: { evaluation: EvaluationSummary | null; index: IndexBenchmark | null }) {
  const methods: { key: SearchMode; label: string; color: string }[] = [{ key: "bm25", label: "Caption TF-IDF", color: "#f6b85f" }, { key: "semantic", label: "Semantic adapter", color: "#7c8cff" }, { key: "hybrid", label: "Hybrid retrieval", color: "#65e6d4" }];
  return <div className="page benchmark-page"><header className="page-heading compact-heading"><div><span className="kicker">Measured before marketed</span><h1>Compare the method.<br/><em>Inspect the trade-off.</em></h1><p>Qualification metrics are loaded from versioned reports generated by the same retrieval engine used by the API.</p></div></header>{evaluation && <><div className="metric-grid"><MetricCard eyebrow="Corpus" value={`${evaluation.images}`} detail={`${evaluation.captions} captions · ${evaluation.queries} queries`} /><MetricCard eyebrow="Hybrid R@1" value={formatPercent(evaluation.methods.hybrid.recall_at_1)} detail="sealed development queries" accent="#65e6d4"/><MetricCard eyebrow="Semantic MRR" value={evaluation.methods.semantic.mrr.toFixed(3)} detail="mean reciprocal rank" accent="#7c8cff"/><MetricCard eyebrow="Approx recall@5" value={formatPercent(index?.recall_at_5_vs_exact ?? 0)} detail="relative to exact" accent="#f6b85f"/></div><section className="method-table panel"><div className="table-heading"><div><span className="kicker">Retrieval leaderboard</span><h2>Components stay visible</h2></div><span className="qualification-badge">Qualification only</span></div><div className="method-rows"><div className="method-row header"><span>Method</span><span>R@1</span><span>R@5</span><span>MRR</span><span>Mean rank</span></div>{methods.map(({ key, label, color }) => { const metric = evaluation.methods[key]; return <div className="method-row" key={key}><span><i style={{ background: color }}/><strong>{label}</strong></span><span>{formatPercent(metric.recall_at_1)}</span><span>{formatPercent(metric.recall_at_5)}</span><span>{metric.mrr.toFixed(3)}</span><span>{metric.mean_rank.toFixed(2)}</span></div>; })}</div></section></>}{index && <section className="index-comparison"><div className="comparison-card"><span className="kicker">Exact reference</span><h3>{index.exact_index}</h3><strong>{index.exact_latency_ms_mean.toFixed(3)} ms</strong><p>Auditable matrix inner product over the full qualification corpus.</p></div><div className="comparison-link"><span>{formatPercent(index.recall_at_5_vs_exact)}</span><small>overlap @5</small></div><div className="comparison-card"><span className="kicker">Approximate proxy</span><h3>{index.approximate_index}</h3><strong>{index.approximate_latency_ms_mean.toFixed(3)} ms</strong><p>Quantized proxy used to validate the comparison contract before FAISS HNSW/IVF.</p></div></section>}<div className="evidence-boundary"><Icon name="info"/><div><strong>Benchmark boundary</strong><p>{evaluation?.claim_boundary ?? "Loading evaluation evidence…"} {index?.claim_boundary}</p></div></div></div>;
}

function ErrorWorkspace({ errors }: { errors: ErrorItem[] }) {
  return <div className="page errors-page"><header className="page-heading compact-heading"><div><span className="kicker">Adversarial evidence</span><h1>Failure is part of<br/><em>the model card.</em></h1><p>These queries are fixed before the demo. They expose constructs the qualification encoder cannot safely interpret.</p></div></header><div className="error-grid">{errors.map((item, index) => <article className="failure-card" key={item.query_id}><div className="failure-top"><span>0{index + 1}</span><code>{item.query_id}</code><span className="risk-tag">{item.risk}</span></div><blockquote>“{item.query}”</blockquote><div><label>Observed finding</label><p>{item.finding}</p></div><div><label>Mitigation</label><p>{item.mitigation}</p></div></article>)}</div><section className="principle-banner"><Icon name="alert"/><div><span className="kicker">Operating principle</span><h2>Similarity is a ranking signal—not semantic truth.</h2></div></section></div>;
}

function ModelWorkspace({ model, index }: { model: ModelBundle | null; index: IndexManifest | null }) {
  return <div className="page model-page"><header className="page-heading compact-heading"><div><span className="kicker">Compatible snapshots</span><h1>Know what produced<br/><em>every ranking.</em></h1><p>Model and index versions travel together. Readiness fails when dimensions, dtypes or snapshot identities diverge.</p></div></header>{model && index && <div className="card-stack"><section className="system-card hero-system-card"><div className="system-card-head"><div className="model-glyph"><Icon name="spark"/></div><div><span className="kicker">Online bundle</span><h2>{model.bundle_id}</h2></div><span className="ready-badge"><Icon name="check"/> {model.status}</span></div><p>{model.evidence_boundary}</p><div className="capability-list">{model.capabilities.map((item) => <span key={item}>{item}</span>)}</div></section><div className="two-column-cards"><section className="system-card"><span className="kicker">Model contract</span><h3>{model.model_version}</h3><dl><div><dt>Dataset</dt><dd>{model.dataset}</dd></div><div><dt>Dimension</dt><dd>{index.dimension}</dd></div><div><dt>dtype</dt><dd>{index.dtype}</dd></div><div><dt>Metric</dt><dd>{index.metric.replaceAll("_", " ")}</dd></div></dl></section><section className="system-card"><span className="kicker">Index contract</span><h3>{index.index_version}</h3><dl><div><dt>Model binding</dt><dd>{index.model_version}</dd></div><div><dt>Strategies</dt><dd>{index.available_indexes.join(" / ")}</dd></div><div><dt>Vectors</dt><dd>{index.item_ids.length}</dd></div><div><dt>Approximation</dt><dd>{index.approximate_is_proxy ? "qualification proxy" : "production index"}</dd></div></dl></section></div><section className="benchmark-statuses"><div><span>Flickr8k</span><strong>{model.official_benchmarks.flickr8k}</strong></div><div><span>OpenAI CLIP</span><strong>{model.official_benchmarks.clip}</strong></div><div><span>OpenCLIP</span><strong>{model.official_benchmarks.openclip}</strong></div></section></div>}</div>;
}

export default function App() {
  const [view, setView] = useState<View>("search");
  const [menuOpen, setMenuOpen] = useState(false);
  const [runtimeReady, setRuntimeReady] = useState(false);
  const [corpus, setCorpus] = useState<CorpusItem[]>([]);
  const [evaluation, setEvaluation] = useState<EvaluationSummary | null>(null);
  const [indexBenchmark, setIndexBenchmark] = useState<IndexBenchmark | null>(null);
  const [errors, setErrors] = useState<ErrorItem[]>([]);
  const [model, setModel] = useState<ModelBundle | null>(null);
  const [index, setIndex] = useState<IndexManifest | null>(null);
  const [query, setQuery] = useState("people near blue water");
  const [mode, setMode] = useState<SearchMode>("hybrid");
  const [indexMode, setIndexMode] = useState<IndexMode>("exact");
  const [alpha, setAlpha] = useState(0.68);
  const [category, setCategory] = useState("all");
  const [response, setResponse] = useState<SearchResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    Promise.all([api.ready(), api.corpus(), api.evaluation(), api.indexBenchmark(), api.errors(), api.model(), api.index()])
      .then(async ([ready, corpusItems, evalData, benchmark, errorItems, modelData, indexData]) => {
        if (!active) return;
        setRuntimeReady(ready.status === "ready");
        setCorpus(corpusItems);
        setEvaluation(evalData);
        setIndexBenchmark(benchmark);
        setErrors(errorItems);
        setModel(modelData);
        setIndex(indexData);
        const initial = await api.searchText({ query: "people near blue water", mode: "hybrid", index_mode: "exact", top_k: 6, alpha: 0.68 });
        if (active) setResponse(initial);
      })
      .catch((reason) => active && setError(reason instanceof Error ? reason.message : "The runtime could not be loaded."));
    return () => { active = false; };
  }, []);

  async function searchText() {
    setLoading(true); setError("");
    try { setResponse(await api.searchText({ query, mode, index_mode: indexMode, top_k: 6, alpha, category: category === "all" ? undefined : category })); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Search failed."); }
    finally { setLoading(false); }
  }

  async function searchImage(imageId: string) {
    setLoading(true); setError("");
    try { setResponse(await api.searchImage(imageId, indexMode)); setView("search"); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Visual search failed."); }
    finally { setLoading(false); }
  }

  async function uploadImage(file: File) {
    setLoading(true); setError("");
    try { setResponse(await api.uploadImage(file)); }
    catch (reason) { setError(reason instanceof Error ? reason.message : "Upload search failed."); }
    finally { setLoading(false); }
  }

  return (
    <div className="app-shell">
      <aside className={`sidebar${menuOpen ? " open" : ""}`}>
        <div className="brand"><div className="brand-mark"><span/><span/></div><div><strong>Lensline</strong><small>Retrieval studio</small></div></div>
        <button className="sidebar-close" onClick={() => setMenuOpen(false)} aria-label="Close navigation"><Icon name="close"/></button>
        <div className="nav-label">Workspace</div>
        <nav>{navItems.map((item) => <button key={item.id} className={view === item.id ? "active" : ""} onClick={() => { setView(item.id); setMenuOpen(false); }}><Icon name={item.icon}/><span><strong>{item.label}</strong><small>{item.detail}</small></span>{view === item.id && <i/>}</button>)}</nav>
        <div className="sidebar-footer"><div className="runtime-card"><span className={`status-dot${runtimeReady ? "" : " warning"}`}/><div><strong>{runtimeReady ? "Bundle ready" : "Connecting"}</strong><small>{model?.model_version ?? "qualification-v1"}</small></div></div><p>AI Engineer · Project 23</p></div>
      </aside>
      {menuOpen && <button className="mobile-overlay" onClick={() => setMenuOpen(false)} aria-label="Close navigation overlay" />}
      <main>
        <header className="topbar"><button className="menu-button" onClick={() => setMenuOpen(true)} aria-label="Open navigation"><Icon name="menu"/></button><div><span>AI Engineer · Plan 04</span><strong>{navItems.find((item) => item.id === view)?.label}</strong></div><div className="topbar-actions"><span className="environment-pill"><span className={`status-dot${runtimeReady ? "" : " warning"}`}/>{runtimeReady ? "Qualification online" : "Runtime unavailable"}</span><span className="version-pill">v1.0.0-rc.1</span></div></header>
        {view === "search" && <SearchWorkspace corpus={corpus} response={response} loading={loading} query={query} setQuery={setQuery} mode={mode} setMode={setMode} indexMode={indexMode} setIndexMode={setIndexMode} alpha={alpha} setAlpha={setAlpha} category={category} setCategory={setCategory} onSearch={searchText} onVisualSearch={searchImage} onUpload={uploadImage} error={error} />}
        {view === "assistant" && <AssistantWorkspace mode={mode} indexMode={indexMode} corpus={corpus} />}
        {view === "benchmark" && <BenchmarkWorkspace evaluation={evaluation} index={indexBenchmark} />}
        {view === "errors" && <ErrorWorkspace errors={errors} />}
        {view === "model" && <ModelWorkspace model={model} index={index} />}
      </main>
    </div>
  );
}

