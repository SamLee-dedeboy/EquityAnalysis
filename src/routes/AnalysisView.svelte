<script>
  import { slide } from 'svelte/transition';

  // Local Modules
  import InfoTab from '../lib/InfoTab.svelte';

  // Importing Store
  import { currentPolicy } from '../lib/stores/currentPolicy.js';

  // --- State Variables ---
  let activeTab = 'general_equity_assessment';
  let perspectiveIndex = 0;

  // --- Reactive Statements ---
  $: perspectives = $currentPolicy?.overall_analysis_by_perspective ?? []; // Binds perspectives to the analysis JSON
  $: currentPerspective = perspectives[perspectiveIndex] ?? null; // Sets currentPerspective with perspectiveIndex
  $: currentAnalysisSection = currentPerspective?.analyses?.[activeTab] ?? null; // Binds to perspective's dimension

  // Analysis Nav Constants
  const equitySections = [
    {
      key: 'recognitional_equity',
      label: 'Recognitional',
      color: 'var(--equity-color-recognitional)',
    },
    {
      key: 'procedural_equity',
      label: 'Procedural',
      color: 'var(--equity-color-procedural)',
    },
    {
      key: 'structural_equity',
      label: 'Structural',
      color: 'var(--equity-color-structural)',
    },
    {
      key: 'distributional_equity',
      label: 'Distributional',
      color: 'var(--equity-color-distributional)',
    },
  ];
  const tabOptions = [
    {
      key: 'general_equity_assessment',
      label: 'Equity Assessment',
      image: 'chart.svg',
    },
    {
      key: 'vulnerable_groups_analysis',
      label: 'Vulnerable Groups',
      image: 'user-group.svg',
    },
    {
      key: 'severity_impact_analysis',
      label: 'Impact Severity',
      image: 'shield-x.svg',
    },
    {
      key: 'mitigation_strategies_analysis',
      label: 'Mitigation Strategies',
      image: 'shield-plus.svg',
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
    <!-- (1) Header with Document Title -->
    <!-- <div class="header">
      <img
        src="document.svg"
        style="height: 1lh; margin-right: 0.2em; vertical-align: bottom;"
        alt="Document icon"
      />
      {$currentPolicy?.document?.title || 'No Document Selected'}
    </div> -->


     

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

      <!-- Test Content -->
      <!-- Header -->
      <div style="position:relative; width:100%; height:min(48vh, 340px); border-radius:8px; overflow:hidden; margin:0 0 0.75rem 0; box-shadow:0 8px 28px rgba(0,0,0,0.18);">
        <div
          aria-hidden="true"
          style="position:absolute; inset:0; width:100%; height:100%; background-image:url('head-image.png'); background-size:cover; background-position:center; background-repeat:no-repeat; display:block;"
        >
          <div style="position:absolute; inset:0; background: rgba(0,0,0,0.45);"></div>
        </div>
        <div aria-hidden="true" style="position:absolute; inset:0; background:linear-gradient(180deg, rgba(0,0,0,0.15) 0%, rgba(0,0,0,0.35) 35%, rgba(0,0,0,0.55) 100%);"></div>
        <div style="position:absolute; inset:0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:0.5rem; padding:1rem; text-align:center; color:#fff; font-family:'Inter', system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; text-shadow:0 2px 8px rgba(0,0,0,0.45);">
          <div
            style="background:rgba(12,57,90,0.85); color:#eaf5fb; padding:0.5rem 1rem; border-radius:9999px; font-weight:600; letter-spacing:0.2px; box-shadow:0 6px 20px rgba(12,57,90,0.35); backdrop-filter:saturate(140%) blur(2px);">
            Placeholder Subject
          </div>
          <h1 style="font-size:clamp(1.6rem, 4.2vw, 3rem); line-height:1.1; font-weight:800; margin:0.15rem 0 0;">
            Placeholder for Document Title 
          </h1>
          <div style="font-size:clamp(1rem, 2.2vw, 1.5rem); font-weight:600; opacity:0.95;">
            Placeholder for Caption
          </div>
          <p style="max-width:900px; margin:0.35rem auto 0.25rem auto; font-size:clamp(0.95rem, 1.7vw, 1.15rem); line-height:1.6; opacity:0.95;">
            This is a placeholder for a static caption that doesn't change with perspective. I want to implement general analysis fields and eliminate some of the pre-processing.
          </p>
          <div style="margin-top:0.5rem; font-size:clamp(1rem, 1.8vw, 1.25rem); font-weight:700;">
            Placeholder: 1972
          </div>
        </div>
      </div>
      <!-- Summary (Choose if dynamic or not) -->
      <div style="font-size:1.2rem; line-height:1.5; font-weight:100; color:var(--primary-text); margin:2.5rem 0;">
        {currentAnalysisSection.summary}
      </div>
      <!-- Perspective Tabs -->
      {#if perspectives.length > 1}
        <div class="perspective-nav-buttons">
          {#each perspectives as perspective, index}
            <button
              style="display:inline-flex; align-items:center; justify-content:center; padding:1.5rem 2rem; font-size:1rem; border:2px solid {perspectiveIndex === index ? 'var(--primary-interactive)' : '#e5e7eb'}; border-radius:12px; color:{perspectiveIndex === index ? 'white' : 'var(--primary-text)'}; background:{perspectiveIndex === index ? 'var(--primary-interactive)' : 'white'}; min-height:80px; font-weight:500; transition:all 0.2s ease; white-space:nowrap; cursor:pointer; box-shadow:0 2px 4px rgba(0,0,0,0.05); margin-right:0.75rem;"
              class:selected={perspectiveIndex === index}
              on:click={() => (perspectiveIndex = index)}
              aria-pressed={perspectiveIndex === index}
            >
              {perspective.group_name}
            </button>
          {/each}
        </div>
      {/if}
      <!-- Equity Tabs -->
      <div aria-hidden="true" style="display:grid; grid-template-columns:1fr; gap:1rem; align-items:stretch; margin-top: 3rem;">
        {#each equitySections as section}
          <div class="test-ptabs">
            <div>
              <div style="display:flex; gap:1rem; align-items:flex-start; margin-top:0.5rem;">
                <span class="test-pill" style="background-color: {section.color}">{section.label}</span>
                <div style="flex:1; min-width:0;">
                  <strong>Positive Findings</strong>
                  <p style="margin-top:0.5rem; word-break:break-word;">
                    {currentAnalysisSection[section.key]?.positive_findings}
                  </p>
                </div>
                <div style="flex:1; min-width:0;">
                  <strong>Areas of Concern</strong>
                  <p style="margin-top:0.5rem; word-break:break-word;">
                    {currentAnalysisSection[section.key]?.concerns}
                  </p>
                </div>
              </div>
            </div>

          </div>
        {/each}
      </div>
      <!-- Divider -->
      <div class="styled-divider" role="separator" aria-label="Analysis divider">
        <div class="line" aria-hidden="true"></div>
        <div class="badge">
          {currentPerspective?.group_name ?? 'Perspective'} · AI-Selected Excerpts
        </div>
        <div class="line" aria-hidden="true"></div>
      </div>
      <!-- Sources -->
      {#if currentAnalysisSection?.sources?.length}
        <div class="sources">
          <strong>Sources:</strong>
          <ul>
            {#each currentAnalysisSection.sources as source}
              <li>{@html source.data}</li>
            {/each}
          </ul>
        </div>
      {/if}







      <!-- (2) Perspective Carousel -->
      {#if perspectives.length > 1}
        <div class="perspective-nav">
          <button
            aria-label="Previous Perspective"
            on:click={() =>
              (perspectiveIndex =
                (perspectiveIndex - 1 + perspectives.length) %
                perspectives.length)}
          >
            <img src="/carousel-left.svg" alt="Previous Perspective" />
          </button>
          <span class="perspective-label">
            Perspective: {currentPerspective?.group_name}
          </span>
          <button
            aria-label="Next Perspective"
            on:click={() =>
              (perspectiveIndex = (perspectiveIndex + 1) % perspectives.length)}
          >
            <img src="/carousel-right.svg" alt="Next Perspective" />
          </button>
        </div>
      {:else}
        <div class="perspective-label" style="margin:1rem">
          Perspective: {currentPerspective?.group_name}
        </div>
      {/if}
      <!-- (3) Analysis Dimension Tabs -->
      <div class="tab-bar">
        {#each tabOptions as t}
          <button
            type="button"
            class="tab {activeTab === t.key ? 'active' : ''}"
            on:click={() => (activeTab = t.key)}
            aria-pressed={activeTab === t.key}
          >
            <img
              src={'/' + t.image}
              alt={t.label}
              style="height: 1.5rem; margin-right: 0.5rem;"
            />
            {t.label}
          </button>
        {/each}
      </div>
      <!-- (4) Analysis Content -->
      {#if currentAnalysisSection}
        {#if activeTab === 'general_equity_assessment'}
          <div in:slide style="overflow: hidden;">
            <p class="summary">{currentAnalysisSection.summary}</p>
            <div class="section-grid">
              {#each equitySections as section}
                <div class="section">
                  <div class="title">
                    <span class="pill" style="background-color: {section.color}"
                      >{section.label}</span
                    >
                  </div>

                  <div class="columns">
                    <div class="box">
                      <strong>
                        <img
                          src="green-dot.svg"
                          alt="Positive Findings"
                          style="height: 1em; vertical-align: middle; margin-right: 0.5em;"
                        />
                        Positive Findings
                      </strong>
                      <p>
                        {currentAnalysisSection[section.key]?.positive_findings}
                      </p>
                    </div>
                    <div class="box">
                      <strong>
                        <img
                          src="red-dot.svg"
                          alt="Areas of Concern"
                          style="height: 1em; vertical-align: middle; margin-right: 0.5em;"
                        />
                        Areas of Concern
                      </strong>
                      <p>{currentAnalysisSection[section.key]?.concerns}</p>
                    </div>
                  </div>

                  <div class="conclusion">
                    <strong>Conclusion:</strong>
                    {currentAnalysisSection[section.key]?.conclusion}
                  </div>
                </div>
              {/each}
            </div>
            {#if currentAnalysisSection?.sources?.length}
              <div class="sources">
                <strong>Sources:</strong>
                <ul>
                  {#each currentAnalysisSection.sources as source}
                    <li>{@html source.data}</li>
                  {/each}
                </ul>
              </div>
            {/if}
          </div>
          <!-- Vulnerable Groups Formatting -->
        {:else if activeTab === 'vulnerable_groups_analysis'}
          <div in:slide style="overflow: hidden;">
            <p class="summary">{currentAnalysisSection.summary}</p>

            <div class="section">
              <div class="title">
                <span
                  class="pill"
                  style="background-color: var(--primary-interactive)"
                >
                  Vulnerable Groups Analysis
                </span>
              </div>

              <div class="columns">
                <div class="box">
                  <strong>Identified Groups</strong>
                  <p>{currentAnalysisSection.identified_groups_and_impacts}</p>
                </div>
              </div>

              <div class="conclusion">
                <strong>Equity Assessment Summary:</strong>
                {currentAnalysisSection.equity_assessment_summary}
              </div>

              <div class="conclusion" style="margin-top: 1rem;">
                <strong>Conclusion:</strong>
                {currentAnalysisSection.conclusion}
              </div>
            </div>
            {#if currentAnalysisSection?.sources?.length}
              <div class="sources">
                <strong>Sources:</strong>
                <ul>
                  {#each currentAnalysisSection.sources as source}
                    <li>{@html source.data}</li>
                  {/each}
                </ul>
              </div>
            {/if}
          </div>
          <!-- Impact Severity Formatting -->
        {:else if activeTab === 'severity_impact_analysis'}
          <div in:slide style="overflow: hidden;">
            <p class="summary">{currentAnalysisSection.summary}</p>

            <div class="section">
              <div class="title">
                <span
                  class="pill"
                  style="background-color: var(--primary-interactive)"
                >
                  Severity of Impact Analysis
                </span>
              </div>

              <div class="columns">
                <div class="box">
                  <strong>High Severity Impacts</strong>
                  <p>{currentAnalysisSection.high_severity_impacts}</p>
                </div>
                <div class="box">
                  <strong>Moderate Severity Impacts</strong>
                  <p>{currentAnalysisSection.moderate_severity_impacts}</p>
                </div>
              </div>

              <div class="columns" style="margin-top: 1rem;">
                <div class="box" style="flex: 1 1 100%;">
                  <strong>Equity Implications of Impacts</strong>
                  <p>{currentAnalysisSection.equity_implications_of_impacts}</p>
                </div>
              </div>

              <div class="conclusion" style="margin-top: 1rem;">
                <strong>Conclusion:</strong>
                {currentAnalysisSection.conclusion}
              </div>
            </div>
            {#if currentAnalysisSection?.sources?.length}
              <div class="sources">
                <strong>Sources:</strong>
                <ul>
                  {#each currentAnalysisSection.sources as source}
                    <li>{@html source.data}</li>
                  {/each}
                </ul>
              </div>
            {/if}
          </div>
          <!-- Mitigation Strategies Formatting -->
        {:else if activeTab === 'mitigation_strategies_analysis'}
          <div in:slide style="overflow: hidden;">
            <p class="summary">
              {currentAnalysisSection.summary}
            </p>

            <div class="section">
              <div class="title">
                <span
                  class="pill"
                  style="background-color: var(--primary-interactive)"
                >
                  Mitigation Strategies Analysis
                </span>
              </div>
              <div class="columns">
                <div class="box">
                  <strong>Identified Strategies</strong>
                  <p>
                    {currentAnalysisSection.identified_strategies}
                  </p>
                </div>
              </div>
              <div class="conclusion">
                <strong>Equity Assessment Summary:</strong>
                {currentAnalysisSection.equity_assessment}
              </div>
              <div class="conclusion" style="margin-top: 1rem;">
                <strong>Conclusion:</strong>
                {currentAnalysisSection.conclusion}
              </div>
            </div>
            {#if currentAnalysisSection?.sources?.length}
              <div class="sources">
                <strong>Sources:</strong>
                <ul>
                  {#each currentAnalysisSection.sources as source}
                    <li>{@html source.data}</li>
                  {/each}
                </ul>
              </div>
            {/if}
          </div>
        {/if}
      {:else}
        <!-- Fallback if analysis data for the specific tab is missing, but policy and primary perspective are there -->
        <div class="header" style="color: var(--primary-interactive);">
          No detailed data available for the selected analysis tab.
        </div>
      {/if}
    {:else}
      <!--- Edge Case: Current Policy Exists but In Progress, currentPerspective = null -->
      <div class="header" style="color: #6c757d;">
        Awaiting analysis data...
      </div>
    {/if}
  </div>

  <!-- Info Tab -->
  <InfoTab />
</section>

<style>
  /* --- Test Classes --- */
  .test-ptabs {
    border-radius: 8px;
    padding: 1rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
    min-height: 80px;
  }
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
  .test-pill {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    width: 180px;       
    height: 80px;         /* fixed height for uniform size */
    margin-right: 2rem;
    padding: 0 0.8rem;
    font-weight: bold;
    font-size: 0.95rem;
    border-radius: 6px;
    color: #fff;
    box-sizing: border-box;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }


  /* --- Layout --- */
  .analysis-layout {
    max-width: 1400px;
    margin: 0.5rem auto;
    padding: 0rem 1rem;
    font-family: 'Inter', sans-serif;
  }

  /* --- (1) Header --- */
  .header {
    font-size: 1.7rem;
    font-weight: 700;
    margin: 0;
    text-align: center;
    color: var(--primary-text);
  }

  /* --- (2) Perspective Carousel --- */
  .perspective-nav {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 2rem;
    margin: 2rem 0;
    padding: 1.5rem 2rem;
    background: var(--primary-background);
    border-radius: 16px;
    box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
  }
  .perspective-label {
    font-size: 1.3rem;
    font-weight: 600;
    color: var(--primary-text);
    text-align: center;
    padding: 0 1rem;
    min-width: 200px;
    flex-shrink: 0;
  }
  .perspective-nav button {
    background: white;
    border: 2px solid #e5e7eb;
    padding: 0.75rem;
    border-radius: 12px;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    min-width: 44px;
    min-height: 44px;
    flex-shrink: 0;
  }
  .perspective-nav button:hover {
    border-color: var(--primary-interactive);
    background: var(--primary-interactive);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
  .perspective-nav button:hover img {
    filter: brightness(0) invert(1);
  }
  .perspective-nav button:focus {
    outline: 2px solid var(--primary-interactive);
    outline-offset: 2px;
  }
  .perspective-nav button:active {
    transform: translateY(0);
  }
  .perspective-nav img {
    height: 20px;
    width: 20px;
    transition: filter 0.2s ease;
    display: block;
  }

  /* --- (3) Analysis Dimension Tabs --- */
  .tab-bar {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
    padding: 2rem;
    background: #f8fafc;
    border-radius: 16px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }
  .tab {
    padding: 1.5rem 2rem;
    font-size: 1rem;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    color: var(--primary-text);
    background: white;
    min-height: 80px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 500;
    transition: all 0.2s ease;
    white-space: nowrap;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  }
  .tab:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    border-color: var(--primary-interactive);
  }
  .tab > img {
    filter: brightness(0.4);
    transition: filter 0.2s ease;
  }
  .tab.active {
    background: var(--primary-interactive);
    color: white;
    font-weight: 600;
    border-color: var(--primary-interactive);
    transform: translateY(-1px);
    box-shadow: 0 8px 24px rgba(12, 57, 90, 0.25);
  }
  .tab.active > img {
    filter: brightness(0) invert(1);
  }

  /* --- (4) Analysis Content --- */
  /* Grid, Analysis Sections */
  .section-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
    overflow: hidden;
  }
  .section {
    background-color: #eee;
    padding: 2rem;
    border-radius: 12px;
    margin-bottom: 2rem;
  }
  /* Chips for Analysis Sections */
  .pill {
    padding: 0.4rem 0.8rem;
    font-weight: bold;
    font-size: 0.95rem;
    border-radius: 6px;
    color: #fff;
    margin-bottom: 0.5rem;
    display: inline-block;
  }
  .title {
    font-size: 1.25rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
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
  /* Captions and Context */
  .summary {
    /* Misnomer. This is the caption text styling */
    color: var(--primary-text);
    font-size: 1rem;
    margin-bottom: 2rem;
    line-height: 1.6;
  }
  .conclusion {
    /* Conclusion and summmary at bottom of dimensions */
    color: var(--primary-text);
    margin-top: 1rem;
    font-style: italic;
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
