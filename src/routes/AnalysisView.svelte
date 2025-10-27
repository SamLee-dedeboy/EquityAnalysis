<script>
  import { slide } from 'svelte/transition';

  // Importing Store
  import { currentPolicy } from '../lib/stores/currentPolicy.js';

  // --- State Variables ---
  let activeTab = 'general_equity_assessment';
  let perspectiveIndex = 0;
  let perspectiveCardGroups = [];

  // --- Reactive Statements ---
  $: perspectives = $currentPolicy?.overall_analysis_by_perspective ?? []; // Binds perspectives to the analysis JSON
  $: currentPerspective = perspectives[perspectiveIndex] ?? null; // Sets currentPerspective with perspectiveIndex

  $: currentAnalysisSection = currentPerspective?.analyses?.[activeTab] ?? null; // Binds to perspective's dimension

  // Analysis Nav Constants
  const equitySections = [
    {
      key: 'recognitional_equity',
      label: 'RECOGNITIONAL EQUITY',
      color: 'var(--equity-color-recognitional)',
    },
    {
      key: 'procedural_equity',
      label: 'PROCEDURAL EQUITY',
      color: 'var(--equity-color-procedural)',
    },
    {
      key: 'structural_equity',
      label: 'STRUCTURAL EQUITY',
      color: 'var(--equity-color-structural)',
    },
    {
      key: 'distributional_equity',
      label: 'DISTRIBUTIONAL EQUITY',
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

      <!-- New Analysis Content -->
      <!-- Header 1 -->
      <!-- <div class="overview-header">
        <h2 class="overview-title">
          {$currentPolicy?.test_fields?.test_subject || 'Overview Description'}
        </h2>
        <div class="overview-actions">
          <button class="share-button">
            <img src="/share.svg" alt="Share Icon" class="share-button-icon" />
            Share
          </button>
          <button class="threedots-button">
            <span style="margin-bottom: .3rem;">...</span>
          </button>
        </div>
      </div> -->
      <!-- Header 2 -->
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
      <!-- Equity Tabs -->
      <div class="equity-summary">
        {#if perspectives.length}
          <div
            class="perspective-matrix"
            style={`--column-count: ${perspectives.length}; --row-count: ${equitySections.length};`}
          >
            <!-- Header row -->
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

            <!-- Content rows -->
            {#each equitySections as section, rowIdx}
              <!-- Row label -->
              <div class="matrix-cell matrix-row-label">
                <span
                  class="equity-label"
                  style={`border-bottom: 4px solid ${section.color}`}
                  >{section.label.replaceAll('EQUITY', '')}</span
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
      <!-- Overall Insights -->
      <div>
        <div
          class="section"
          in:slide
          aria-labelledby="overall-insights"
          style="background: white; margin-top: 1.5rem;"
        >
          <h2
            id="overall-insights"
            style="font-size:1.5rem; font-weight:800; margin:0 0 0.75rem 0; color:var(--primary-text);"
          >
            Overall Insights
          </h2>

          <div
            class="columns"
            style="display:grid; grid-template-columns:repeat(2, 1fr); gap:1.5rem; margin-top:1rem;"
          >
            <div
              class="box"
              aria-label="Positive insights"
              style="background-color: var(--primary-aview-accent);"
            >
              <strong
                style="display:block; font-size:1.05rem; margin-bottom:0.5rem;"
              >
                Positive Insights
              </strong>
              <p style="margin:0;">
                {$currentPolicy?.overall_summary_and_recommendations
                  ?.key_equity_strengths || '...'}
              </p>
            </div>

            <div
              class="box"
              aria-label="Negative insights"
              style="background-color: var(--primary-aview-accent);"
            >
              <strong
                style="display:block; font-size:1.05rem; margin-bottom:0.5rem;"
              >
                Key Equity Gaps
              </strong>
              <p style="margin:0;">
                {$currentPolicy?.overall_summary_and_recommendations
                  ?.key_equity_gaps || '...'}
              </p>
            </div>
          </div>
        </div>
        <!-- Recommendations -->
        <div
          class="section"
          in:slide
          aria-labelledby="recommendations"
          style="margin-top:1rem; background: white;"
        >
          <h2
            style="font-size:1.5rem; font-weight:800; margin:0 0 0.75rem 0; color:var(--primary-text);"
          >
            Recommendations
          </h2>

          <div style="margin-top:1rem;">
            <p>
              {$currentPolicy?.overall_summary_and_recommendations
                ?.recommendations || '...'}
            </p>
          </div>
        </div>
      </div>
      <!-- Divider -->
      <!-- <div class="styled-divider" role="separator" aria-label="Analysis divider">
        <div class="line" aria-hidden="true"></div>
        <div class="badge">
          {currentPerspective?.group_name ?? 'Perspective'} · AI-Selected Excerpts
        </div>
        <div class="line" aria-hidden="true"></div>
      </div> -->
      <!-- Sources -->
      <!-- {#if currentAnalysisSection?.sources?.length}
        <div class="sources">
          <strong>Sources:</strong>
          <ul>
        {#each currentAnalysisSection.sources.slice(0, 3) as source}
          <li>{@html source.data}</li>
        {/each}
          </ul>
          {#if currentAnalysisSection.sources.length > 3}
        <div style="margin-top:0.5rem; color:#666; font-size:0.95rem;">
          And {currentAnalysisSection.sources.length - 3} more...
        </div>
          {/if}
        </div>
      {/if} -->
      <!-- End of New Analysis Content -->
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
    /* --bg-policy-makers: rgba(59, 130, 246, 0.08);
    --bg-residents: rgba(246, 128, 59, 0.08);
    --bg--farmers: rgba(59, 246, 81, 0.08); */
    /* --bg-policy-makers: rgba(0, 0, 0, 0.02);
    --bg-residents: rgba(0, 0, 0, 0.02);
    --bg--farmers: rgba(0, 0, 0, 0.02); */
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

  /* --- Header 1 --- */
  .overview-header {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    padding: 1.25rem 2.75rem 1.65rem;
    border-radius: 16px;
  }
  .overview-title {
    margin: 0;
    font-size: 1.6rem;
    font-weight: 600;
    color: var(--primary-interactive);
    text-align: center;
  }
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

  /* --- Header 2 --- */
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

  /* --- Equity Tabs --- */
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

  /* Header cells */
  .matrix-header-empty {
    /* Empty top-left cell */
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

  /* Hover effects */
  .matrix-content-card,
  .matrix-row-label {
    transition:
      transform 160ms ease,
      box-shadow 160ms ease;
  }

  /* .matrix-content-card:hover, */
  /* .matrix-row-label:hover {
    transform: translateY(-6px);
  } */

  /* Responsive design */
  @media (max-width: 1100px) {
    .perspective-matrix {
      grid-template-columns: 240px repeat(var(--column-count), minmax(0, 1fr));
      column-gap: 1.25rem;
      row-gap: 1.25rem;
    }

    .matrix-content-card {
      min-height: 200px;
    }
  }

  @media (max-width: 768px) {
    .perspective-matrix {
      grid-template-columns: 1fr;
      grid-template-rows: repeat(
        calc(var(--row-count) * (var(--column-count) + 1)),
        minmax(0, auto)
      );
    }

    .matrix-header-empty,
    .matrix-header,
    .matrix-row-label {
      display: none;
    }

    .matrix-label-mobile {
      display: block;
    }

    .matrix-content-card {
      min-height: unset;
    }

    .stakeholder-card::before {
      content: '';
      position: absolute;
      inset: 0 0 auto 0;
      width: 100%;
      height: 4px;
    }
  }

  /* --- Overall Insights --- */
  /* --- Recommendations --- */

  /*--- Old AnalysisView --- */
  /* --- Header --- */

  .section {
    background-color: #eee;
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
  }
  .columns {
    flex-direction: column;
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    margin-top: 1rem;
  }

  /* Pos. & Neg. Sections */
  .box {
    flex: 1 1 45%;
    background-color: #fff;
    padding: 1rem;
    border-radius: 8px;
    box-shadow: 0 0 2px rgba(0, 0, 0, 0.1);
    min-height: 120px;
  }
  .box strong {
    display: block;
    margin-bottom: 0.4rem;
    font-size: 0.95rem;
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
</style>
