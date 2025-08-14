<script>
  
  import { onMount } from "svelte";
  import { server_address } from "../constants.js";
  
  // Importing Local Module
  import InfoTab from "../lib/InfoTab.svelte";
  import InfoModal from "../lib/pg-modals/InfoModal.svelte";
  import DocUpModal from "../lib/pg-modals/DocUpModal.svelte";

  // Policies data
  import {
    currentPolicy,
    fetchPolicies,
    fetchPolicyDataById,
  } from "../lib/stores/currentPolicy.js";

  // State variables for modals
  let showInfo = false; // Info modal state
  let docUp = false; // Document upload state

  let modalElement;
  let policies = [];

  // ---- Equity Framework modal content state (for Info modal) ----
  const efItems = [
    { id: "procedural", label: "Procedural", def: "Fair and inclusive processes in policy development, implementation, and enforcement. Ensures all stakeholders have meaningful participation opportunities.", color: "var(--equity-color-procedural)" },
    { id: "structural", label: "Structural", def: "Addresses underlying systems and institutions that create inequities. Focuses on reforming organizational structures, legal frameworks, and policies that systematically advantage some groups.", color: "var(--equity-color-structural)" },
    { id: "distributional", label: "Distributional", def: "Fair allocation of benefits, burdens, and resources. Examines who gets what, when, and how in policy outcomes.", color: "var(--equity-color-distributional)" },
    { id: "recognitional", label: "Recognitional", def: "Recognition of historical, cultural, and social contexts that shape communities’ relationships with water resources and governance.", color: "var(--equity-color-recognitional)" },
    { id: "transformational", label: "Transformational", def: "Reimagines systems to center equity from the ground up, creating new approaches rather than marginal fixes.", color: "var(--equity-color-transformational)" }
  ];

  // multi‑expand: which rows are open
  let efOpen = new Set(); // e.g. Set([0, 2])
  function efToggle(i) {
    const next = new Set(efOpen);
    next.has(i) ? next.delete(i) : next.add(i);
    efOpen = next;
  }

  // Auto-focus modal when opened
  $: if (showInfo && modalElement) {
    modalElement.focus();
  }

  // State Variable from Store, Selection for Analysis Modal
  async function handleSelect(policy) {
    console.log("Setting currentPolicy with:", policy);
    const policyData = await fetchPolicyDataById(policy.id);
    currentPolicy.set(policyData);
    window.location.hash = "#/aview";
  }

  onMount(async () => {
    policies = await fetchPolicies();
  });

</script>

