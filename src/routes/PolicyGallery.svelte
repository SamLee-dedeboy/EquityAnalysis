<script>
  import { onMount } from 'svelte';
  import { server_address } from '../constants.js';

  // Importing Local Modules
  import InfoTab from '../lib/InfoTab.svelte';
  import InfoModal from '../lib/pg-modals/InfoModal.svelte';
  import DocUpModal from '../lib/pg-modals/DocUpModal.svelte';

  // Importing Stores
  import {
    currentPolicy,
    fetchPolicies,
    fetchPolicyDataById,
  } from '../lib/stores/currentPolicy.js';

  // --- State Variables ---
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

  // Helper function to check if a policy belongs to a specific tier
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

  function isCourt(policy) {
    return (
      policy.document.type === 'court' ||
      policy.document.title.toLowerCase().includes('court') ||
      policy.document.title.toLowerCase().includes('decision') ||
      policy.document.title.toLowerCase().includes('ruling')
    );
  }

  function isPlanning(policy) {
    return (
      policy.document.type === 'planning' ||
      policy.document.title.toLowerCase().includes('plan') ||
      policy.document.title.toLowerCase().includes('strategy') ||
      policy.document.title.toLowerCase().includes('draft')
    );
  }

  function isOperations(policy) {
    return (
      policy.document.type === 'operations' ||
      policy.document.title.toLowerCase().includes('operation') ||
      policy.document.title.toLowerCase().includes('implementation') ||
      policy.document.title.toLowerCase().includes('procedure')
    );
  }

  function isOther(policy) {
    return (
      !isFederal(policy) &&
      !isAgency(policy) &&
      !isCourt(policy) &&
      !isPlanning(policy) &&
      !isOperations(policy)
    );
  }
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
    <img
      src="landmark.svg"
      alt=""
      style="height: 0.9em; position: relative; top: 0.1em;"
    />
    Document Hierarchy Flow
    <!-- Document Hierarchy Flow Chart -->
    <div class="hierarchy-flow">
      <div class="flow-item">
        <div class="flow-box federal">
          <span class="flow-label">Federal Law</span>
          <span class="flow-desc">Constitutional & Legislative Framework</span>
        </div>
      </div>
      <div class="flow-arrow">→</div>
      <div class="flow-item">
        <div class="flow-box agency">
          <span class="flow-label">Agency Law</span>
          <span class="flow-desc">Regulatory Implementation</span>
        </div>
      </div>
      <div class="flow-arrow">→</div>
      <div class="flow-item">
        <div class="flow-box court">
          <span class="flow-label">Court Decision</span>
          <span class="flow-desc">Judicial Interpretation</span>
        </div>
      </div>
      <div class="flow-arrow">→</div>
      <div class="flow-item">
        <div class="flow-box planning">
          <span class="flow-label">Planning</span>
          <span class="flow-desc">Strategic Development</span>
        </div>
      </div>
      <div class="flow-arrow">→</div>
      <div class="flow-item">
        <div class="flow-box operations">
          <span class="flow-label">Daily Operations</span>
          <span class="flow-desc">Implementation & Execution</span>
        </div>
      </div>
    </div>
  </h3>

  <!-- (1) Hierarchical Policy Gallery -->
  <div class="hierarchical-gallery">
    <!-- Federal Law Section -->
    <div class="policy-section">
      <h4 class="section-header federal">
        <span class="section-icon">
          <img src="landmark.svg" alt="Federal Law" />
        </span>
        Federal Law
        <span class="section-count"
          >{policies.filter(isFederal).length} Documents</span
        >
      </h4>
      <div class="policy-cards">
        {#each policies.filter(isFederal) as policy}
          <div
            class="policy-card"
            role="button"
            tabindex="0"
            on:click={() => handleSelect(policy)}
            on:keydown={e => e.key === 'Enter' && handleSelect(policy)}
          >
            <h5>{policy.document.title}</h5>
            <p>{policy.document.description}</p>
            <div class="tier-chip federal-chip">Federal Law</div>
            <button class="analysis-btn" on:click={() => handleSelect(policy)}
              >View Analysis</button
            >
          </div>
        {/each}
        {#if policies.filter(isFederal).length === 0}
          <div class="empty-section">No federal laws available</div>
        {/if}
      </div>
    </div>

    <!-- Agency Law Section -->
    <div class="policy-section">
      <h4 class="section-header agency">
        <span class="section-icon">
          <img src="user-group.svg" alt="Agency Law" />
        </span>
        Agency Law
        <span class="section-count"
          >{policies.filter(isAgency).length} Documents</span
        >
      </h4>
      <div class="policy-cards">
        {#each policies.filter(isAgency) as policy}
          <div
            class="policy-card"
            role="button"
            tabindex="0"
            on:click={() => handleSelect(policy)}
            on:keydown={e => e.key === 'Enter' && handleSelect(policy)}
          >
            <h5>{policy.document.title}</h5>
            <p>{policy.document.description}</p>
            <div class="tier-chip agency-chip">Agency Law</div>
            <button class="analysis-btn" on:click={() => handleSelect(policy)}
              >View Analysis</button
            >
          </div>
        {/each}
        {#if policies.filter(isAgency).length === 0}
          <div class="empty-section">No agency regulations available</div>
        {/if}
      </div>
    </div>

    <!-- Court Decision Section -->
    <div class="policy-section">
      <h4 class="section-header court">
        <span class="section-icon">
          <img src="landmark.svg" alt="Court Decision" />
        </span>
        Court Decision
        <span class="section-count"
          >{policies.filter(isCourt).length} Documents</span
        >
      </h4>
      <div class="policy-cards">
        {#each policies.filter(isCourt) as policy}
          <div
            class="policy-card"
            role="button"
            tabindex="0"
            on:click={() => handleSelect(policy)}
            on:keydown={e => e.key === 'Enter' && handleSelect(policy)}
          >
            <h5>{policy.document.title}</h5>
            <p>{policy.document.description}</p>
            <div class="tier-chip court-chip">Court Decision</div>
            <button class="analysis-btn" on:click={() => handleSelect(policy)}
              >View Analysis</button
            >
          </div>
        {/each}
        {#if policies.filter(isCourt).length === 0}
          <div class="empty-section">No court decisions available</div>
        {/if}
      </div>
    </div>

    <!-- Planning Section -->
    <div class="policy-section">
      <h4 class="section-header planning">
        <span class="section-icon">
          <img src="chart.svg" alt="Planning" />
        </span>
        Planning
        <span class="section-count"
          >{policies.filter(isPlanning).length} Documents</span
        >
      </h4>
      <div class="policy-cards">
        {#each policies.filter(isPlanning) as policy}
          <div
            class="policy-card"
            role="button"
            tabindex="0"
            on:click={() => handleSelect(policy)}
            on:keydown={e => e.key === 'Enter' && handleSelect(policy)}
          >
            <h5>{policy.document.title}</h5>
            <p>{policy.document.description}</p>
            <div class="tier-chip planning-chip">Planning</div>
            <button class="analysis-btn" on:click={() => handleSelect(policy)}
              >View Analysis</button
            >
          </div>
        {/each}
        {#if policies.filter(isPlanning).length === 0}
          <div class="empty-section">No planning documents available</div>
        {/if}
      </div>
    </div>

    <!-- Daily Operations Section -->
    <div class="policy-section">
      <h4 class="section-header operations">
        <span class="section-icon">
          <img src="network.svg" alt="Daily Operations" />
        </span>
        Daily Operations
        <span class="section-count"
          >{policies.filter(isOperations).length} Documents</span
        >
      </h4>
      <div class="policy-cards">
        {#each policies.filter(isOperations) as policy}
          <div
            class="policy-card"
            role="button"
            tabindex="0"
            on:click={() => handleSelect(policy)}
            on:keydown={e => e.key === 'Enter' && handleSelect(policy)}
          >
            <h5>{policy.document.title}</h5>
            <p>{policy.document.description}</p>
            <div class="tier-chip operations-chip">Daily Operations</div>
            <button class="analysis-btn" on:click={() => handleSelect(policy)}
              >View Analysis</button
            >
          </div>
        {/each}
        {#if policies.filter(isOperations).length === 0}
          <div class="empty-section">No operational documents available</div>
        {/if}
      </div>
    </div>

    <!-- Other Documents Section -->
    <div class="policy-section">
      <h4 class="section-header other">
        <span class="section-icon">
          <img src="document.svg" alt="Other Documents" />
        </span>
        Other Documents
        <span class="section-count"
          >{policies.filter(isOther).length} Documents</span
        >
      </h4>
      <div class="policy-cards">
        {#each policies.filter(isOther) as policy}
          <div
            class="policy-card"
            role="button"
            tabindex="0"
            on:click={() => handleSelect(policy)}
            on:keydown={e => e.key === 'Enter' && handleSelect(policy)}
          >
            <h5>{policy.document.title}</h5>
            <p>{policy.document.description}</p>
            <div class="tier-chip other-chip">Other Document</div>
            <button class="analysis-btn" on:click={() => handleSelect(policy)}
              >View Analysis</button
            >
          </div>
        {/each}
        {#if policies.filter(isOther).length === 0}
          <div class="empty-section">No other documents available</div>
        {/if}
      </div>
    </div>

    <!-- Add Policy Section -->
    <div class="add-policy-section">
      <button
        class="add-policy-card"
        type="button"
        on:click={() => (docUp = true)}
        title="Add a new policy"
        aria-label="Add Policy"
      >
        <div class="add-icon">
          <img
            src="plus.svg"
            alt="Plus Icon"
            style="width: 2rem; height: 2rem;"
          />
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
  <!-- ii. Upload Modal, Document Loading for Tool -->
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
  /* --- Document Hierarchy Flow Chart --- */
  .hierarchy-flow {
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
  .flow-box {
    background: white;
    border: 2px solid;
    border-radius: 8px;
    padding: 1rem 1.5rem;
    text-align: center;
    min-width: 140px;
    height: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.25rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    transition:
      transform 0.2s ease,
      box-shadow 0.2s ease;
  }
  .flow-box:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
  }
  .flow-label {
    font-weight: 600;
    font-size: 0.9rem;
    line-height: 1.2;
  }
  .flow-desc {
    font-size: 0.7rem;
    opacity: 0.8;
    line-height: 1.1;
  }
  .flow-arrow {
    font-size: 1.5rem;
    color: var(--primary-interactive);
    font-weight: bold;
    margin: 0 0.25rem;
    flex-shrink: 0;
  }
  /* Color coding for different document types */
  .federal {
    border-color: var(--policy-federal);
    background: var(--policy-federal-light);
    color: var(--policy-federal);
  }
  .agency {
    border-color: var(--policy-agency);
    background: var(--policy-agency-light);
    color: var(--policy-agency);
  }
  .court {
    border-color: var(--policy-court);
    background: var(--policy-court-light);
    color: var(--policy-court);
  }
  .planning {
    border-color: var(--policy-planning);
    background: var(--policy-planning-light);
    color: var(--policy-planning);
  }
  .operations {
    border-color: var(--policy-operations);
    background: var(--policy-operations-light);
    color: var(--policy-operations);
  }
  /* Responsive design for flow chart */
  @media (max-width: 768px) {
    .hierarchy-flow {
      flex-direction: column;
      gap: 1rem;
    }

    .flow-arrow {
      transform: rotate(90deg);
      font-size: 1.2rem;
    }

    .flow-box {
      min-width: 200px;
      height: 70px;
    }
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

  /* --- Hierarchical Policy Gallery --- */
  .hierarchical-gallery {
    max-width: 1200px;
    margin: 0 auto 4rem auto;
    padding: 0 2rem;
    font-family: 'Inter', sans-serif;
    overflow: visible;
  }

  .policy-section {
    margin-bottom: 3rem;
    position: relative;
    z-index: 1;
    overflow: visible;
  }

  .section-header {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    font-size: 1.4rem;
    font-weight: 600;
    margin-bottom: 2rem;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    border: 2px solid;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    position: relative;
    z-index: 1;
  }

  .section-icon {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .section-icon img {
    width: 1.5rem;
    height: 1.5rem;
    filter: currentColor;
  }

  /* Invert colors for agency and planning SVGs */
  .agency .section-icon img,
  .planning .section-icon img {
    filter: invert(1);
  }

  .section-count {
    font-size: 0.9rem;
    font-weight: 400;
    opacity: 0.8;
    margin-left: auto;
  }

  .policy-cards {
    display: flex;
    gap: 1.5rem;
    overflow-x: auto;
    overflow-y: visible;
    padding-bottom: 2rem;
    padding-top: 0.5rem;
    scroll-behavior: smooth;
    z-index: 100;
  }

  .policy-cards::-webkit-scrollbar {
    height: 8px;
  }

  .policy-cards::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
  }

  .policy-cards::-webkit-scrollbar-thumb {
    background: #c1c1c1;
    border-radius: 4px;
  }

  .policy-cards::-webkit-scrollbar-thumb:hover {
    background: #a8a8a8;
  }

  .policy-card {
    background: white;
    border: 2px solid #e5e7eb;
    border-radius: 12px;
    padding: 1.5rem;
    cursor: pointer;
    transition: all 0.2s ease;
    position: relative;
    min-height: 200px;
    max-height: 200px;
    min-width: 320px;
    max-width: 320px;
    flex-shrink: 0;
    display: flex;
    flex-direction: column;
    z-index: 2;
  }

  .policy-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
    z-index: 10;
    border-color: var(--primary-interactive);
  }

  .policy-card h5 {
    font-size: 1.1rem;
    font-weight: 600;
    margin: 0 0 0.75rem 0;
    line-height: 1.3;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
    color: var(--primary-text);
  }

  .policy-card p {
    font-size: 0.9rem;
    line-height: 1.5;
    margin: 0 0 1rem 0;
    flex-grow: 1;
    opacity: 0.8;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 4;
    line-clamp: 4;
    -webkit-box-orient: vertical;
  }

  .tier-chip {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    margin-bottom: 0.75rem;
    margin-top: auto;
    text-align: center;
    width: fit-content;
  }

  .federal-chip {
    background: var(--policy-federal);
    color: white;
  }

  .agency-chip {
    background: var(--policy-agency);
    color: white;
  }

  .court-chip {
    background: var(--policy-court);
    color: white;
  }

  .planning-chip {
    background: var(--policy-planning);
    color: white;
  }

  .operations-chip {
    background: var(--policy-operations);
    color: white;
  }

  .other-chip {
    background: var(--policy-other);
    color: white;
  }

  .analysis-btn {
    background: var(--primary-interactive);
    border: none;
    border-radius: 6px;
    padding: 0.5rem 1rem;
    font-size: 0.85rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    color: white;
  }

  .analysis-btn:hover {
    background: var(--primary-interactive-hover);
    transform: translateY(-1px);
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
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
    min-height: 200px;
    max-height: 200px;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .add-policy-section {
    margin-top: 2rem;
    display: flex;
    justify-content: center;
  }

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
