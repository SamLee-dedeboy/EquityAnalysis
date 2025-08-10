<script>
  // Local Modules
  import BackButton from "../lib/BackButton.svelte";
  import InfoTab from "../lib/InfoTab.svelte";
  import { slide, fade } from "svelte/transition";

  // import { equity_colors } from "../constants";
  // // (WIP) Temporarily import currentPolicy from PolicyGallery
  import { currentPolicy } from "../lib/stores/currentPolicy.js";
  // // currentPolicy Store Variable
  // import analysis from "../lib/data/structured.json";

  // Hardcoded data for testing
  // Automatically subscribe to store
  // let general;
  // $: matchedPolicy = analysis.find(
  //   (item) => item.document.filename === $currentPolicy?.document?.filename
  // );
  export const equity_colors = {
    Procedural: "#227C9D",
    Structural: "#17C3B2",
    Distributional: "#FFCB77",
    Recognitional: "#FEB3B1",
    Transformational: "#FE6D73",
  };
  const equitySections = [
    {
      key: "recognitional_equity",
      label: "Recognitional",
      color: equity_colors["Recognitional"],
    },
    {
      key: "procedural_equity",
      label: "Procedural",
      color: equity_colors["Procedural"],
    },
    {
      key: "structural_equity",
      label: "Structural",
      color: equity_colors["Structural"],
    },
    {
      key: "distributional_equity",
      label: "Distributional",
      color: equity_colors["Distributional"],
    },
  ];

  const tabOptions = [
    {
      key: "general_equity_assessment",
      label: "Equity Assessment",
      image: "chart.svg",
    },
    {
      key: "vulnerable_groups",
      label: "Vulnerable Groups",
      image: "user-group.svg",
    },
    {
      key: "impact_severity",
      label: "Impact Severity",
      image: "shield-x.svg",
    },
    {
      key: "mitigation_strategies",
      label: "Mitigation Strategies",
      image: "shield-plus.svg",
    },
  ];
  let activeTab = "general_equity_assessment";
  $: general = $currentPolicy["analysis_sections"];
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
      {$currentPolicy?.document?.title}
      <!-- <img src="public/sel-btn.png" alt="{selectedPolicy?.document?.title}" style="height: 1em; vertical-align: middle; margin-right: 0.5em;">
        {selectedPolicy?.document?.title} -->
    </div>

    <!-- Tab Bar -->
    <div class="tab-bar">
      {#each tabOptions as t}
        <button
          type="button"
          class="tab {activeTab === t.key ? 'active' : ''}"
          on:click={() => (activeTab = t.key)}
          aria-pressed={activeTab === t.key}
        >
          <img
            src={t.image}
            alt={t.label}
            style="height: 1.5rem; margin-right: 0.5rem;"
          />
          {t.label}
        </button>
      {/each}
    </div>
    <!-- General Equity Assessment -->
    {#if activeTab === "general_equity_assessment"}
      <div in:slide style="overflow: hidden;">
        <p class="summary">{general[activeTab].summary}</p>
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
                  <strong
                    ><img
                      src="public/green-dot.png"
                      alt="Positive Findings"
                      style="height: 1em; vertical-align: middle; margin-right: 0.5em;"
                    /> Positive Findings</strong
                  >
                  <p>
                    {general[activeTab][section.key].positive_findings}
                  </p>
                </div>
                <div class="box">
                  <strong
                    ><img
                      src="public/red-dot.png"
                      alt="Areas of Concern"
                      style="height: 1em; vertical-align: middle; margin-right: 0.5em;"
                    /> Areas of Concern</strong
                  >
                  <p>{general[activeTab][section.key].concerns}</p>
                </div>
              </div>

              <div class="conclusion">
                <strong>Conclusion:</strong>
                {general[activeTab][section.key].conclusion}
              </div>
            </div>
          {/each}
        </div>
      </div>
    {/if}

    <!-- Vulnerable Groups Formatting -->
    {#if activeTab === "vulnerable_groups"}
      <div in:slide style="overflow: hidden;">
        <p class="summary">{general.vulnerable_groups_analysis.summary}</p>

        <div class="section">
          <div class="title">
            <span
              class="pill"
              style="background-color: var(--primary-interactive)"
              >Vulnerable Groups Analysis</span
            >
          </div>

          <div class="columns">
            <div class="box">
              <strong>Identified Groups</strong>
              <p>
                {general.vulnerable_groups_analysis
                  .identified_groups_and_impacts}
              </p>
            </div>
          </div>

          <div class="conclusion">
            <strong>Equity Assessment Summary:</strong>
            {general.vulnerable_groups_analysis.equity_assessment_summary}
          </div>

          <div class="conclusion" style="margin-top: 1rem;">
            <strong>Conclusion:</strong>
            {general.vulnerable_groups_analysis.conclusion}
          </div>
        </div>
      </div>
    {/if}
    <!-- Impact Severity Formatting -->
    {#if activeTab === "impact_severity"}
      <div in:slide style="overflow: hidden;">
        <p class="summary">{general.severity_impact_analysis.summary}</p>

        <div class="section">
          <div class="title">
            <span
              class="pill"
              style="background-color: var(--primary-interactive)"
              >Severity of Impact Analysis</span
            >
          </div>

          <div class="columns">
            <div class="box">
              <strong>High Severity Impacts</strong>
              <p>{general.severity_impact_analysis.high_severity_impacts}</p>
            </div>
            <div class="box">
              <strong>Moderate Severity Impacts</strong>
              <p>
                {general.severity_impact_analysis.moderate_severity_impacts}
              </p>
            </div>
          </div>

          <div class="columns" style="margin-top: 1rem;">
            <div class="box" style="flex: 1 1 100%;">
              <strong>Equity Implications of Impacts</strong>
              <p>
                {general.severity_impact_analysis
                  .equity_implications_of_impacts}
              </p>
            </div>
          </div>

          <div class="conclusion" style="margin-top: 1rem;">
            <strong>Conclusion:</strong>
            {general.severity_impact_analysis.conclusion}
          </div>
        </div>
      </div>
    {/if}

    <!-- Mitigation Strategies Formatting -->
    {#if activeTab === "mitigation_strategies"}
      <div in:slide style="overflow: hidden;">
        <p class="summary">
          {general.mitigation_strategies_analysis.summary}
        </p>

        <div class="section">
          <div class="title">
            <span
              class="pill"
              style="background-color: var(--primary-interactive)"
              >Mitigation Strategies Analysis</span
            >
          </div>

          <div class="columns">
            <div class="box">
              <strong>Identified Strategies</strong>
              <p>
                {general.mitigation_strategies_analysis.identified_strategies}
              </p>
            </div>
          </div>

          <div class="conclusion">
            <strong>Equity Assessment Summary:</strong>
            {general.mitigation_strategies_analysis.equity_assessment}
          </div>

          <div class="conclusion" style="margin-top: 1rem;">
            <strong>Conclusion:</strong>
            {general.mitigation_strategies_analysis.conclusion}
          </div>
        </div>
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
</style>
