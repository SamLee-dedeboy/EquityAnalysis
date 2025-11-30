<script>
  import { onMount } from 'svelte';
  import {
    currentPolicy,
    fetchPolicies,
    fetchPolicyDataById,
  } from '../lib/stores/currentPolicy.js';

  // Theme Constants
  const tierOptions = {
    "1": "Agricultural Productivity",
    "2": "River Flows",
    "3": "Delta Estuary Health",
    "4": "Freshwater for in-Delta Use",
    "5": "Freshwater for Delta Exports",
    "6": "Reservoir Storage",
    "7": "Groundwater",
    "8": "Salmon Abundance"
  };

  // Accent Colors for Cards
  const accentPalette = ['#7cc4ff', '#f5c84c', '#71d2c6', '#b499ff', '#f6a387', '#5ad9a6'];

  let policies = [];
  let searchTerm = '';
  let selectedTier = null;
  let controlsOpen = false;

  // Lifecycle Hook
  onMount(async () => {
    const list = await fetchPolicies();
    policies = list || [];
  });

  
  $: filteredPolicies = (policies || []).filter(policy => {
    const term = searchTerm.trim().toLowerCase();
    const matchesSearch = term
      ? (policy.document?.title || '').toLowerCase().includes(term) ||
        (policy.document?.filename || '').toLowerCase().includes(term)
      : true;

    const matchesTier = selectedTier
      ? Array.isArray(policy.tiers) && policy.tiers.map(Number).includes(Number(selectedTier))
      : true;

    return matchesSearch && matchesTier;
  });

  function accentForIndex(index) {
    return accentPalette[index % accentPalette.length];
  }

  function toggleTier(tier) {
    selectedTier = selectedTier === tier ? null : tier;
  }

  async function handleSelect(policy) {
    const policyData = await fetchPolicyDataById(policy.id);
    currentPolicy.set(policyData);
    window.location.hash = '#/aview';
  }

  // Tool Nav, for Dev Use
  let tscreen = false;
</script>

