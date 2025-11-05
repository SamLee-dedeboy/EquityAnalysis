<script>
  import { slide } from 'svelte/transition';

  // Importing Store
  import { currentPolicy } from '../lib/stores/currentPolicy.js';

  // --- Helpers ---
  const stripHtml = (html) => {
    if (!html) return '';

    return html
      .replace(/<br\s*\/?>/gi, ' ')
      .replace(/<\/p>/gi, ' ')
      .replace(/<[^>]+>/g, ' ')
      .replace(/&nbsp;/gi, ' ')
      .replace(/&amp;/gi, '&');
  };

  const collapseWhitespace = (text) =>
    text ? text.replace(/\s+/g, ' ').trim() : '';

  const prettifyFileLabel = (label) => {
    if (!label) return 'Source';
    const filename = label.split('/').pop().trim();
    const withoutId = filename.replace(/^[0-9a-f-]{32,}_/i, '');
    return withoutId.replace(/[_-]+/g, ' ').replace(/\s+/g, ' ').trim() || 'Source';
  };

  const looksEncodedPayload = (snippet) => {
    if (!snippet) return false;
    const condensed = snippet.replace(/\s+/g, '');
    if (condensed.length >= 40 && /^[0-9A-F]+$/i.test(condensed)) return true;
    const zeroPairs = condensed.match(/00/g);
    return Boolean(zeroPairs && zeroPairs.length > condensed.length / 4);
  };

  const formatSource = (rawHtml) => {
    const plain = collapseWhitespace(stripHtml(rawHtml));
    if (!plain) return null;

    const prefixMatch = plain.match(/^Source from\s+([^:]+):\s*(.*)$/i);
    const label = prefixMatch?.[1] ?? null;
    let snippet = prefixMatch?.[2]?.trim() ?? plain;

    const encoded = looksEncodedPayload(snippet);
    if (encoded) {
      snippet = 'Extract contains scanned or encoded text—refer to the source document for details.';
    }

    const maxLength = 260;
    const needsTruncation = snippet.length > maxLength;
    if (needsTruncation) {
      snippet = snippet.slice(0, maxLength).trimEnd().replace(/[,:;.-]+$/, '');
      snippet += '…';
    }

    return {
      title: prettifyFileLabel(label),
      snippet: snippet || 'See the linked document for the exact excerpt.',
      encoded,
      truncated: needsTruncation,
    };
  };

  // --- State Variables ---
  let activeTab = 'general_equity_assessment';
  let perspectiveIndex = 0;
  let perspectiveCardGroups = [];

  // --- Reactive Statements ---
  $: perspectives = $currentPolicy?.overall_analysis_by_perspective ?? []; // Binds perspectives to the analysis JSON
  $: currentPerspective = perspectives[perspectiveIndex] ?? null; // Sets currentPerspective with perspectiveIndex

  $: currentAnalysisSection = currentPerspective?.analyses?.[activeTab] ?? null; // Binds to perspective's dimension

  // Grouped Sources by Perspective for Sources 
  $: groupedSourcesByPerspective = perspectives
    .map((perspective) => {
      const analysis = perspective?.analyses?.[activeTab];
      const rawSources = analysis?.sources ?? [];

      if (!rawSources.length) return null;

      const formattedSources = rawSources
        .map((source) => formatSource(source?.data))
        .filter(Boolean);

      if (!formattedSources.length) return null;

      const total = rawSources.length;

      return {
        name: perspective?.group_name ?? 'Perspective',
        total,
        previewSources: formattedSources.slice(0, 3),
        remaining: Math.max(0, total - 3),
      };
    })
    .filter(Boolean);

  // Analysis Nav Constants
  const equitySections = [
    {
      key: 'recognitional_equity',
      label: 'RECOGNITIONAL',
      color: 'var(--equity-color-recognitional)',
    },
    {
      key: 'procedural_equity',
      label: 'PROCEDURAL',
      color: 'var(--equity-color-procedural)',
    },
    {
      key: 'structural_equity',
      label: 'STRUCTURAL',
      color: 'var(--equity-color-structural)',
    },
    {
      key: 'distributional_equity',
      label: 'DISTRIBUTIONAL',
      color: 'var(--equity-color-distributional)',
    },
  ];

  // Debugging Logs
  $: console.log('Current Policy Analysis Data:', $currentPolicy);
  $: console.log('Current Perspective Used:', currentPerspective?.group_name);
  $: console.log('Active analysis section:', activeTab, currentAnalysisSection);