<section>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet"/>

  <!-- (0) Info Tab -->
  <InfoTab />

  <!-- (1) Tool Button -->
  <button
    class="tool-button"
    on:click={() => (window.location.hash = "#/tool")}
  >
    <img src="magic-wand.svg" alt="Tool Icon" style="height: 1rem;" />
    Equiflow AI
  </button>

  <!-- (2) Headers, Caption -->
  <!-- Caption 1 -->
  <p class="caption-1">
    Explore our analysis on water policies. Each policy has been automatically
    evaluated using the
    <button class="quickef-btn" on:click={() => (showInfo = true)}>
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
    <img
      src="landmark.svg"
      alt=""
      style="height: 0.9em; position: relative; top: 0.1em;"
    />
    Analysis Gallery
    <span
      style="display: inline-flex; align-items: center; gap: 0.25em; margin-left: -0.15em;"
    >
      <!-- <img
        src="line-arrow-down.svg"
        alt="Down Arrow"
        style="height: 0.9em; position: relative; top: 0.1em;"
      /> -->
    </span>
  </h3>

  <!-- (3) Grid-Enabled Gallery View -->
  <div
    class="card-grid"
    style="grid-template-columns: repeat(3, 1fr); gap: 2.5rem; align-items: stretch;"
  >
    <!-- Policy Cards -->
    {#each policies as policy}
      <div
        class="card"
        role="button"
        tabindex="0"
        on:click={() => handleSelect(policy)}
        on:keydown={(e) => e.key === "Enter" && handleSelect(policy)}
      >
        <h3>{policy.document.title}</h3>
        <p>{policy.document.description}</p>
        <!-- <button class="analysis-btn" on:click={() => handleSelect(policy)}
          >View Analysis</button
        > -->
      </div>
    {/each}

    <!-- (4) Add Policy Card Outline Button-->
    <button
      class="card add-button"
      type="button"
      style=""
      on:click={() => (docUp = true)}
      title="Add a new policy"
      aria-label="Add Policy"
    >
      <!-- Plus Icon -->
      <div id="oc-plus">
        <img
          src="plus.svg"
          alt="Plus Icon"
          style="width: 1.8rem; height: 1.8rem;"
        />
      </div>
      <!-- Text -->
      <div style="text-align: center;">
        <span style="font-size: 1.1em; color: #0C8BA7; font-weight: 500;"
          >Add Policy</span>
        <p style="font-size: 0.95em; color: #444; margin-top: 0.5em;">
          Upload a new policy for equity analysis
        </p>
      </div>
    </button>
  </div>

  <!-- --- Modals!! --- -->
  <!-- i. CTA Modal, Info/Onboarding -->
  {#if showInfo}
    <InfoModal on:close={() => (showInfo = false)} />
  {/if}
  <!-- ii. Upload Modal, Document Loading for Tool -->
  {#if docUp} 
    <DocUpModal on:close={() => (docUp = false)} />
  {/if}

</section>

<style>
  /* --- Main Container --- */
  .caption-1 {
    font-family: "Inter", sans-serif;
    font-size: 26px;
    text-align: center;
    margin-bottom: 2rem;
    max-width: 1100px;
    margin-left: auto;
    margin-right: auto;
    line-height: 1.8;
    /* background-color: #f3f3f3; */
    color: var(--primary-text);
    border-radius: 8px;
  }
  .caption-2 {
    font-family: "Inter", sans-serif;
    font-size: 1.5rem;
    font-weight: 500;
    color: var(--primary-text);
    text-align: center;
    margin-bottom: 1.2rem;
    letter-spacing: 0.02em;
    background-color: var(--primary-background);
    padding: 1rem 1rem;
  }
  .quickef-btn {
    background: var(--primary-interactive);
    border: none;
    color: white;
    font-weight: 300;
    cursor: pointer;
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
    font-family: "Inter", sans-serif;
    font-weight: 500;
    cursor: pointer;
    z-index: 10;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
  }
  .tool-button:hover {
    background: var(--primary-interactive-hover);
    color: white;
  }

  /* --- Grid, Policy Cards --- */
  .card-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 1.2rem;
    padding-left: 2rem;
    padding-right: 2rem;
    align-items: stretch;
    font-family: "Inter", sans-serif;
  }
  .card-grid > .card {
    min-height: 240px;
    position: relative;
    background: var(--primary-background);
    padding: 1rem;
    border-radius: 11px;
    box-shadow: 0 3px 8px -2px rgba(0, 0, 0, 0.32);
    transition: transform 0.2s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-self: center;
    font-size: 1.05rem;
    cursor: pointer;
  }
  .card-grid > .card:hover {
    transform: scale(1.015);
    outline: 2px solid var(--primary-interactive);
  }
  .card-grid > .card h3 {
    text-align: center;
    margin-top: 0.5em;
    padding-bottom: 0.5em;
    width: 100%;
    border-bottom: 2px solid var(--primary-interactive);
  }
  .card-grid > .card p {
    text-align: center;
  }
  /* --- ./Outline Card --- */
  .add-button {
    border: none;
    outline: 2px dashed #0c8ba7;
    background: #f8fafc;
  }
  #oc-plus {
    width: 3.5em;
    height: 3.5em;
    border-radius: 50%;
    background: #0c8ba7;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 1em;
  }
</style>


