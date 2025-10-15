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
      <div class="overview-header">
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
      </div>
      <!-- Header 2 -->
      <div class="header-container">
        <div class="header-bg">
          <div class="header-overlay"></div>
        </div>
        <div class="header-gradient"></div>

        <div class="header-content">
          <h1 class="header-title">
            {$currentPolicy?.test_fields?.test_title || 'Placeholder Title'}
          </h1>
          <div class="header-caption">
            {$currentPolicy?.test_fields?.test_short_caption || 'Placeholder Short Caption'}
          </div>
          <p class="header-description">
            {$currentPolicy?.test_fields?.test_long_caption || 'Placeholder Long Caption'}
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
            style={`--column-count:${perspectives.length}; --card-rows:${equitySections.length};`}
          >
            {#each perspectives as perspective, pIndex}
              <div class="matrix-heading">
                <h3 class="stakeholder-name">
                  {perspective.group_name || `Perspective ${pIndex + 1}`}
                </h3>
              </div>
            {/each}

            {#each equitySections as section}
              {#each perspectives as perspective}
                {@const axis = perspective.analyses?.[activeTab]?.[section.key]}
                <article class="stakeholder-card matrix-card">
                  <div class="stakeholder-card-header">
                    <span
                      class="stakeholder-card-accent"
                      style="background-color: {section.color};"
                      aria-hidden="true"
                    ></span>
                    <div class="stakeholder-card-category">
                      {section.label}
                    </div>
                  </div>
                  <h2 class="stakeholder-card-headline">
                    {axis?.caption || axis?.headline || '...'}
                  </h2>
                  <div class="stakeholder-card-description">
                    {axis?.findings ||
                    axis?.summary ||
                    axis?.description ||
                    axis?.conclusion ||
                    axis?.concerns ||
                    '...'}
                  </div>
                </article>
              {/each}
            {/each}
          </div>
        {/if}
      </div>
      <!-- Overall Insights -->
      <div>
        <div class="section" in:slide aria-labelledby="overall-insights" style="background: white; margin-top: 1.5rem;">
          <h2 id="overall-insights" style="font-size:1.5rem; font-weight:800; margin:0 0 0.75rem 0; color:var(--primary-text);">
            Overall Insights
          </h2>

          <div class="columns" style="display:grid; grid-template-columns:repeat(2, 1fr); gap:1.5rem; margin-top:1rem;">
            <div class="box" aria-label="Positive insights" style="background-color: var(--primary-aview-accent);">
              <strong style="display:block; font-size:1.05rem; margin-bottom:0.5rem;">
                Positive Insights
              </strong>
              <p style="margin:0;">
                {$currentPolicy?.overall_summary_and_recommendations?.key_equity_strengths || '...'}
              </p>
            </div>

            <div class="box" aria-label="Negative insights" style="background-color: var(--primary-aview-accent);">
              <strong style="display:block; font-size:1.05rem; margin-bottom:0.5rem;">
                Key Equity Gaps
              </strong>
              <p style="margin:0;">
                {$currentPolicy?.overall_summary_and_recommendations?.key_equity_gaps || '...'}
              </p>
            </div>
          </div>
        </div>
        <!-- Recommendations -->
        <div class="section" in:slide aria-labelledby="recommendations" style="margin-top:1rem; background: white;">
          <h2 style="font-size:1.5rem; font-weight:800; margin:0 0 0.75rem 0; color:var(--primary-text);">
            Recommendations
          </h2>

          <div style="margin-top:1rem;">
            <p>
              {$currentPolicy?.overall_summary_and_recommendations?.recommendations || '...'}
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

<style>
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
    right: 2rem;
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
    font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif;
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
    margin-top: 3rem;
  }
  .perspective-matrix {
    --column-count: 1;
    --card-rows: 1;
    display: grid;
    grid-template-columns: repeat(var(--column-count), minmax(0, 1fr));
    grid-template-rows: auto repeat(var(--card-rows), minmax(0, 1fr));
    column-gap: 1.5rem;
    row-gap: 1.5rem;
    align-items: stretch;
  }
  .matrix-heading {
    padding: 0.85rem 1rem;
    border-radius: 16px;
    background: linear-gradient(135deg, rgba(12, 57, 90, 0.08), rgba(12, 57, 90, 0.02));
    border: 1px solid rgba(15, 23, 42, 0.08);
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    min-height: 78px;
  }
  .stakeholder-name {
    margin: 0;
    font-size: 1.4rem;
    font-weight: 800;
    color: #0f172a;
    letter-spacing: -0.01em;
  }
  .stakeholder-card {
    position: relative;
    padding: 1.6rem;
    background: #ffffff;
    border-radius: 18px;
    border: 1px solid rgba(15, 23, 42, 0.12);
    box-shadow: 0 18px 32px rgba(15, 23, 42, 0.09);
    display: flex;
    flex-direction: column;
    gap: 0.9rem;
    min-height: 220px;
    height: 100%;
  }
  .matrix-card {
    display: flex;
    flex-direction: column;
    height: 100%;
  }
  .stakeholder-card-header {
    display: flex;
    align-items: center;
    gap: 0.6rem;
  }


  .stakeholder-card { overflow: visible; }
  .stakeholder-card-accent {
    width: 44px;
    height: 6px;
    border-radius: 999px;
    display: inline-block;
    flex: 0 0 auto;
    margin-right: 0.6rem;
    z-index: 1;
  }
  .stakeholder-card-category {
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #1f2937;
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
    font-size: 0.96rem;
    line-height: 1.6;
    flex: 1;
  }
  @media (max-width: 1100px) {
    .perspective-matrix {
      column-gap: 1.25rem;
      row-gap: 1.25rem;
    }
    .stakeholder-card {
      min-height: 200px;
    }
  }
  @media (max-width: 768px) {
    .perspective-matrix {
      grid-template-columns: 1fr;
      grid-template-rows: auto repeat(var(--card-rows), minmax(0, auto));
    }
    .stakeholder-card {
      min-height: unset;
    }
  }

  /* --- Overall Insights --- */
  /* --- Recommendations --- */

  /* --- Divider --- */
  .styled-divider {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin: 2rem 0;
    width: 100%;
    justify-content: center;
  }
  .styled-divider .line {
    flex: 1 1 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, rgba(0,0,0,0.12), transparent);
  }
  .styled-divider .badge {
    background: linear-gradient(135deg, rgba(12,57,90,0.95), rgba(25,118,210,0.95));
    color: #fff;
    padding: 0.35rem 0.85rem;
    border-radius: 999px;
    font-weight: 700;
    font-size: 0.95rem;
    box-shadow: 0 6px 18px rgba(12,57,90,0.18);
    white-space: nowrap;
    text-align: center;
    line-height: 1;
  }

  /* Sources */
  .sources {
    margin-top: 2rem;
    padding: 1.5rem;
    background: #f8fafc;
    border-radius: 12px;
    border-left: 4px solid var(--primary-interactive);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }
  .sources strong {
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--primary-interactive);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }
  .sources strong::before {
    content: '';
    width: 1.2rem;
    height: 1.2rem;
    background-image: url('/document.svg');
    background-size: contain;
    background-repeat: no-repeat;
    background-position: center;
    filter: var(--primary-interactive);
  }
  .sources ul {
    margin: 0;
    padding: 0;
    list-style: none;
  }
  .sources li {
    margin-bottom: 1rem;
    padding: 1rem;
    background: white;
    border-radius: 8px;
    border: 1px solid #e5e7eb;
    line-height: 1.6;
    position: relative;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    transition: all 0.2s ease;
  }
  .sources li:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    border-color: var(--primary-interactive);
  }

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