</script>

<section>
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"
    rel="stylesheet"
  />
  <div class="analysis-layout">
    {#if !$currentPolicy}
      <!-- Initial State: No document selected or uploaded -->
      <div class="header" style="color: #6c757d;">
        Please select or upload a document to begin analysis.
      </div>
    {:else if $currentPolicy?.source === 'user' && ['pending', 'waiting_vs_processing', 'analysis_generating', 'vs_processing_pending'].includes($currentPolicy.analysis_status)}
      <!-- In Progress State: for user-uploaded documents -->
      <div class="header" style="color: var(--primary-interactive);">
        <div
          style="display: flex; align-items: center; justify-content: center; gap: 10px;"
        >
          <div class="spinner-small"></div>
          Analysis in progress: {$currentPolicy.analysis_status?.replace(
            /\_/g,
            ' '
          )}...
        </div>
        <p style="font-size: 0.8em; color: #888; margin-top: 10px;">
          This may take a few minutes.
        </p>
      </div>
    {:else if $currentPolicy?.source === 'user' && $currentPolicy.analysis_status === 'failed'}
      <!-- Failed State: for user-uploaded documents -->
      <div class="header" style="color: red;">
        Analysis Failed: {$currentPolicy?.analysis_error || 'Unknown error.'}
        <p style="font-size: 0.8em; color: #888; margin-top: 10px;">
          Please check the server logs for more details or try uploading another
          document.
        </p>
      </div>
    {:else if ($currentPolicy?.analysis_status === 'completed' || $currentPolicy?.source === 'preprocessed') && currentPerspective}
      <!-- Expected Case (Analysis Completed, Data Available)-->

      <!-- Header -->
      <div class="header-container">
        <div class="header-bg">
          <div class="header-overlay"></div>
        </div>
        <div class="header-gradient"></div>
        <div class="overview-actions">
          <button class="share-button">
            <img src="/share.svg" alt="Share Icon" class="share-button-icon" />
            Share
          </button>
          <button class="threedots-button">
            <span style="margin-bottom: .3rem;">...</span>
          </button>
        </div>
        <div class="header-content">
          <h1 class="header-title">
            {$currentPolicy?.test_fields?.test_title || 'Placeholder Title'}
          </h1>
          <div class="header-caption">
            {$currentPolicy?.test_fields?.test_short_caption ||
              'Placeholder Short Caption'}
          </div>
          <p class="header-description">
            {$currentPolicy?.test_fields?.test_long_caption ||
              'Placeholder Long Caption'}
          </p>
          <div class="header-date">
            {$currentPolicy?.test_fields?.test_date || '...'}
          </div>
        </div>
      </div>

      <!-- Equity Matrix -->
      <div class="equity-summary">
        {#if perspectives.length}
          <div
            class="perspective-matrix"
            style={`--column-count: ${perspectives.length}; --row-count: ${equitySections.length};`}
          >
            <!-- Header Column -->
            <div class="matrix-cell matrix-header">
              <h3>Equities</h3>
            </div>
            <!-- <div class="matrix-cell matrix-header-empty"></div> -->
            {#each perspectives as perspective}
              <div class="matrix-cell matrix-header">
                <h3 class="stakeholder-name">
                  {perspective.group_name}
                </h3>
              </div>
            {/each}

            <!-- Content Columns -->
            {#each equitySections as section, rowIdx}
              <!-- Row label -->
              <div class="matrix-cell matrix-row-label">
                <span
                  class="equity-label"
                  style={`border-bottom: 4px solid ${section.color}`}
                  >{section.label}</span
                >
              </div>

              <!-- Row cards -->
              {#each perspectives as perspective, colIdx}
                {@const axis = perspective.analyses?.[activeTab]?.[section.key]}
                <div
                  class="matrix-cell matrix-content-card"
                  data-row={rowIdx}
                  data-col={colIdx}
                >
                  <article class="stakeholder-card">
                    <div class="matrix-label-mobile">
                      <span>{section.label}</span>
                    </div>
                    <h2
                      class="stakeholder-card-headline"
                      style={`color: ${section.color}`}
                    >
                      {axis?.caption || '...'}
                    </h2>
                    <div class="stakeholder-card-description">
                      {axis?.findings || '...'}
                    </div>
                  </article>
                </div>
              {/each}
            {/each}
          </div>
        {/if}
      </div>
      
      <!-- Divider -->

      <!-- Sources -->
      {#if groupedSourcesByPerspective.length}
        <div class="styled-divider" role="separator" aria-label="Analysis divider">
          <div class="line" aria-hidden="true"></div>
            <div class="badge">
              AI-Selected References
            </div>
          <div class="line" aria-hidden="true"></div>
        </div>
        <section class="sources" aria-label="Analysis sources grouped by perspective">
          <div class="sources-heading">
            <strong>Sources by Perspective</strong>
            <span class="sources-subhead">Curated excerpts for each stakeholder group</span>
          </div>
          <div class="sources-groups">
            {#each groupedSourcesByPerspective as perspectiveSources}
              <article class="sources-card">
                <header class="sources-card-header">
                  <h3>{perspectiveSources.name}</h3>
                  <span class="sources-count">
                    {perspectiveSources.total} source{perspectiveSources.total === 1 ? '' : 's'}
                  </span>
                </header>
                <ul class="sources-list">
                  {#each perspectiveSources.previewSources as source}
                    <li class="source-item">
                      <div class="source-title">{source.title}</div>
                      <p class="source-snippet">{source.snippet}</p>
                    </li>
                  {/each}
                </ul>
                {#if perspectiveSources.remaining}
                  <div class="sources-more">
                    And {perspectiveSources.remaining} more source{perspectiveSources.remaining === 1 ? '' : 's'} in this perspective.
                  </div>
                {/if}
              </article>
            {/each}
          </div>
        </section>
      {/if}

      <div style="text-align: center; ">
        Analyses are generated by AI and may contain inaccuracies. Please verify important information with original sources.
      </div>

    {:else}
      <!--- Edge Case: Current Policy Exists but In Progress, currentPerspective = null -->
      <div class="header" style="color: #6c757d;">
        Awaiting analysis data...
      </div>
    {/if}
  </div>
</section>

<style lang="postcss">
  /* --- CSS Variables --- */
  :root {
    --bg-policy-makers: oklch(96.8% 0.007 247.896);
    --bg-residents: oklch(96.7% 0.003 264.542);
    --bg--farmers: oklch(96.7% 0.001 286.375);
  }

  /* --- Layout --- */
  .analysis-layout {
    max-width: 1400px;
    margin: 0.5rem auto;
    padding: 0rem 1rem;
    font-family: 'Inter', sans-serif;
  }
  .header {
    font-size: 1.7rem;
    font-weight: 700;
    margin: 0;
    text-align: center;
    color: var(--primary-text);
  }

  /* --- Header --- */
  .header-container {
    position: relative;
    width: 100%;
    height: min(48vh, 340px);
    border-radius: 8px;
    overflow: hidden;
    margin: 0 0 0.75rem 0;
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.18);
  }
  /* Background image + dark overlay */
  .header-bg {
    position: absolute;
    inset: 0;
    background-image: url('head-image.png');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
  }
  .header-overlay {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.45);
  }
  /* Gradient overlay */
  .header-gradient {
    position: absolute;
    inset: 0;
    background: linear-gradient(
      180deg,
      rgba(0, 0, 0, 0.15) 0%,
      rgba(0, 0, 0, 0.35) 35%,
      rgba(0, 0, 0, 0.55) 100%
    );
  }
  /* Text content */
  .header-content {
    position: absolute;
    inset: 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    padding: 1rem;
    text-align: center;
    color: #fff;
    font-family:
      'Inter',
      system-ui,
      -apple-system,
      Segoe UI,
      Roboto,
      Arial,
      sans-serif;
    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.45);
  }
  .header-title {
    font-size: clamp(1.6rem, 4.2vw, 3rem);
    line-height: 1.1;
    font-weight: 800;
    margin: 0.15rem 0 0;
  }
  .header-caption {
    font-size: clamp(1rem, 2.2vw, 1.5rem);
    font-weight: 600;
    opacity: 0.95;
  }
  .header-description {
    max-width: 900px;
    margin: 0.35rem auto 0.25rem auto;
    font-size: clamp(0.95rem, 1.7vw, 1.15rem);
    line-height: 1.6;
    opacity: 0.95;
  }
  .header-date {
    margin-top: 0.5rem;
    font-size: clamp(1rem, 1.8vw, 1.25rem);
    font-weight: 700;
  }

  /* --- Header Actions --- */
  .overview-actions {
    position: absolute;
    top: 2px;
    right: 3px;
    display: flex;
    align-items: center;
    gap: 0.75rem;
  }
  .share-button {
    background: #fff;
    color: var(--primary-text);
    border: 1px solid rgba(15, 23, 42, 0.06);
    padding: 0.5rem 0.75rem;
    border-radius: 8px;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
    cursor: pointer;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
    font-size: 1rem;
  }
  .share-button img.share-button-icon {
    height: 1rem;
    width: auto;
  }
  .threedots-button {
    background: #fff;
    font-size: 1rem;
    color: var(--primary-text);
    border: 1px solid rgba(15, 23, 42, 0.06);
    padding: 0.45rem 0.6rem;
    border-radius: 8px;
    font-weight: 700;
    cursor: pointer;
    min-width: 40px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  }

  /* --- Equity Matrix --- */
  .equity-summary {
    margin-top: 1rem;
  }

  .perspective-matrix {
    display: grid;
    grid-template-columns: 220px repeat(var(--column-count), minmax(0, 1fr));
    grid-template-rows: auto repeat(var(--row-count), minmax(180px, auto));
    --column-count: 1;
    --row-count: 1;
    column-gap: 1rem;
    align-items: stretch;

    position: relative;
  }

  .matrix-cell {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 78px;
  }

  .matrix-header {
    padding: 0.85rem 1rem;
    text-align: center;
    flex-direction: column;
  }

  .stakeholder-name {
    margin: 0;
    font-size: 1.4rem;
    font-weight: 800;
    color: #3c4352;
    /* color: #0f172a; */
    letter-spacing: -0.01em;
  }

  /* Row label cells */
  .matrix-row-label {
    padding: 2rem 1rem;
    font-size: 0.95rem;
    font-weight: 700;
    color: #0f172a;
    letter-spacing: 0.12em;
    min-height: 180px;
    display: flex;
    align-items: start;
  }

  .equity-label {
    /* max-width: 220px; */
    width: 100%;
    text-align: center;
    padding-bottom: 0.25rem;
  }

  /* Content cards */
  .matrix-content-card {
    padding: 0;
    align-items: stretch;
    min-height: 180px;
  }

  /* Second column styling */
  .matrix-content-card[data-col='0'] {
    background-color: var(--bg-policy-makers);
  }

  .matrix-content-card[data-col='0'] .stakeholder-card {
    background-color: transparent;
  }

  .matrix-content-card[data-col='0'] .stakeholder-card-headline {
    /* color: white; */
  }

  .matrix-content-card[data-col='0'] .stakeholder-card-description {
    /* color: rgba(255, 255, 255, 0.9); */
  }

  /* Third column styling */
  .matrix-content-card[data-col='1'] {
    background-color: var(--bg-residents);
  }

  .matrix-content-card[data-col='1'] .stakeholder-card {
    background-color: transparent;
  }

  /* Fourth column styling */
  .matrix-content-card[data-col='2'] {
    background-color: var(--bg--farmers);
  }

  .matrix-content-card[data-col='2'] .stakeholder-card {
    background-color: transparent;
  }

  /* Second column header styling */
  .matrix-header:nth-child(2) {
    background-color: var(--bg-policy-makers);
  }

  .matrix-header:nth-child(2) .stakeholder-name {
    /* color: white; */
  }

  /* Third column header styling */
  .matrix-header:nth-child(3) {
    background-color: var(--bg-residents);
  }

  /* Fourth column header styling */
  .matrix-header:nth-child(4) {
    background-color: var(--bg--farmers);
  }

  /* Blue background for the entire second column track */
  .perspective-matrix::before {
    content: '';
    position: absolute;
    top: 0;
    left: calc(220px + 1rem);
    width: calc(
      (100% - 220px - 1rem * (var(--column-count) + 1)) / var(--column-count)
    );
    height: 100%;
    /* background-color: var(--bg-policy-makers); */
    z-index: -1;
    pointer-events: none;
  }

  .stakeholder-card {
    position: relative;
    padding: 1.35rem;
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
    overflow: visible;
  }

  .matrix-label-mobile {
    display: none;
    margin-bottom: 0.75rem;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    color: rgba(15, 23, 42, 0.6);
  }

  .stakeholder-card-headline {
    margin: 0;
    font-size: 1.8rem;
    font-weight: 700;
    line-height: 1.25;
    color: #0f172a;
  }

  .stakeholder-card-description {
    margin: 0;
    color: #475467;
    font-size: 1.05rem;
    /* font-size: 0.96rem; */
    line-height: 1.6;
    flex: 1;
  }

  /* Spinner */
  .spinner-small {
    border: 2px solid rgba(0, 0, 0, 0.1);
    width: 20px;
    height: 20px;
    border-radius: 50%;
    border-left-color: var(
      --primary-interactive
    ); /* Use primary interactive color */
    animation: spin 1s ease infinite;
    flex-shrink: 0;
  }
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }

  /* --- Divider + Sources Section --- */
  .styled-divider {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.9rem;
    margin: 2.5rem 0 1.75rem;
    color: #ffffff;
  }

  .styled-divider .line {
    flex: 1 1 0%;
    height: 1px;
    background: linear-gradient(
      to right,
      rgba(15, 23, 42, 0),
      rgba(15, 23, 42, 0.12),
      rgba(15, 23, 42, 0)
    );
  }

  .styled-divider .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    padding: 0.45rem 1.4rem;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    border-radius: 999px;
    background: var(--primary-interactive);
    border: 1px solid rgba(15, 23, 42, 0.1);
    box-shadow: 0 10px 24px rgba(15, 23, 42, 0.08);
  }

  .sources {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.75rem;
    box-shadow: 0 18px 36px rgba(15, 23, 42, 0.08);
    border: 1px solid rgba(15, 23, 42, 0.06);
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    margin: 0 0 3rem 0;
  }

  .sources-heading {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    text-transform: uppercase;
    font-size: 0.85rem;
    letter-spacing: 0.16em;
    color: rgba(15, 23, 42, 0.75);
  }

  .sources-heading strong {
    font-size: 0.95rem;
    letter-spacing: 0.12em;
  }

  .sources-subhead {
    font-size: 0.82rem;
    text-transform: none;
    font-weight: 500;
    letter-spacing: 0.02em;
    color: #475467;
  }

  .sources-groups {
    display: grid;
    gap: 1.25rem;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  }

  .sources-card {
    background: rgba(248, 250, 252, 0.7);
    border: 1px solid rgba(15, 23, 42, 0.06);
    border-radius: 12px;
    padding: 1.1rem 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 0.85rem;
  }

  .sources-card-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    gap: 0.75rem;
    border-bottom: 1px solid rgba(15, 23, 42, 0.06);
    padding-bottom: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    font-size: 0.75rem;
  }

  .sources-card-header h3 {
    margin: 0;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.1em;
    color: #0f172a;
  }

  .sources-count {
    font-size: 0.7rem;
    font-weight: 600;
    color: rgba(15, 23, 42, 0.55);
  }

  .sources-list {
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    gap: 0.65rem;
    list-style: none;
  }

  .source-item {
    display: flex;
    flex-direction: column;
    gap: 0.35rem;
    border-left: 3px solid rgba(30, 38, 57, 0.08);
    padding-left: 0.75rem;
  }

  .source-title {
    font-size: 0.85rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: rgba(92, 106, 138, 0.7);
  }

  .source-snippet {
    margin: 0;
    color: #1f2937;
    font-size: 0.95rem;
    line-height: 1.55;
  }

  .sources-more {
    font-size: 0.85rem;
    color: #475467;
    margin-top: 0.15rem;
  }

  @media (max-width: 768px) {
    .styled-divider {
      margin: 2rem 0 1.2rem;
      gap: 0.6rem;
    }

    .styled-divider .badge {
      padding-inline: 1rem;
      letter-spacing: 0.1em;
    }

    .sources {
      padding: 1.3rem;
      gap: 1.1rem;
    }

    .sources-groups {
      grid-template-columns: 1fr;
      gap: 1rem;
    }

    .sources-card {
      padding: 1rem;
    }

    .source-item {
      padding-left: 0.6rem;
    }
  }
</style>
