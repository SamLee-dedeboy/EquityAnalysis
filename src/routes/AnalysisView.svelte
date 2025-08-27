<script>
  // Local Modules
  import InfoTab from '../lib/InfoTab.svelte';
  import { slide } from 'svelte/transition';

  // Import Store Variable
  import { currentPolicy } from '../lib/stores/currentPolicy.js';

  export const equity_colors = {
    Procedural: '#227C9D',
    Structural: '#17C3B2',
    Distributional: '#FFCB77',
    Recognitional: '#FEB3B1',
  };
  const equitySections = [
    {
      key: 'recognitional_equity',
      label: 'Recognitional',
      color: equity_colors['Recognitional'],
    },
    {
      key: 'procedural_equity',
      label: 'Procedural',
      color: equity_colors['Procedural'],
    },
    {
      key: 'structural_equity',
      label: 'Structural',
      color: equity_colors['Structural'],
    },
    {
      key: 'distributional_equity',
      label: 'Distributional',
      color: equity_colors['Distributional'],
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

  let activeTab = 'general_equity_assessment';

  let perspectiveIndex = 0;
  $: perspectives = $currentPolicy?.overall_analysis_by_perspective ?? [];
  $: currentPerspective = perspectives[perspectiveIndex] ?? null;
  $: currentAnalysisSection = currentPerspective?.analyses?.[activeTab] ?? null;

  $: console.log('Current Policy Analysis Data:', $currentPolicy);
  $: console.log('Current Perspective Used:', currentPerspective?.group_name);
  $: console.log('Active analysis section:', activeTab, currentAnalysisSection);
</script>

<section>
  <!-- <BackButton destination="#/" /> -->
  <InfoTab />

  <div class="container">
    <div class="header">
      <img
        src="document.svg"
        style="height: 1lh; margin-right: 0.2em; vertical-align: bottom;"
        alt=""
      />
      <!-- Display document title if available, otherwise a placeholder -->
      {$currentPolicy?.document?.title || 'No Document Selected'}
      <!-- <img src="public/sel-btn.png" alt="{selectedPolicy?.document?.title}" style="height: 1em; vertical-align: middle; margin-right: 0.5em;">
        {selectedPolicy?.document?.title} -->
    </div>

    {#if !$currentPolicy}
      <!-- Initial state: No document selected or uploaded. -->
      <div class="header" style="color: #6c757d;">
        Please select or upload a document to begin analysis.
      </div>
    {:else if $currentPolicy?.source === 'user' && ['pending', 'waiting_vs_processing', 'analysis_generating', 'vs_processing_pending'].includes($currentPolicy.analysis_status)}
      <!-- Analysis is in progress (for user-uploaded documents) -->
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
      <!-- Analysis failed (for user-uploaded documents) -->
      <div class="header" style="color: red;">
        Analysis Failed: {$currentPolicy?.analysis_error || 'Unknown error.'}
        <p style="font-size: 0.8em; color: #888; margin-top: 10px;">
          Please check the server logs for more details or try uploading another
          document.
        </p>
      </div>
    {:else if ($currentPolicy?.analysis_status === 'completed' || $currentPolicy?.source === 'preprocessed') && currentPerspective}
      <!-- Tab Bar -->
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
      <!-- Display content based on activeTab and the selected (first) perspective -->
      {#if currentAnalysisSection}
        <!-- General Equity Assessment -->
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
      {:else}
        <!-- Fallback if analysis data for the specific tab is missing, but policy and primary perspective are there -->
        <div class="header" style="color: var(--primary-interactive);">
          No detailed data available for the selected analysis tab.
        </div>
      {/if}
    {:else}
      <!-- Final fallback, if currentPolicy exists but isn't completed/failed yet, and currentPerspective is null -->
      <div class="header" style="color: #6c757d;">
        Awaiting analysis data...
      </div>
    {/if}
  </div>
</section>

<style>
  section {
    max-width: 1200px;
  }
  /* Container for the main content */
  .container {
    max-width: 1080;
    margin: 0.5rem auto;
    padding: 0rem 1rem;
    font-family: system-ui, sans-serif;
  }

  /* Header and Subtitle */
  .header {
    font-size: 1.7rem;
    font-weight: 700;
    margin: 0;
    text-align: center;
    color: var(--primary-text);
  }

  /* Tab Elements */
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
    cursor: pointer;
    padding: 0.5rem;
    transition: filter 0.2s;
  }
  .perspective-nav button:hover {
    filter: brightness(0.8);
  }
  .perspective-nav img {
    height: 24px;
  }
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
    cursor: pointer;
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

  /* Equity Tab, Cards */
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
  /* Conclusion text styling */
  .conclusion {
    margin-top: 1rem;
    font-style: italic;
    color: #444;
  }

  h1 {
    font-size: 1.75rem;
    font-weight: 700;
    margin-bottom: 0.75rem;
  }
  .summary {
    color: #444;
    font-size: 1rem;
    margin-bottom: 2rem;
    line-height: 1.6;
  }

  /* Spinner Small */
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
