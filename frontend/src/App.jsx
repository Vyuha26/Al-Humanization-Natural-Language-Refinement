import { useRef, useState } from 'react';
import { ArrowDown, ArrowRight, Check, ChevronDown, Clipboard, Feather, FileText, FileUp, LoaderCircle, Menu, RotateCcw, ShieldCheck, Sparkles, Upload, X } from 'lucide-react';
import { extractDocument, humanizeText } from './services/api';
import './App.css';

const contexts = ['General Writing', 'Professional Communication', 'Academic Writing', 'Reports and Summaries', 'Interview Questions', 'Candidate Communication', 'Business Documents'];
const tones = ['Natural', 'Professional', 'Conversational', 'Polished', 'Concise'];

const count = (s) => s.trim() ? s.trim().split(/\s+/).length : 0;

export default function App() {
  const [tab, setTab] = useState('write');
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const [context, setContext] = useState(contexts[0]);
  const [tone, setTone] = useState(tones[0]);
  const [minimal, setMinimal] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  const [notice, setNotice] = useState('');
  const [file, setFile] = useState(null);
  const [drag, setDrag] = useState(false);
  const [mobileMenu, setMobileMenu] = useState(false);

  const picker = useRef(null);

  async function run() {
    if (!input.trim()) {
      setError('Add some text before humanizing.');
      return;
    }
    setBusy(true);
    setError('');
    setNotice('');
    try {
      const data = await humanizeText({
        text: input,
        context,
        tone,
        minimal_rewrite: minimal
      });
      setOutput(data.humanized_text);
      setResult(data);
    } catch (e) {
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function selectFile(f) {
    if (!f) return;
    setError('');
    setNotice('');
    if (!/\.(pdf|docx|txt)$/i.test(f.name)) {
      setError('Choose a PDF, DOCX, or TXT file.');
      return;
    }
    if (f.size > 5 * 1024 * 1024) {
      setError('This file is over the 5 MB limit.');
      return;
    }
    setFile(f);
    setInput('');
    setOutput('');
    setResult(null);
    setBusy(true);
    try {
      const data = await extractDocument(f);
      setInput(data.extracted_text);
      if (data.warnings?.length) setNotice(data.warnings.join(' '));
    } catch (e) {
      setFile(null);
      setError(e.message);
    } finally {
      setBusy(false);
    }
  }

  async function copy() {
    try {
      await navigator.clipboard.writeText(output);
      setNotice('Copied to clipboard.');
    } catch {
      setError('Clipboard access was blocked. Select the text and copy it manually.');
    }
  }

  function download() {
    const blob = new Blob([output], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'humanized-text.txt';
    a.click();
    URL.revokeObjectURL(url);
  }

  function clear() {
    setInput('');
    setOutput('');
    setResult(null);
    setError('');
    setNotice('');
    setFile(null);
  }

  return (
    <div className="app">
      <header className="nav">
        <a className="brand" href="#home">
          <span className="brand-mark"><Feather size={20} /></span>
          <span>humanize<span className="brand-ai">ai</span></span>
        </a>

        <button className="mobile-toggle" aria-label="Toggle navigation" onClick={() => setMobileMenu(!mobileMenu)}>
          <Menu />
        </button>

        <nav className={mobileMenu ? 'nav-links open' : 'nav-links'}>
          <a href="#home">Home</a>
          <a href="#workspace">Humanize Text</a>
          <a href="#workspace" onClick={() => setTab('upload')}>Documents</a>
          <a href="#how">How It Works</a>
        </nav>

        <a className="nav-cta" href="#workspace">Try it free <ArrowRight size={16} /></a>
      </header>

      <main id="home">
        <section className="hero">
          <div className="hero-copy">
            <div className="eyebrow">
              <span className="eyebrow-dot" /> A thoughtful way to write
            </div>
            <h1>Make every word<br />feel more <em>human.</em></h1>
            <p>Refine robotic or awkward writing into clear, natural language. Your meaning, facts, and intent stay at the heart of every edit.</p>
            <div className="hero-actions">
              <a className="button primary" href="#workspace">Start humanizing <ArrowRight size={17} /></a>
              <a className="button secondary" href="#workspace" onClick={() => setTab('upload')}><Upload size={17} /> Upload a document</a>
            </div>
            <div className="hero-note"><ShieldCheck size={16} /> Your text stays yours. Review every change.</div>
          </div>
          <div className="hero-art" aria-hidden="true">
            <div className="art-orbit orbit-a" />
            <div className="art-orbit orbit-b" />
            <div className="art-card">
              <div className="art-card-top"><span>BEFORE</span><span className="art-dash" /></div>
              <div className="fake-lines"><i /><i /><i className="short" /></div>
              <div className="art-spark"><Sparkles size={17} /></div>
              <div className="art-card-top after"><span>AFTER</span><span className="art-check"><Check size={12} /></span></div>
              <div className="fake-lines warm"><i /><i /><i className="short" /></div>
            </div>
            <div className="art-flower flower-one">✳</div>
            <div className="art-flower flower-two">✿</div>
          </div>
        </section>

        <section className="workspace-section" id="workspace">
          <div className="section-heading">
            <div>
              <div className="eyebrow">YOUR WRITING STUDIO</div>
              <h2>A little more you, in every sentence.</h2>
            </div>
            <span className="secure-label"><ShieldCheck size={15} /> Private by design</span>
          </div>

          <div className="workspace-card">
            <div className="workspace-tabs">
              <button className={tab === 'write' ? 'active' : ''} onClick={() => setTab('write')}>
                <Feather size={16} /> Write or paste text
              </button>
              <button className={tab === 'upload' ? 'active' : ''} onClick={() => setTab('upload')}>
                <FileUp size={16} /> Upload document
              </button>
            </div>

            {tab === 'upload' && (
              <div
                className={'dropzone ' + (drag ? 'dragging' : '')}
                onDragOver={(e) => { e.preventDefault(); setDrag(true); }}
                onDragLeave={() => setDrag(false)}
                onDrop={(e) => {
                  e.preventDefault();
                  setDrag(false);
                  selectFile(e.dataTransfer.files[0]);
                }}
              >
                <input
                  ref={picker}
                  hidden
                  type="file"
                  accept=".pdf,.docx,.txt,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
                  onChange={(e) => selectFile(e.target.files[0])}
                />
                {file ? (
                  <div className="selected-file">
                    <span className="file-icon"><FileText /></span>
                    <div>
                      <b>{file.name}</b>
                      <small>{(file.size / 1024).toFixed(0)} KB · extracted preview below</small>
                    </div>
                    <button
                      aria-label="Remove document"
                      className="icon-btn"
                      disabled={busy}
                      onClick={() => {
                        setFile(null);
                        setInput('');
                        setOutput('');
                        setResult(null);
                        setNotice('');
                      }}
                    >
                      <X size={17} />
                    </button>
                  </div>
                ) : (
                  <>
                    <div className="upload-icon"><Upload size={20} /></div>
                    <b>Drop your document here</b>
                    <span>PDF, DOCX or TXT · up to 5 MB</span>
                    <button className="browse-btn" onClick={() => picker.current?.click()}>Browse files</button>
                  </>
                )}
              </div>
            )}

            <div className="editor-grid">
              <div className="editor-pane">
                <div className="pane-head">
                  <label htmlFor="source">{tab === 'upload' ? 'Extracted text preview' : 'Your original text'}</label>
                  <span>INPUT</span>
                </div>
                <textarea
                  id="source"
                  value={input}
                  maxLength={20000}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="Paste your writing here, or upload a document to get started…"
                />
                <div className="pane-foot">
                  <span>{count(input)} words · {input.length.toLocaleString()} / 20,000 characters</span>
                  {file && <span className="editable">Editable preview</span>}
                </div>
              </div>

              <div className="editor-pane output-pane">
                <div className="pane-head">
                  <label>Humanized version</label>
                  <span className="output-label"><Sparkles size={12} /> OUTPUT</span>
                </div>
                {busy && (
                  <div className="loading-state">
                    <LoaderCircle className="spin" size={22} />
                    <span>{tab === 'upload' && !input ? 'Reading your document…' : `Rewriting naturally with ${provider === 'gemini' ? 'Gemini' : 'AI'}…`}</span>
                  </div>
                )}
                <textarea
                  aria-label="Humanized output"
                  value={output}
                  readOnly
                  placeholder="Your refined writing will appear here…"
                />
                <div className="pane-foot">
                  <span>{count(output)} words · {output.length.toLocaleString()} characters</span>
                  {output && (
                    <div className="output-actions">
                      <button onClick={copy}><Clipboard size={14} /> Copy</button>
                      <button onClick={download}><ArrowDown size={14} /> Download</button>
                    </div>
                  )}
                </div>
              </div>
            </div>

            <div className="controls">
              <label className="select-control">
                <span>Writing context</span>
                <div>
                  <select value={context} onChange={(e) => setContext(e.target.value)}>
                    {contexts.map((x) => <option key={x}>{x}</option>)}
                  </select>
                  <ChevronDown size={15} />
                </div>
              </label>

              <label className="select-control">
                <span>Tone</span>
                <div>
                  <select value={tone} onChange={(e) => setTone(e.target.value)}>
                    {tones.map((x) => <option key={x}>{x}</option>)}
                  </select>
                  <ChevronDown size={15} />
                </div>
              </label>

              <label className="toggle-control">
                <input type="checkbox" checked={minimal} onChange={(e) => setMinimal(e.target.checked)} />
                <span className="toggle-ui" />
                <span>Minimal rewrite</span>
              </label>

              <div className="control-actions">
                <button className="clear-btn" onClick={clear} disabled={busy}><RotateCcw size={15} /> Clear</button>
                <button
                  className="button primary humanize-btn"
                  onClick={run}
                  disabled={busy || !input.trim()}
                >
                  {busy ? (
                    <><LoaderCircle className="spin" size={16} /> Humanizing…</>
                  ) : (
                    <><Sparkles size={16} /> Humanize text</>
                  )}
                </button>
              </div>
            </div>

            {(error || notice) && (
              <div role="status" className={error ? 'notice error' : 'notice'}>
                {error || notice}
              </div>
            )}

            {result && (
              <div className="validation">
                <div className="validation-title">
                  <ShieldCheck size={18} />
                  <div>
                    <b>Meaning & fact check</b>
                    <span>Automated review · please verify important content</span>
                  </div>
                </div>
                <div className="validation-statuses">
                  <Status label="Meaning preservation" data={result.meaning_validation} />
                  <Status label="Factual consistency" data={result.factuality_validation} />
                </div>
                <div className="entities">
                  <b>Details found in your original</b>
                  <div className="entity-list">
                    {Object.entries(result.extracted_entities || {}).flatMap(([k, v]) =>
                      v.map((x, i) => <span key={`${k}-${i}`}>{x}</span>)
                    )}
                    {!Object.values(result.extracted_entities || {}).some((v) => v.length) && (
                      <small>No names, dates, or numbers detected.</small>
                    )}
                  </div>
                </div>
                {result.warnings?.length > 0 && (
                  <div className="warnings">
                    {result.warnings.map((w, i) => <p key={i}>• {w}</p>)}
                  </div>
                )}
              </div>
            )}
          </div>
        </section>

        <section id="how" className="how">
          <div className="section-heading">
            <div>
              <div className="eyebrow">A SIMPLE, CAREFUL PROCESS</div>
              <h2>Writing, with room to breathe.</h2>
            </div>
            <p className="how-intro">You stay in control at every step. Nothing is changed until you choose to begin.</p>
          </div>
          <div className="steps">
            {[
              ['01', 'Bring your words', 'Paste text or upload a document. Review extracted content before it goes anywhere.'],
              ['02', 'Find your voice', 'Choose a context and tone, then let HumanizeAI improve clarity and flow.'],
              ['03', 'Review with care', 'Check the independent consistency review, then copy or download what feels right.']
            ].map(([n, t, d]) => (
              <article className="step" key={n}>
                <span className="step-number">{n}</span>
                <h3>{t}</h3>
                <p>{d}</p>
              </article>
            ))}
          </div>
        </section>
      </main>

      <footer>
        <a className="brand footer-brand" href="#home">
          <span className="brand-mark"><Feather size={18} /></span>
          <span>humanize<span className="brand-ai">ai</span></span>
        </a>
        <p>Clearer writing. Still yours.</p>
        <div className="footer-meta">
          <span>FastAPI · React · AI-Assisted</span>
        </div>
        <small>Privacy note: Text is processed securely and is not permanently saved by this app.</small>
      </footer>
    </div>
  );
}

function Status({ label, data }) {
  const status = data?.meaning_status || data?.factuality_status || 'Review recommended';
  const klass = status === 'Passed' ? 'passed' : status === 'Potential issue detected' ? 'issue' : 'review';
  return (
    <div className="status-item">
      <span>{label}</span>
      <b className={klass}>{status}</b>
      <small>{data?.meaning_explanation || data?.factuality_explanation || 'Please review.'}</small>
    </div>
  );
}

