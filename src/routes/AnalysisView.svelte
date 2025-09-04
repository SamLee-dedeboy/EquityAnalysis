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
    <!-- (1)Header with Document Title -->
    <div class="header">
      <img
        src="document.svg"
        style="height: 1lh; margin-right: 0.2em; vertical-align: bottom;"
        alt="Document icon"
      />
      {$currentPolicy?.document?.title || 'No Document Selected'}
    </div>
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
          </div>
        {/if}
        <!-- Sources section - available for all tabs -->
        {#if currentAnalysisSection?.sources?.length}
          <div class="sources">
            <strong>Sources & References</strong>
            <ul>
              {#each currentAnalysisSection.sources as source}
                <li>
                  <div class="source-header">
                    <span class="source-document">
                      📄 {$currentPolicy?.document?.title || 'Document Source'}
                    </span>
                  </div>
                  <div class="source-content">
                    {@html source.data.replace(/Source from [^:]+:\s*/, '')}
                  </div>
                </li>
              {/each}
            </ul>
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
    gap: 1rem;
    margin: 1rem 0;
  }
  .perspective-label {
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--primary-text);
    text-align: center;
  }
  .perspective-nav button {
    background: none;
    border: none;
    padding: 0.5rem;
    transition: filter 0.2s;
  }
  .perspective-nav button:hover {
    filter: brightness(0.8);
  }
  .perspective-nav img {
    height: 24px;
  }

  /* --- (3) Analysis Dimension Tabs --- */
  .tab-bar {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1rem;
    justify-content: center;
    /* background: #ededed; */
    border-radius: 14px;
    padding: 1.5rem 3rem;
  }
  .tab {
    max-width: 300px;
    padding: 1.2rem 2rem;
    font-size: 1rem;
    border: 2.5px solid #ccc;
    border-radius: 12px;
    color: var(--primary-text);
    min-height: 64px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 300;
    transition:
      background 0.2s,
      color 0.2s;
    white-space: nowrap;
    > img {
      filter: brightness(0.2);
    }
  }
  .tab.active {
    background: var(--primary-interactive);
    color: white;
    font-weight: 500;
    border-color: var(--primary-interactive);
    > img {
      filter: unset;
    }
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
    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
    border-radius: 12px;
    border: 1px solid #dee2e6;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
  }

  .sources > strong {
    display: flex;
    align-items: center;
    font-size: 1.1rem;
    font-weight: 600;
    color: var(--primary-text);
    margin-bottom: 1rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid var(--primary-interactive);
  }

  .sources > strong::before {
    content: '📚';
    margin-right: 0.5rem;
    font-size: 1.2rem;
  }

  .sources ul {
    margin: 0;
    padding: 0;
    list-style: none;
  }

  .sources li {
    margin-bottom: 1.5rem;
    background: white;
    border-radius: 8px;
    border-left: 4px solid var(--primary-interactive);
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    position: relative;
    line-height: 1.6;
    transition:
      transform 0.2s ease,
      box-shadow 0.2s ease;
    overflow: hidden;
  }

  .sources li:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }

  .sources li:last-child {
    margin-bottom: 0;
  }

  .source-header {
    background: linear-gradient(
      135deg,
      var(--primary-interactive) 0%,
      #0056b3 100%
    );
    color: white;
    padding: 0.75rem 1.25rem;
    font-weight: 600;
    font-size: 0.9rem;
    border-radius: 8px 8px 0 0;
    margin: 0;
    position: relative;
  }

  .source-header::after {
    content: 'EXCERPT';
    position: absolute;
    top: 0.75rem;
    right: 1.25rem;
    font-size: 0.7rem;
    opacity: 0.8;
    font-weight: 400;
    letter-spacing: 0.5px;
  }

  .source-document {
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }

  .source-content {
    padding: 1.25rem;
  }

  .sources blockquote {
    background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
    border: 2px solid #e9ecef;
    border-left: 4px solid var(--primary-interactive);
    border-radius: 6px;
    padding: 1.25rem;
    margin: 0;
    font-style: normal;
    font-family: 'Georgia', serif;
    font-size: 0.9rem;
    line-height: 1.6;
    color: #2c3e50;
    position: relative;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.05);
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
