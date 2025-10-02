<script>
  import { onMount } from 'svelte';
  import { server_address } from '../constants.js';

  // Importing Local Modules
  import InfoTab from '../lib/InfoTab.svelte';
  import EquityModals from '../lib/pg-modals/EquityModals.svelte';
  import InfoModal from '../lib/pg-modals/InfoModal.svelte';
  import DocUpModal from '../lib/pg-modals/DocUpModal.svelte';

  // Importing Stores
  import {
    currentPolicy,
    fetchPolicies,
    fetchPolicyDataById,
  } from '../lib/stores/currentPolicy.js';

  // --- State Variables ---
  let selectedEquity = null;
  let showEquity = false; // Equity modal state

  let showInfo = false; // Info modal state
  let docUp = false; // Document upload modal state

  let policies = [];


  // --- Lifecycle Hook ---
  onMount(async () => {
    policies = await fetchPolicies();
  });

  // handleSelect function for updating policy store variable
  async function handleSelect(policy) {
    console.log('Setting currentPolicy with:', policy);
    const policyData = await fetchPolicyDataById(policy.id);
    currentPolicy.set(policyData);
    window.location.hash = '#/aview';
  }

  // Filters: Helper functions to check if a policy belongs to a specific tier
  function isFederal(policy) {
    return (
        policy.document.type === 'federal' ||
        policy.document.title.toLowerCase().includes('federal') ||
        policy.document.title.toLowerCase().includes('act')
    );
  }

  function isAgency(policy) {
    return (
      policy.document.type === 'agency' ||
      policy.document.title.toLowerCase().includes('regulation') ||
      policy.document.title.toLowerCase().includes('agency')
    );
  }

  function isState(policy) {
    const title = policy.document.title.toLowerCase();
    const dtype = (policy.document.type || '').toLowerCase();
    return (
      dtype === 'state' ||
      title.includes('state') ||
      title.includes('california')

    );
  }

  function isOther(policy) {
    return !isFederal(policy) && !isState(policy) && !isAgency(policy);
  }

  // Testing Helper Functions
  // function isFederal(policy) {
  //   return (policy.test_fields.test_scope || '').toLowerCase() === 'federal';
  // }

  // function isState(policy) {
  //   return (policy.test_fields.test_scope || '').toLowerCase() === 'state';
  // }

  // function isAgency(policy) {
  //   return (policy.test_fields.test_scope || '').toLowerCase() === 'agency';
  // }

</script>

