<script>
  import { onMount } from 'svelte';
  import { slide } from 'svelte/transition';
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
  let selectedEquity = null;

  let showInfo = false; // Info modal state
  let docUp = false; // Document upload modal state

  let policies = [];

  let selectedTheme = null;

  // Curved connections
  let svgContainer = null;
  let activeButton = null;
  let detailsContainer = null;
  let animationId = null; // Track animation for cleanup
  let currentlyAnimatingEquity = null; // Track which equity is currently animating

  // --- Equity Definitions ---
  const efItems = [
    {
      id: 'procedural',
      label: 'Procedural',
      def: 'Fair and inclusive processes in policy development, implementation, and enforcement. Ensures all stakeholders have meaningful participation opportunities.',
      color: 'var(--equity-color-procedural)',
    },
    {
      id: 'structural',
      label: 'Structural',
      def: 'Addresses underlying systems and institutions that create inequities. Focuses on reforming organizational structures, legal frameworks, and policies that systematically advantage some groups while disadvantaging others.',
      color: 'var(--equity-color-structural)',
    },
    {
      id: 'distributional',
      label: 'Distributional',
      def: 'Fair allocation of benefits, burdens, and resources. Examines who gets what, when, and how in policy outcomes.',
      color: 'var(--equity-color-distributional)',
    },
    {
      id: 'recognitional',
      label: 'Recognitional',
      def: "Recognition of historical, cultural, and social contexts that shape communities' relationships with water resources and governance.",
      color: 'var(--equity-color-recognitional)',
    },
    {
      id: 'transformational',
      label: 'Transformational',
      def: 'Goes beyond fixing current systems to fundamentally reimagining and restructuring them. Creates entirely new approaches that center equity from the ground up, building regenerative systems that prevent inequities from occurring.',
      color: 'var(--equity-color-transformational)',
    },
  ];

  const themes = [
    'Theme 1',
    'Theme 2',
    'Theme 3',
    'Theme 4',
    'Theme 5',
    'Theme 6',
    'Theme 7',
  ];

  // --- Lifecycle Hook ---
  onMount(async () => {
    policies = await fetchPolicies();

    // Add resize handler to update curves
    const handleResize = () => {
      if (selectedEquity) {
        setTimeout(createCurvedConnections, 50);
      }
    };

    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
    };
  });

  // Function to create curved connections
  function createCurvedConnections() {
    if (!selectedEquity || !svgContainer) return;

    // Cancel any existing animation
    if (animationId) {
      cancelAnimationFrame(animationId);
      animationId = null;
    }

    // Clear existing paths
    svgContainer.innerHTML = '';

    // Find the active button
    activeButton = document.querySelector(
      `.equity-box.${selectedEquity}.active`
    );
    detailsContainer = document.querySelector('.equity-details-container');

    if (!activeButton || !detailsContainer) return;

    const buttonRect = activeButton.getBoundingClientRect();
    const containerRect = detailsContainer.getBoundingClientRect();
    const svgRect = svgContainer.getBoundingClientRect();

    // Calculate middle points
    const buttonCenterX = buttonRect.left + buttonRect.width / 2 - svgRect.left;
    const buttonBottom = buttonRect.bottom - svgRect.top;
    const containerCenterX =
      containerRect.left + containerRect.width / 2 - svgRect.left;
    const containerTop = containerRect.top - svgRect.top;

    // Create single curved path from button middle to container middle
    const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');

    // Calculate control point for the curve (creates a nice arc)
    const midY = buttonBottom + (containerTop - buttonBottom) / 2;
    const controlX = (buttonCenterX + containerCenterX) / 2;
    const controlY = midY + 30; // Add some curve depth

    const pathD = `M ${buttonCenterX} ${buttonBottom} 
                   Q ${controlX} ${controlY} 
                     ${containerCenterX} ${containerTop}`;

    path.setAttribute('d', pathD);
    path.setAttribute('stroke', getComputedStyle(activeButton).backgroundColor);
    path.setAttribute('stroke-width', '2');
    path.setAttribute('fill', 'none');
    path.setAttribute('opacity', '0.7');

    // Get path length and set up drawing animation like in test.html
    const pathLength = path.getTotalLength();

    // Set up the dash so the entire path is hidden at first
    path.style.strokeDasharray = pathLength;
    path.style.strokeDashoffset = pathLength;

    // Animate using requestAnimationFrame for smooth drawing
    const duration = 300; // in ms
    const startTime = performance.now();

    function animatePath(currentTime) {
      const elapsed = currentTime - startTime;
      const progress = Math.min(elapsed / duration, 1); // clamp 0–1

      // Update dash offset based on progress
      path.style.strokeDashoffset = pathLength * (1 - progress);

      if (progress >= 1) {
        // Animation completed, clear the ID and tracking
        animationId = null;
        currentlyAnimatingEquity = null;
        // After animation completes, switch to dashed appearance
        setTimeout(() => {
          path.style.strokeDasharray = '8,4';
          path.style.strokeDashoffset = '0';
        }, 100);
      } else {
        animationId = requestAnimationFrame(animatePath);
      }
    }

    // Start animation
    animationId = requestAnimationFrame(animatePath);

    // Add CSS animations if they don't exist
    if (!document.querySelector('#path-animation-style')) {
      const style = document.createElement('style');
      style.id = 'path-animation-style';
      style.textContent = `
        @keyframes fadeInScale {
          from {
            opacity: 0;
          }
          to {
            opacity: 1;
          }
        }
      `;
      document.head.appendChild(style);
    }

    // Calculate the true midpoint of the quadratic Bézier curve (t = 0.5)
    // Formula: B(t) = (1-t)²P₀ + 2(1-t)tP₁ + t²P₂
    const t = 0.3;
    const curveMidX =
      Math.pow(1 - t, 2) * buttonCenterX +
      2 * (1 - t) * t * controlX +
      Math.pow(t, 2) * containerCenterX;
    const curveMidY =
      Math.pow(1 - t, 2) * buttonBottom +
      2 * (1 - t) * t * controlY +
      Math.pow(t, 2) * containerTop;

    // Create decorative whirl/knot at the actual midpoint
    const whirl = document.createElementNS(
      'http://www.w3.org/2000/svg',
      'circle'
    );
    whirl.setAttribute('cx', curveMidX);
    whirl.setAttribute('cy', curveMidY);
    whirl.setAttribute('r', '6');
    whirl.setAttribute('fill', getComputedStyle(activeButton).backgroundColor);
    whirl.setAttribute('opacity', '0');
    whirl.style.animation = 'fadeInScale 0.2s ease-out 0.6s forwards';
    whirl.style.animationDelay = '0s';

    // Add a smaller inner circle for the knot effect
    const innerWhirl = document.createElementNS(
      'http://www.w3.org/2000/svg',
      'circle'
    );
    innerWhirl.setAttribute('cx', curveMidX);
    innerWhirl.setAttribute('cy', curveMidY);
    innerWhirl.setAttribute('r', '4');
    innerWhirl.setAttribute('fill', 'white');
    innerWhirl.setAttribute('opacity', '0');
    innerWhirl.style.animation = 'fadeInScale 0.2s ease-out 0.6s forwards';
    innerWhirl.style.animationDelay = '0s';

    svgContainer.appendChild(path);
    svgContainer.appendChild(whirl);
    svgContainer.appendChild(innerWhirl);
  }

  // Handle equity selection changes
  function handleEquitySelection(equityType) {
    const previousEquity = selectedEquity;

    // Toggle the selected equity
    selectedEquity = selectedEquity === equityType ? null : equityType;

    // Cancel any running animation
    if (animationId) {
      cancelAnimationFrame(animationId);
      animationId = null;
    }

    if (selectedEquity) {
      // Create new animation for the selected equity
      currentlyAnimatingEquity = selectedEquity;
      setTimeout(createCurvedConnections, 100); // Small delay for DOM updates
    } else {
      // Clear everything when no equity is selected
      currentlyAnimatingEquity = null;
      if (svgContainer) {
        svgContainer.innerHTML = '';
      }
    }
  }

  function toggleTheme(theme) {
    selectedTheme = selectedTheme === theme ? null : theme;
  }

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
  <h3 class="caption-2" style="position: relative;">
    <!-- Pre-Analyzed Documents -->
    <!-- <img
      src="landmark.svg"
      alt=""
      style="height: 0.9em; position: relative; top: 0.1em;"
    /> -->
    Understand the Five Equities
    <!-- Document Hierarchy Flow Chart -->
    <div class="eqbox-container">
      <button
        type="button"
        class="equity-box procedural {selectedEquity === 'procedural'
          ? 'active'
          : ''}"
        on:click={() => handleEquitySelection('procedural')}
        aria-label="Show Procedural Equity details"
      >
        <span class="equity-name">Procedural Equity</span>
      </button>
      <button
        type="button"
        class="equity-box structural {selectedEquity === 'structural'
          ? 'active'
          : ''}"
        on:click={() => handleEquitySelection('structural')}
        aria-label="Show Structural Equity details"
      >
        <span class="equity-name">Structural Equity</span>
      </button>
      <button
        type="button"
        class="equity-box distributional {selectedEquity === 'distributional'
          ? 'active'
          : ''}"
        on:click={() => handleEquitySelection('distributional')}
        aria-label="Show Distributional Equity details"
      >
        <span class="equity-name">Distributional Equity</span>
      </button>
      <button
        type="button"
        class="equity-box recognitional {selectedEquity === 'recognitional'
          ? 'active'
          : ''}"
        on:click={() => handleEquitySelection('recognitional')}
        aria-label="Show Recognitional Equity details"
      >
        <span class="equity-name">Recognitional Equity</span>
      </button>
      <button
        type="button"
        class="equity-box transformational {selectedEquity ===
        'transformational'
          ? 'active'
          : ''}"
        on:click={() => handleEquitySelection('transformational')}
        aria-label="Show Transformational Equity details"
      >
        <span class="equity-name">Transformational Equity</span>
      </button>
    </div>

    <!-- SVG for curved connections -->
    <svg
      bind:this={svgContainer}
      class="connection-svg"
      style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: 5;"
    ></svg>

    <!-- Equity Details Row -->
    {#if selectedEquity}
      {#each efItems as item}
        {#if item.id === selectedEquity}
          <div
            class="equity-details-container"
            style="--equity-color: {item.color};"
            in:slide={{ duration: 400, delay: 100 }}
            out:slide={{ duration: 300 }}
          >
            <div class="equity-details-content">
              <!-- <h3 class="equity-details-title">{item.label} Equity</h3> -->
              <p class="equity-details-text">{item.def}</p>
            </div>
          </div>
        {/if}
      {/each}
    {/if}
  </h3>

  <div class="theme-strip">
    <div class="theme-controls">
      {#each themes as theme}
        <button
          type="button"
          class="theme-label {selectedTheme === theme
            ? 'active'
            : selectedTheme
            ? 'inactive'
            : ''}"
          on:click={() => toggleTheme(theme)}
          aria-pressed={selectedTheme === theme}
        >
          {theme}
        </button>
      {/each}
    </div>
  </div>

  <!-- (1) Gantt-like Policy Gallery (Federal, State, Agency, Other) -->
  <div class="gallery">
    <!-- Row: Federal -->
    <div class="row federal">
      <div class="row-label federal">
        <div class="row-label-content">
          <span class="row-icon">
            <img src="landmark.svg" alt="Federal" />
          </span>
          <span> Federal </span>
          <span class="row-count">{policies.filter(isFederal).length}</span>
        </div>
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
        <div class="row-label-content">
          <span class="row-icon">
            <img src="landmark.svg" alt="State" />
          </span>
          <span> State </span>
          <span class="row-count">{policies.filter(isState).length}</span>
        </div>
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
        <div class="row-label-content">
          <span class="row-icon">
            <img src="landmark.svg" alt="Agency" />
          </span>
          <span> Agency </span>
          <span class="row-count">{policies.filter(isAgency).length}</span>
        </div>
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
        <div class="row-label-content">
          <span class="row-icon">
            <img src="document.svg" alt="Agency" />
          </span>
          <span> Other </span>
          <span class="row-count">{policies.filter(isOther).length}</span>
        </div>
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
    <!-- <div>
      <button
        class="add-policy-card"
        type="button"
        on:click={() => (docUp = true)}
        title="Add a new policy"
        aria-label="Add Policy"
        style="display: block; margin: 0 auto;"
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
    </div> -->
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
  <!-- <InfoTab /> -->

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

<style lang="postcss">
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

  /* --- Equity Info Buttons --- */
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
    border: 0.5px solid rgba(0, 0, 0, 0.1);
    padding: 1rem 1.5rem;
    text-align: center;
    width: 180px;
    height: 80px;
    display: flex;
    flex-direction: column;
    justify-content: center;
    gap: 0.25rem;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
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
  .equity-box.active {
    transform: translateY(-12px) scale(1.1);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
    /* border: 3px solid rgba(255, 255, 255, 0.95); */
    position: relative;
    z-index: 10;
  }
  .equity-name {
    color: rgb(255, 255, 255);
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

  /* --- Theme Selector Buttons --- */
  .theme-strip {
    display: flex;
    justify-content: center;
    margin: 1.5rem auto 2.25rem;
    padding: 0.85rem 0rem;

    overflow-x: auto;
    scrollbar-width: none;
    -ms-overflow-style: none;
    background: white;
    border: 1px solid #d1d5db;
    border-radius: 48px;
    box-shadow: 0 12px 32px rgba(15, 23, 42, 0.08);
    color: black
  }

  .theme-strip::-webkit-scrollbar {
    display: none;
  }

  .theme-controls {
    display: flex;
    flex-wrap: nowrap;
    align-items: center;
    justify-content: space-evenly;
    gap: 0.3rem;
    padding: 0.35rem 0rem;
    width: 80%;
    min-width: max-content;
    flex: 1 1 0;
  }

  .theme-label {
    background: transparent;
    flex: 0 0 auto;
    border: none;
    color: inherit;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 0.6rem;
    font-family: 'Inter', sans-serif;
    font-size: 0.95rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    white-space: nowrap;
    padding: 0.45rem 1.35rem;
    transition:
      opacity 0.2s ease,
      transform 0.2s ease,
      text-shadow 0.2s ease,
      color 0.2s ease;
  }

  .theme-label:hover {
    transform: translateY(-2px);
  }

  .theme-label:focus-visible {
    outline: 2px solid rgba(255, 255, 255, 0.6);
    outline-offset: 4px;
  }

  .theme-label.active {
    opacity: 1;
    color: var(
      --theme-strip-active-text,
      color-mix(in srgb, var(--primary-text, #101828) 60%, #000 40%)
    );
    text-shadow: 0 0 14px
      var(--theme-strip-active-glow, rgba(15, 23, 42, 0.35));
    transform: translateY(-4px);
  }

  .theme-label.inactive {
    opacity: 0.45;
    filter: grayscale(1);
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
    grid-template-columns: 180px 1fr;
    align-items: stretch;
    /* gap: 0.75rem; */
  }

  .row-label {
    display: flex;
    /* align-items: center; */
    font-weight: 700;
    /* border: 2px solid currentColor; */
    border-top-left-radius: 10px;
    border-bottom-left-radius: 10px;
    padding: 0.75rem 0.9rem;
    /* background: white; */
    /* max-height: 100px; */
  }
  .row-label-content {
    display: flex;
    height: fit-content;
    align-items: center;
    gap: 0.5rem;
    & > .row-icon img {
      height: 1.2rem;
    }
    & > .row-count {
      font-size: 0.85rem;
      opacity: 0.8;
    }
    & > span {
      height: fit-content;
    }
  }

  /* .row-label .row-icon img {
    height: 1.2rem;
  } */

  .row-count {
    /* margin-left: auto; */
    /* font-size: 0.85rem; */
    /* opacity: 0.8; */
    /* background: rgba(0, 0, 0, 0.04); */
    /* padding: 0.15rem 0.5rem; */
    /* border-radius: 999px; */
  }

  .row-track {
    position: relative;
    display: flex;
    gap: 0.5rem;
    align-items: center;
    padding: 0.5rem;
    border-top-right-radius: 10px;
    border-bottom-right-radius: 10px;
    overflow-x: auto;
    background: var(--track-color);
    min-height: 60px;
    width: 1200px;
  }
  .row.other > .row-track {
    background: var(--policy-other-light);
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

  .row-label.federal {
    color: var(--policy-federal);
    /* background: var(--policy-federal-light); */
    background: var(--track-color);
  }
  .row-label.agency {
    color: var(--policy-agency);
    /* background: var(--policy-agency-light); */
    background: var(--track-color);
  }
  .row-label.other {
    color: var(--policy-other);
    background: var(--policy-other-light);
  }
  .row-label.state {
    color: var(--policy-state);
    /* background: var(--policy-state-light); */
    background: var(--track-color);
  }

  @media (max-width: 768px) {
    .row {
      grid-template-columns: 160px 1fr;
    }
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
    margin-left: 0rem;
    margin-right: 0rem;
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

  /* --- Equity Details Styling --- */
  .equity-details-container {
    background: white;
    border: 3px solid var(--equity-color);
    /* border-top: none; */
    border-radius: 4px;
    margin-left: auto;
    margin-right: auto;
    max-width: 800px;
    width: 90%;
    padding: 1.5rem 2rem 2rem 2rem;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    position: relative;
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* .equity-details-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 200px;
    height: 3px;
    background: var(--equity-color);
    border-radius: 0 0 3px 3px;
  } */

  .equity-details-content {
    position: relative;
    z-index: 2;
  }

  .equity-details-text {
    color: var(--primary-text);
    font-size: 0.9rem;
    font-style: italic;
    line-height: 1.6;
    margin: 0;
    text-align: center;
    font-weight: 400;
  }

  @media (max-width: 768px) {
    .equity-details-container {
      width: 95%;
      padding: 1rem 1.5rem 1.5rem 1.5rem;
    }

    .equity-details-text {
      font-size: 1rem;
    }
  }
</style>
