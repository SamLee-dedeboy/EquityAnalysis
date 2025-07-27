<script>
    // Local Modules
    import BackButton from "../lib/BackButton.svelte";
    import InfoTab from "../lib/InfoTab.svelte";

    // // (WIP) Temporarily import currentPolicy from PolicyGallery
    import { currentPolicy } from '../lib/stores/currentPolicy.js';
    // // currentPolicy Store Variable 
    import analysis from "../lib/data/structured.json";

    // Hardcoded data for testing
    // Automatically subscribe to store
    let general;
    $: matchedPolicy = analysis.find(
      (item) => item.document.filename === $currentPolicy?.document?.filename
    );
    $: general = matchedPolicy?.analysis_sections;

    // State Variables
    let activeTab = 'general_equity_assessment';
    const tabOptions = [
        { key: 'general_equity_assessment', label: 'Equity Assessment', image: 'public/eq-asmnt.png' },
        { key: 'vulnerable_groups', label: 'Vulnerable Groups', image: 'public/vgroups.png' },
        { key: 'impact_severity', label: 'Impact Severity', image: 'public/sev.png' },
        { key: 'mitigation_strategies', label: 'Mitigation Strategies', image: 'public/mstrats.png' }
    ];
    const equitySections = [
        { key: 'recognitional_equity', label: 'Recognitional', color: '#F4A3A3' },
        { key: 'procedural_equity', label: 'Procedural', color: '#3B88A6' },
        { key: 'structural_equity', label: 'Structural', color: '#2AA78D' },
        { key: 'distributional_equity', label: 'Distributional', color: '#F0B340' }
    ];

</script>