<section>
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"
    rel="stylesheet"
  />

  <!-- Caption 1 -->
  <p class="caption-1">
    Explore our analysis on water policies. Each policy has been automatically
    evaluated using the
    <button
      class="quickef-btn"
      on:click={() => (window.location.hash = '#/info')}
    >
      Equity Framework <img
        src="box-arrow-top-right.svg"
        alt="Arrow"
        style="height: 1.2rem;"
      />
    </button>
    providing instant insights with dynamic visualizations
  </p>
  <!-- Caption 2 -->
  <h3 class="caption-2">
    <!-- Pre-Analyzed Documents -->
    <!-- <img
      src="landmark.svg"
      alt=""
      style="height: 0.9em; position: relative; top: 0.1em;"
    /> -->
    Understand the Five Equities
    <!-- Document Hierarchy Flow Chart -->
    <div class="eqbox-container">
      <button type="button" class="equity-box procedural" on:click={() => { selectedEquity = 'procedural'; showEquity = true; }} aria-label="Open Procedural Equity modal">
        <span class="equity-name">Procedural Equity</span>
      </button>
      <button type="button" class="equity-box structural" on:click={() => { selectedEquity = 'structural'; showEquity = true; }} aria-label="Open Structural Equity modal">
        <span class="equity-name">Structural Equity</span>
      </button>
      <button type="button" class="equity-box distributional" on:click={() => { selectedEquity = 'distributional'; showEquity = true; }} aria-label="Open Distributional Equity modal">
        <span class="equity-name">Distributional Equity</span>
      </button>
      <button type="button" class="equity-box recognitional" on:click={() => { selectedEquity = 'recognitional'; showEquity = true; }} aria-label="Open Recognitional Equity modal">
        <span class="equity-name">Recognitional Equity</span>
      </button>
      <button type="button" class="equity-box transformational" on:click={() => { selectedEquity = 'transformational'; showEquity = true; }} aria-label="Open Transformational Equity modal">
        <span class="equity-name">Transformational Equity</span>
      </button>
    </div>
  </h3>

  <!-- (1) Gantt-like Policy Gallery (Federal, State, Agency, Other) -->
  <div class="gallery">

    <!-- Row: Federal -->
    <div class="row federal">
      <div class="row-label federal">
        <span class="row-icon"><img src="landmark.svg" alt="Federal" /></span>
        Federal
        <span class="row-count">{policies.filter(isFederal).length}</span>
      </div>
      <div class="row-track">
        {#each policies.filter(isFederal) as policy}
          <div
            class="policy-card"
            role="button"
            tabindex="0"
            on:click={() => handleSelect(policy)}
            on:keydown={e => e.key === 'Enter' && handleSelect(policy)}
            title={policy.document.title}
          >
            <h5>{policy.document.title}</h5>
            <div class="tier-chip federal-chip">Federal</div>
          </div>
        {/each}
        {#if policies.filter(isFederal).length === 0}
          <div class="empty-section">No federal documents available</div>
        {/if}
      </div>
    </div>

    <!-- Row: State -->
    <div class="row state">
      <div class="row-label state">
        <span class="row-icon"><img src="landmark.svg" alt="State" /></span>
        State
        <span class="row-count">{policies.filter(isState).length}</span>
      </div>
      <div class="row-track">
        {#each policies.filter(isState) as policy}
          <div
            class="policy-card"
            role="button"
            tabindex="0"
            on:click={() => handleSelect(policy)}
            on:keydown={e => e.key === 'Enter' && handleSelect(policy)}
            title={policy.document.title}
          >
            <h5>{policy.document.title}</h5>
            <div class="tier-chip state-chip">State</div>
          </div>
        {/each}
        {#if policies.filter(isState).length === 0}
          <div class="empty-section">No state documents available</div>
        {/if}
      </div>
    </div>

    <!-- Row: Agency -->
    <div class="row agency">
      <div class="row-label agency">
        <span class="row-icon"><img src="landmark.svg" alt="Agency"/></span>
        Agency
        <span class="row-count">{policies.filter(isAgency).length}</span>
      </div>
      <div class="row-track">
        {#each policies.filter(isAgency) as policy}
          <div
            class="policy-card"
            role="button"
            tabindex="0"
            on:click={() => handleSelect(policy)}
            on:keydown={e => e.key === 'Enter' && handleSelect(policy)}
            title={policy.document.title}
          >
            <h5>{policy.document.title}</h5>
            <div class="tier-chip agency-chip">Agency</div>
          </div>
        {/each}
        {#if policies.filter(isAgency).length === 0}
          <div class="empty-section">No agency documents available</div>
        {/if}
      </div>
    </div>

    <!-- Row: Other -->
    <div class="row other">
      <div class="row-label other">
        <span class="row-icon"><img src="document.svg" alt="Other" /></span>
        Other
        <span class="row-count">{policies.filter(isOther).length}</span>
      </div>
      <div class="row-track">
        {#each policies.filter(isOther) as policy}
          <div
            class="policy-card"
            role="button"
            tabindex="0"
            on:click={() => handleSelect(policy)}
            on:keydown={e => e.key === 'Enter' && handleSelect(policy)}
            title={policy.document.title}
          >
            <h5>{policy.document.title}</h5>
            <div class="tier-chip other-chip">Other</div>
          </div>
        {/each}
        {#if policies.filter(isOther).length === 0}
          <div class="empty-section">No other documents available</div>
        {/if}
      </div>
    </div>

    <!-- Add Policy CTA aligned with lanes -->
    <div>
      <button
        class="add-policy-card"
        type="button"
        on:click={() => (docUp = true)}
        title="Add a new policy"
        aria-label="Add Policy"
        style="display: block; margin: 0 auto;"
      >
        <div class="add-icon">
          <img src="plus.svg" alt="Plus Icon" style="width: 2rem; height: 2rem;" />
        </div>
        <span class="add-text">Add New Policy</span>
        <p class="add-desc">Upload a document for equity analysis</p>
      </button>
    </div>
  </div>

  <!-- Tool Button -->
  <button
    class="tool-button"
    on:click={() => (window.location.hash = '#/tool')}
  >
    <img src="magic-wand.svg" alt="Tool Icon" style="height: 1rem;" />
    Equiflow AI
  </button>
  <!-- Info Tab -->
  <InfoTab />

  <!-- --- Modals!! --- -->
  <!-- i. CTA Modal, Info/Onboarding -->
  {#if showInfo}
    <InfoModal on:close={() => (showInfo = false)} />
  {/if}
  <!-- ii. Equity Definition Modals -->
  {#if showEquity}
    <EquityModals selectedEquity={selectedEquity} on:close={() => (showEquity = false)} />
  {/if}
  <!-- iii. Upload Modal, Document Loading for Tool -->
  {#if docUp}
    <DocUpModal on:close={() => (docUp = false)} />
  {/if}
</section>

<style>

  /* --- Captions --- */
  .caption-1 {
    font-family: 'Inter', sans-serif;
    font-size: 26px;
    text-align: center;
    margin-bottom: 2rem;
    max-width: 1100px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.8;
    color: var(--primary-text);
    border-radius: 8px;
  }
  .caption-2 {
    font-family: 'Inter', sans-serif;
    font-size: 1.5rem;
    font-weight: 500;
    color: var(--primary-text);
    text-align: center;
    margin-bottom: 1.2rem;
    letter-spacing: 0.02em;
    background-color: var(--primary-background);
    padding: 1rem 1rem;
  }

  /* Tool Button */
  .tool-button {
    position: absolute;
    top: 0.8rem;
    right: 1rem;
    background: var(--primary-interactive);
    background: 0.2s;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.5rem 1rem;
    font-size: 1.1em;
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    z-index: 10;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
  }
  .tool-button:hover {
    background: var(--primary-interactive-hover);
    color: white;
  }

  /* --- Info Screen CTA --- */
  .quickef-btn {
    background: var(--primary-interactive);
    border: none;
    color: white;
    font-weight: 300;
    font-size: 1em;
    padding: 0.2em 0.5em;
    border-radius: 6px;
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    font-style: italic;
  }
  .quickef-btn:hover {
    background: var(--primary-interactive-hover);
    color: white;
  }

  /* --- Equity Buttons --- */
  .eqbox-container {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0.5rem;
    margin: 1rem auto 1rem auto;
    padding: 1.5rem;
    max-width: 1200px;
    overflow-x: auto;
    font-family: 'Inter', sans-serif;
  }
  .equity-box {
    border-radius: 8px;
    padding: 1rem 1.5rem;
    text-align: center;
    width: 180px;
    height: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.25rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition:
      transform 0.2s ease,
      box-shadow 0.2s ease;
    margin-right: 1rem;
  }
  .equity-box.procedural {
    background: var(--equity-color-procedural);
  }
  .equity-box.structural {
    background: var(--equity-color-structural);
  }
  .equity-box.distributional {
    background: var(--equity-color-distributional);
  }
  .equity-box.recognitional {
    background: var(--equity-color-recognitional);
  }
  .equity-box.transformational {
    background: var(--equity-color-transformational);
  }
  .equity-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
  .equity-name {
    color: white;
    font-weight: 600;
    font-size: 0.9rem;
    line-height: 1.2;
  }
  
  @media (max-width: 768px) {
    .eqbox-container {
      flex-direction: column;
      gap: 1rem;
    }

    .equity-box {
      min-width: 200px;
      height: 70px;
    }
  }

  /* --- Gallery --- */
  .gallery {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    margin-top: 0.5rem;
  }

  .row {
    display: grid;
    grid-template-columns: 220px 1fr;
    align-items: stretch;
    gap: 0.75rem;
  }

  .row-label {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 700;
    border: 2px solid currentColor;
    border-radius: 10px;
    padding: 0.75rem 0.9rem;
    background: white;
    max-height: 100px;
  }

  .row-label .row-icon img {
    height: 1.2rem;
  }

  .row-count {
    margin-left: auto;
    font-size: 0.85rem;
    opacity: 0.8;
    background: rgba(0, 0, 0, 0.04);
    padding: 0.15rem 0.5rem;
    border-radius: 999px;
  }

  .row-track {
    position: relative;
    display: flex;
    gap: 0.5rem;
    align-items: center;
    padding: 0.5rem;
    border-radius: 10px;
    overflow-x: auto;
    background: var(--track-color);
    min-height: 60px;
    width: 1200px;
  }

  /* Lane-specific Stylings */
  .row.state {
    padding-left: 1.2rem; /* slight indent for state row */
  }
  .row.agency {
    padding-left: 2.4rem; /* larger indent for agency row */
  }
  .row.other {
    padding-left: 3.6rem; /* largest indent for other row */
  }


  .row-label.federal { color: var(--policy-federal); background: var(--policy-federal-light); }
  .row-label.agency { color: var(--policy-agency); background: var(--policy-agency-light); }
  .row-label.other { color: var(--policy-other); background: var(--policy-other-light); }
  .row-label.state { color: var(--policy-state); background: var(--policy-state-light); }

  @media (max-width: 768px) {
    .row { grid-template-columns: 160px 1fr; }
  }

  .empty-section {
    text-align: center;
    padding: 2rem;
    color: #6c757d;
    font-style: italic;
    border: 2px dashed #dee2e6;
    border-radius: 12px;
    background: #f8f9fa;
    min-width: 320px;
    max-width: 320px;
    flex-shrink: 0;
    min-height: 100px;
    max-height: 100px;
    display: flex;
    align-items: center;
    justify-content: center;
  }


  /* Policy Cards */

  .policy-card {
    padding: 0.7rem;
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    box-sizing: border-box;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;

    /* Fix to a 100px card height */
    height: 100px;
    min-height: 100px;
    max-height: 100px;

    width: clamp(240px, 30vw, 320px);
    flex-shrink: 0;

    display: flex;
    flex-direction: column;
    justify-content: space-between; /* ensures header, body and CTA distribute neatly */
    gap: 0.25rem;
    overflow: hidden;
    z-index: 2;
    word-break: break-word;
  }

  .policy-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    z-index: 10;
    border-color: var(--primary-interactive);
  }

  .policy-card h5 {
    text-align: left;
    font-size: 1rem;
    font-weight: 600;
    margin: 0 0 0.75rem 0;
    line-height: 1.3;
    color: var(--primary-text);

    box-sizing: border-box;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
  }

  /* Tier Chips */
  .tier-chip {
    display: inline-block;
    padding: 0.15rem 0.6rem; /* horizontal padding matches header */
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;

    margin-top: auto;
    text-align: center;
    width: fit-content;
    margin-left: 0.0rem;
    margin-right: 0.0rem;
    box-sizing: border-box;
  }

  .federal-chip {
    background: var(--policy-federal);
    color: white;
  }

  .agency-chip {
    background: var(--policy-agency);
    color: white;
  }

  .state-chip {
    background: var(--policy-state);
    color: white;
  }

  .other-chip {
    background: var(--policy-other);
    color: white;
  }

  /* View Analysis Button */
  /* .analysis-btn {
    background: var(--primary-interactive);
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    color: white;
  } */
  /* .analysis-btn:hover {
    background: var(--primary-interactive-hover);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  } */

  /* Add-Policy Card */
  .add-policy-card {
    background: linear-gradient(135deg, #f0f9ff 0%, #dbeafe 100%);
    border: 2px dashed var(--primary-interactive);
    border-radius: 12px;
    padding: 2rem;
    cursor: pointer;
    transition: all 0.2s ease;
    text-align: center;
    min-width: 300px;

  }

  .add-policy-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0, 123, 167, 0.15);
    background: linear-gradient(135deg, #e0f2fe 0%, #b3e5fc 100%);
  }

  .add-icon {
    width: 3rem;
    height: 3rem;
    border-radius: 50%;
    background: var(--primary-interactive);
    display: flex;
    align-items: center;
    justify-content: center;
    margin: 0 auto 1rem auto;
  }

  .add-text {
    display: block;
    font-size: 1.2rem;
    font-weight: 600;
    color: var(--primary-interactive);
    margin-bottom: 0.5rem;
  }

  .add-desc {
    font-size: 0.9rem;
    color: #6c757d;
    margin: 0;
  }
</style>