<section class="page">
  <link
    href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap"
    rel="stylesheet"
  />

  <!--- Side Bar --->
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-mark" aria-hidden="true"></div>
      <div class="brand-text">
        <p class="eyebrow">Equiflow</p>
        <p class="tagline">Placeholder Tagline</p>
      </div>
    </div>

    <div class="sidebar-separator" aria-hidden="true"></div>

    <div class="tiers">
      <p class="section-label">Tiers</p>
      <div class="tier-list">
      {#each Object.entries(tierOptions) as [tierId, tierName]}
        <button
        type="button"
        class={`tier ${selectedTier === tierId ? 'active' : ''}`}
        on:click={() => toggleTier(tierId)}
        aria-pressed={selectedTier === tierId}
        >
        <span class="tier-icon" aria-hidden="true"></span>
        <span>{tierName}</span>
        </button>
      {/each}
      </div>
    </div>

    <div class="sidebar-footer">
      {#if tscreen}
        <button type="button" on:click={() => (window.location.hash = '#/tool')}>
          Tool
        </button>
      {/if}
      <div> 
        <button type="button" class="learn-more" on:click={() => (window.location.hash = '#/info')}>
          Click here
        </button> 
        if you want to learn more about how Equiflow's analysis works.
      </div>
    </div>
  </aside>

  <!--- Content --->
  <div class="content">
    <div class="search-bar">
      <label class="search" aria-label="Search policies">
        <svg viewBox="0 0 20 20" fill="none" stroke="currentColor" aria-hidden="true">
          <circle cx="9" cy="9" r="6" stroke-width="2" />
          <path d="m13.5 13.5 3 3" stroke-width="2" stroke-linecap="round" />
        </svg>
        <input
          type="search"
          placeholder="Search policies..."
          bind:value={searchTerm}
          autocomplete="off"
        />
      </label>
      <button
        type="button"
        class="filter-btn"
        on:click={() => (controlsOpen = !controlsOpen)}
        aria-pressed={controlsOpen}
        aria-expanded={controlsOpen}
      >
        <svg viewBox="0 0 512 512" aria-hidden="true" fill="currentColor">
          <path d="M304 416c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16h-64c-8.8 0-16-7.2-16-16v-32c0-8.8 7.2-16 16-16h64zM176 352c14.2 0 21.3 17.3 11.3 27.3l-80 96c-2.9 2.9-6.9 4.7-11.3 4.7-4.4 0-8.4-1.8-11.3-4.7l-80-96c-10.1-10.1-2.9-27.3 11.3-27.3h48v-304c0-8.8 7.2-16 16-16h32c8.8 0 16 7.2 16 16v304h48zM432 160c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16h-192c-8.8 0-16-7.2-16-16v-32c0-8.8 7.2-16 16-16h192zM368 288c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16h-128c-8.8 0-16-7.2-16-16v-32c0-8.8 7.2-16 16-16h128zM496 32c8.8 0 16 7.2 16 16v32c0 8.8-7.2 16-16 16h-256c-8.8 0-16-7.2-16-16v-32c0-8.8 7.2-16 16-16h256z"></path>
        </svg>
        <span>Filter</span>
      </button>
    </div>

    {#if controlsOpen}
      <div class="control-buttons-inline">
        <button type="button">One</button>
        <button type="button">Two</button>
        <button type="button">Three</button>
      </div>
    {/if}

    <div class="cards-grid">
      {#if filteredPolicies.length}
        {#each filteredPolicies as policy, index}
          <div
            class="policy-card"
            role="button"
            tabindex="0"
            on:click={() => handleSelect(policy)}
            on:keydown={event => event.key === 'Enter' && handleSelect(policy)}
          >
            <div class="card-header">
              <span class="pill id-pill">Identifier</span>
              <span class="pill date-pill">Date</span>
            </div>

            <div class="card-illustration">
              <div class="line-group">
                <span></span>
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div class="color-block" style={`background: ${accentForIndex(index)};`}></div>
              <div class="line-group">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>

            <div class="card-text">
              <h3>{policy.document?.title || 'Untitled policy'}</h3>
              <p>
                {policy.document?.filename
                  ? `Analysis generated from ${policy.document.filename}`
                  : 'A comprehensive equity analysis ready to explore.'}
              </p>
            </div>
          </div>
        {/each}
      {:else}
        <div class="empty">No policies match your search.</div>
      {/if}
    </div>
  </div>

</section>

<style>
  /* ------ Layout ------ */
  .page {
    display: grid;
    grid-template-columns: 480px 1fr;
    height: 100vh;
    width: 100vw;
    color: #e8edf5;
    font-family: 'Inter', sans-serif;
    background: #0c111a;
  }
  /* ------ Sidebar ------ */
  .sidebar {
    background: #0d1420;
    padding: 2.5rem 1.8rem;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
    border-right: 1px solid rgba(255, 255, 255, 0.04);
    height: 100vh;
    overflow-y: auto;
  }

  .brand {
    display: flex;
    gap: 0.75rem;
    align-items: flex-start;
  }

  .brand-mark {
    width: 40px;
    height: 40px;
    border-radius: 12px;
    background: linear-gradient(135deg, #6cc7ff, #1d9fff);
    box-shadow: 0 8px 30px rgba(0, 163, 255, 0.25);
  }

  .brand-text {
    display: grid;
    gap: 0.25rem;
    max-width: 230px;
  }

  .eyebrow {
    margin: 0;
    font-weight: 700;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #e8edf5;
  }

  .tagline {
    margin: 0;
    color: #9aa4b5;
    line-height: 1.4;
    font-size: 1.05rem;
  }

  .search {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: #111a27;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 0.75rem 0.9rem;
    color: #9aa4b5;
    height: 48px;
  }

  .search svg {
    width: 20px;
    height: 20px;
  }

  .search input {
    background: transparent;
    border: none;
    outline: none;
    color: #e8edf5;
    width: 100%;
    font-size: 1.05rem;
  }

  .tiers {
    display: grid;
    gap: 0.5rem;
  }

  .section-label {
    margin: 0;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    font-weight: 700;
    font-size: 0.9rem;
    color: #6e7687;
  }

  .tier-list {
    display: grid;
    gap: 0.6rem;
  }

  .tier {
    width: 100%;
    background: transparent;
    color: #d5d9e1;
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    text-align: left;
    display: flex;
    align-items: center;
    gap: 0.65rem;
    font-weight: 700;
    font-size: 1.15rem;
    transition: all 0.2s ease;
  }

  .tier:hover {
    border-color: rgba(255, 255, 255, 0.12);
    background: rgba(255, 255, 255, 0.02);
  }

  .tier.active {
    background: linear-gradient(135deg, #18314a, #0b465a);
    border-color: #0b465a;
    box-shadow: 0 2px 14px rgba(13, 125, 220, 0.25);
  }

  .tier-icon {
    width: 36px;
    height: 36px; 
    margin-right: .5rem;
    border-radius: 10px;
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.06);
    flex-shrink: 0;
    display: inline-flex;
    align-items: center;
    justify-content: center;
  }

  .sidebar-separator {
    height: 1px;
    width: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.1), transparent);
    margin: 0.5rem 0 0.75rem;
  }

  .sidebar-footer {
    margin-top: auto;
    display: grid;
    gap: 0.6rem;
  }

  .learn-more {
    background: transparent;
    border: none;
    color: #d5d9e1;
    text-decoration: underline;
    font-weight: 600;
    padding: 0.5rem 0.2rem;
    font-size: 1.05rem;
    text-align: left;
  }

  .learn-more:hover {
    color: #f2f5fa;
  }

  /* ------ Content ------ */
  .content {
    padding: 2.25rem 0 2.5rem;
    background: radial-gradient(circle at 20% 20%, rgba(63, 121, 255, 0.08), transparent 40%),
      radial-gradient(circle at 80% 0%, rgba(255, 214, 102, 0.08), transparent 35%),
      #0c111a;
    height: 100vh;
    overflow-y: auto;
  }

  .search-bar {
    padding: 0 3rem 2rem;
    display: flex;
    justify-content: flex-end;
    align-items: center;
    gap: 0.75rem;
  }

  .search-bar .search {
    width: 20%;
    min-width: 200px;
    max-width: none;
  }

  .filter-btn {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    height: 44px;
    background: #7b7f85;
    border: none;
    color: white;
    border-radius: 999px;
    padding: 0 1rem;
    font-weight: 700;
    font-size: 0.95rem;
    white-space: nowrap;
    box-shadow: 0 10px 24px rgba(0, 0, 0, 0.25);
  }

  .filter-btn svg {
    width: 18px;
    height: 18px;
  }

  .control-buttons-inline {
    padding: 0 3rem 2rem;
    display: flex;
    justify-content: flex-end;
    gap: 0.5rem;
  }

  .control-buttons-inline button {
    background: rgba(255, 255, 255, 0.06);
    border: 1px solid rgba(255, 255, 255, 0.08);
    color: #d5d9e1;
    border-radius: 10px;
    padding: 0.35rem 0.75rem;
    font-size: 0.9rem;
    white-space: nowrap;
  }

  .cards-grid {
    padding: 0 3rem;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 1.6rem;
  }

  .policy-card {
    background: #0f1724;
    border-radius: 16px;
    padding: 1.2rem 1.1rem 1.4rem;
    border: 1px solid rgba(255, 255, 255, 0.06);
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.35);
    display: grid;
    gap: 0.85rem;
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    cursor: pointer;
  }

  .policy-card:hover {
    transform: translateY(-4px);
    border-color: rgba(255, 255, 255, 0.14);
    box-shadow: 0 26px 80px rgba(0, 0, 0, 0.45);
  }

  .card-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.5rem;
  }

  .pill {
    display: inline-flex;
    align-items: center;
    padding: 0.35rem 0.9rem;
    border-radius: 999px;
    font-weight: 800;
    font-size: 0.9rem;
    letter-spacing: 0.04em;
  }

  .id-pill {
    background: #0e263d;
    color: #b7d9ff;
    border: 1px solid rgba(183, 217, 255, 0.4);
  }

  .date-pill {
    background: #161f2b;
    color: #d6dde9;
    border: 1px solid rgba(255, 255, 255, 0.08);
  }

  .card-illustration {
    background: white;
    border-radius: 14px;
    border: 1px solid rgba(255, 255, 255, 0.04);
    padding: 1rem 1.05rem;
    display: grid;
    gap: 0.7rem;
  }

  .line-group {
    display: grid;
    gap: 0.45rem;
  }

  .line-group span {
    display: block;
    height: 9px;
    border-radius: 6px;
    background: rgba(0, 0, 0, 0.112);
  }

  .line-group span:nth-child(1) {
    width: 80%;
  }

  .line-group span:nth-child(2) {
    width: 65%;
  }

  .line-group span:nth-child(3) {
    width: 90%;
  }

  .line-group span:nth-child(4) {
    width: 55%;
  }

  .color-block {
    width: 58px;
    height: 58px;
    border-radius: 16px;
    background: #6cc7ff;
  }

  .card-text h3 {
    margin: 0 0 0.4rem 0;
    color: #f2f5fa;
    font-size: 1.2rem;
    text-transform: lowercase;
  }

  .card-text p {
    margin: 0;
    color: #a4aec0;
    line-height: 1.6;
    font-size: 1.05rem;
  }

  .empty {
    grid-column: 1 / -1;
    text-align: center;
    color: #8e98aa;
    border: 1px dashed rgba(255, 255, 255, 0.15);
    border-radius: 12px;
    padding: 1.5rem;
    background: rgba(255, 255, 255, 0.02);
  }

  @media (max-width: 960px) {
    .page {
      grid-template-columns: 1fr;
    }

    .sidebar {
      flex-direction: column;
      padding: 1.5rem 1.25rem;
    }

    .content {
      padding: 1.5rem 0 2.5rem;
    }

    .search-bar {
      padding: 0 1rem 1.25rem;
    }

    .search-bar .search {
      width: 100%;
    }

    .cards-grid {
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    }
  }

  @media (max-width: 600px) {
    .cards-grid {
      grid-template-columns: 1fr;
    }

    .policy-card {
      padding: 1rem 0.9rem 1.2rem;
    }
  }

  @media (min-width: 1400px) {
    .cards-grid {
      grid-template-columns: repeat(4, minmax(0, 1fr));
    }
  }
</style>