<style>
    /* Container for the main content */
    .container { max-width: 1080; margin: 0 auto; padding: 2rem 1rem; font-family: system-ui, sans-serif; }

    /* Header and Subtitle */
    .header { margin-top: -75px; text-align: center;}

    /* Tab Elements */
    .tab-bar { display: flex; gap: 1rem; margin-bottom: 2.5rem; justify-content: center; background: #EDEDED; border-radius: 14px; padding: 1.5rem 3rem; max-width: 1200px; box-sizing: border-box; margin-left: auto; margin-right: auto; overflow-x: auto; white-space: nowrap; }
    .tab {
      padding: 1.2rem 4.5rem;
      font-size: 1.35rem;
      border: 2.5px solid #ccc;
      border-radius: 12px;
      background: #5bcce8;
      cursor: pointer;
      min-width: 260px;
      min-height: 64px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: 600;
      transition: background 0.2s, color 0.2s;
      white-space: nowrap;
    }
    .tab.active {
      background: #0C395A;
      color: white;
      border-color: #0C395A;
    }

    /* Equity Tab, Cards */

    .section-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.5rem; overflow: hidden;}
    .section { background-color: #eee; padding: 2rem; border-radius: 12px; margin-bottom: 2rem; }
    .pill { padding: 0.4rem 0.8rem; font-weight: bold; font-size: 0.95rem; border-radius: 6px; color: #fff; margin-bottom: 0.5rem; display: inline-block; }
    .title { font-size: 1.25rem; font-weight: 600; margin-bottom: 0.5rem; }
    .columns { flex-direction: column; display: flex; flex-wrap: wrap; gap: 1.5rem; margin-top: 1rem; }
    /* Pos. & Neg. Sections */
    .box { flex: 1 1 45%; background-color: #fff; padding: 1rem; border-radius: 8px; box-shadow: 0 0 2px rgba(0,0,0,0.1); min-height: 120px; }
    .box strong { display: block; margin-bottom: 0.4rem; font-size: 0.95rem; }
    /* Conclusion text styling */
    .conclusion { margin-top: 1rem; font-style: italic; color: #444; }

    h1 { font-size: 1.75rem; font-weight: 700; margin-bottom: 0.75rem; }
    .summary { color: #444; font-size: 1rem; margin-bottom: 2rem; line-height: 1.6; }
</style>

<section>
  <BackButton destination="#/" />
  <InfoTab />

  <div class="container">

    <div class="header">
      <h1>
        <img src="public/sel-btn.png" alt="{$currentPolicy?.document?.title}" style="height: 1em; vertical-align: middle; margin-right: 0.5em;">
        {$currentPolicy?.document?.title}
        <!-- <img src="public/sel-btn.png" alt="{selectedPolicy?.document?.title}" style="height: 1em; vertical-align: middle; margin-right: 0.5em;">
        {selectedPolicy?.document?.title} -->
      </h1>
    </div>


    <!-- Tab Bar -->
    <div class="tab-bar">
        {#each tabOptions as t}
        <button
            type="button"
            class="tab {activeTab === t.key ? 'active' : ''}"
            on:click={() => activeTab = t.key}
            aria-pressed={activeTab === t.key}
        >
            <img src={t.image} alt={t.label} style="height: 1em; vertical-align: middle; margin-right: 0.5em;">
            {t.label}
        </button>
        {/each}
    </div>

    <!-- General Equity Assessment -->
    {#if activeTab === 'general_equity_assessment'}
      <p class="summary">{general[activeTab].summary}</p>
      <div class="section-grid">
        {#each equitySections as s}
            <div class="section">
            <div class="title">
                <span class="pill" style="background-color: {s.color}">{s.label}</span>
            </div>

            <div class="columns">
                <div class="box">
                <strong><img src="public/green-dot.png" alt="Positive Findings" style="height: 1em; vertical-align: middle; margin-right: 0.5em;"> Positive Findings</strong>
                <p>{general[activeTab][s.key].positive_findings}</p>
                </div>
                <div class="box">
                <strong><img src="public/red-dot.png" alt="Areas of Concern" style="height: 1em; vertical-align: middle; margin-right: 0.5em;"> Areas of Concern</strong>
                <p>{general[activeTab][s.key].concerns}</p>
                </div>
            </div>

            <div class="conclusion">
                <strong>Conclusion:</strong> {general[activeTab][s.key].conclusion}
            </div>
            </div>
        {/each}
      </div>
      
    {:else}
      <p class="summary">{general[activeTab]}</p>
    {/if}

    <!-- Vulnerable Groups Formatting -->
    {#if activeTab === 'vulnerable_groups'}
      <p class="summary">{general.vulnerable_groups_analysis.summary}</p>

      <div class="section">
        <div class="title">
          <span class="pill" style="background-color: #0C395A">Vulnerable Groups Analysis</span>
        </div>

        <div class="columns">
          <div class="box">
            <strong>Identified Groups</strong>
            <p>{general.vulnerable_groups_analysis.identified_groups_and_impacts}</p>
          </div>
        </div>

        <div class="conclusion">
          <strong>Equity Assessment Summary:</strong> {general.vulnerable_groups_analysis.equity_assessment_summary}
        </div>

        <div class="conclusion" style="margin-top: 1rem;">
          <strong>Conclusion:</strong> {general.vulnerable_groups_analysis.conclusion}
        </div>
      </div>
    {/if}
    <!-- Impact Severity Formatting -->
    {#if activeTab === 'impact_severity'}
      <p class="summary">{general.severity_impact_analysis.summary}</p>

      <div class="section">
        <div class="title">
          <span class="pill" style="background-color: #0C395A">Severity of Impact Analysis</span>
        </div>

        <div class="columns">
          <div class="box">
            <strong>High Severity Impacts</strong>
            <p>{general.severity_impact_analysis.high_severity_impacts}</p>
          </div>
          <div class="box">
            <strong>Moderate Severity Impacts</strong>
            <p>{general.severity_impact_analysis.moderate_severity_impacts}</p>
          </div>
        </div>

        <div class="columns" style="margin-top: 1rem;">
          <div class="box" style="flex: 1 1 100%;">
            <strong>Equity Implications of Impacts</strong>
            <p>{general.severity_impact_analysis.equity_implications_of_impacts}</p>
          </div>
        </div>

        <div class="conclusion" style="margin-top: 1rem;">
          <strong>Conclusion:</strong> {general.severity_impact_analysis.conclusion}
        </div>
      </div>
    {/if}

    <!-- Mitigation Strategies Formatting -->
    {#if activeTab === 'mitigation_strategies'}
      <p class="summary">{general.mitigation_strategies_analysis.summary}</p>

      <div class="section">
        <div class="title">
          <span class="pill" style="background-color: #0C395A">Mitigation Strategies Analysis</span>
        </div>

        <div class="columns">
          <div class="box">
            <strong>Identified Strategies</strong>
            <p>{general.mitigation_strategies_analysis.identified_strategies}</p>
          </div>
        </div>

        <div class="conclusion">
          <strong>Equity Assessment Summary:</strong> {general.mitigation_strategies_analysis.equity_assessment}
        </div>

        <div class="conclusion" style="margin-top: 1rem;">
          <strong>Conclusion:</strong> {general.mitigation_strategies_analysis.conclusion}
        </div>
      </div>
    {/if}

  </div>

</section>