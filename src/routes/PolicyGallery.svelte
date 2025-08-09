<script>
  // Importing Local Module
  import InfoTab from "../lib/InfoTab.svelte";

  // Policies data
  import { currentPolicy } from "../lib/stores/currentPolicy.js";
  import policies from "../lib/data/structured.json";

  // State variables for modals
  let showInfo = false;
  let modalElement;

  // Auto-focus modal when opened
  $: if (showInfo && modalElement) {
    modalElement.focus();
  }

  // State Variable from Store, Selection for Analysis Modal
  function handleSelect(policy) {
    console.log("Setting currentPolicy with:", policy);
    currentPolicy.set(policy);
    window.location.hash = "#/aview";
  }
</script>

<section>
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"
    rel="stylesheet"
  />
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
    Explore pre-analyzed water policies. Each policy has been automatically
    evaluated using our
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
    Pre-Analyzed Documents
    <span
      style="display: inline-flex; align-items: center; gap: 0.25em; margin-left: -0.15em;"
    >
      <img
        src="line-arrow-down.svg"
        alt="Down Arrow"
        style="height: 0.9em; position: relative; top: 0.1em;"
      />
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
      on:click={() => (window.location.hash = "#/tool")}
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
          >Add Policy</span
        >
        <p style="font-size: 0.95em; color: #444; margin-top: 0.5em;">
          Upload a new policy for equity analysis
        </p>
      </div>
    </button>
  </div>

  <!-- --- Modals!! --- -->
  <!-- i. Modal, Info/Onboarding -->
  {#if showInfo}
    <!-- Backdrop -->
    <div
      class="modal-backdrop"
      role="button"
      tabindex="0"
      aria-label="Close info modal"
      on:click={() => (showInfo = false)}
      on:keydown={(e) => {
        if (e.key === "Enter" || e.key === " ") {
          showInfo = false;
        }
      }}
    ></div>
    <!-- Content -->
    <div
      bind:this={modalElement}
      class="modal"
      role="dialog"
      aria-modal="true"
      tabindex="0"
      on:keydown={(e) => e.key === "Escape" && (showInfo = false)}
    >
      <!-- Close Button -->
      <button
        class="modal-close-btn"
        on:click={() => (showInfo = false)}
        aria-label="Close modal"
      >
        <img src="circle-x.svg" alt="Close" />
      </button>

      <img
        src="understanding.png"
        alt="Equity Framework Diagram"
        style="max-width: 100%; display: block; margin: 0 auto;"
      />
    </div>
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
    background-color: #f3f3f3;
    padding: 0.5rem;
    font-style: italic;
    color: #3f3f3f;
    border-radius: 8px;
  }
  .caption-2 {
    font-family: "Inter", sans-serif;
    font-size: 1.5rem;
    font-weight: 500;
    color: #3f3f3f;
    text-align: center;
    margin-bottom: 2.2rem;
    letter-spacing: 0.02em;
  }
  .quickef-btn {
    background: #0c395a;
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
    background: #1a2547;
    color: white;
  }
  .tool-button {
    position: absolute;
    top: 0.8rem;
    right: 1rem;
    background: #0c395a;
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
    background: #1a2547;
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
  }
  .card-grid > .card {
    min-height: 240px;
    position: relative;
    background: #0c8ba71c;
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
    outline: 2px solid #0c395a;
  }
  .card-grid > .card h3 {
    text-align: center;
    margin-top: 0.75em;
    margin-bottom: 0.35em;
  }
  .card-grid > .card p {
    text-align: center;
  }
  /* --- ./View Analysis Button on Card --- */
  .analysis-btn {
    position: absolute;
    bottom: 1rem;
    left: 1rem;
    right: 1rem;
    background-color: #0c395a;
    background: 0.2s;
    color: white;
    border: none;
    border-radius: 12px;
    font-size: 1.13rem;
    height: 2.7em;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 400;
    max-width: 260px;
    margin-left: auto;
    margin-right: auto;
    font-family: "Inter", sans-serif;
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

  /* --- Modal --- */
  .modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 50;
  }
  .modal {
    position: fixed;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: white;
    padding: 3.5rem;
    border-radius: 18px;
    width: 70vw;
    max-width: 1200px;
    min-height: 80vh;
    z-index: 100;
    box-shadow: 0 0 32px rgba(0, 0, 0, 0.28);
  }
  .modal-close-btn {
    position: absolute;
    top: 1.2rem;
    right: 1.2rem;
    background: none;
    border: none;
    cursor: pointer;
    z-index: 101;
    padding: 0.5rem;
    border-radius: 50%;
    transition: background-color 0.2s ease;
  }
  .modal-close-btn:hover {
    background-color: rgba(0, 0, 0, 0.1);
  }
  .modal-close-btn img {
    height: 1.5rem;
    width: 1.5rem;
    display: block;
  }
</style>
