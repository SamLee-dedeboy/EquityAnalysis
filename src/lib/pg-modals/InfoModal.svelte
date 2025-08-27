<script>
  import { createEventDispatcher } from 'svelte';
  const dispatch = createEventDispatcher();

  function closeModal() {
    dispatch('close');
  }

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
      def: 'Recognition of historical, cultural, and social contexts that shape communities’ relationships with water resources and governance.',
      color: 'var(--equity-color-recognitional)',
    },
    {
      id: 'transformational',
      label: 'Transformational',
      def: 'Goes beyond fixing current systems to fundamentally reimagining and restructuring them. Creates entirely new approaches that center equity from the ground up, building regenerative systems that prevent inequities from occurring.',
      color: 'var(--equity-color-transformational)',
    },
  ];

  let efOpen = new Set();
  function efToggle(index) {
    if (efOpen.has(index)) {
      efOpen.delete(index);
    } else {
      efOpen.add(index);
    }
    efOpen = new Set(efOpen); // trigger reactivity
  }
</script>

<section>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet"/>
  <button
    type="button"
    class="modal-backdrop"
    on:click={closeModal}
    aria-label="Close modal"
    tabindex="0"
  ></button>

  <!-- Modal -->
  <div class="modal">
    <!-- Close Button -->
    <button class="modal-close-btn" on:click={closeModal}>
      <img src="circle-x.svg" alt="Close" />
    </button>
    <!-- Modal Wrapper -->
    <div class="ef-wrap">
      <!-- Header -->
      <header class="ef-head">
        <h2>Understanding our Equity Definitions</h2>
      </header>
      <!-- Body -->
      <div class="ef-body">
        {#each efItems as e, i}
          <div class="ef-row {efOpen.has(i) ? 'is-open' : ''}">
            {#if efOpen.has(i)}
              <div class="ef-definition">
                <p>{e.def}</p>
              </div>
              <button
                class="ef-pill"
                style="--ef-pill:{e.color}"
                on:click={() => efToggle(i)}
                aria-pressed="true"
                aria-label={'Collapse ' + e.label}
              >
                <span class="ef-pill-text">{e.label}</span>
              </button>
            {:else}
              <button
                class="ef-bar"
                style="--ef-bar:{e.color}"
                on:click={() => efToggle(i)}
                aria-pressed="false"
                aria-label={'Expand ' + e.label}
              >
                <span class="ef-bar-text">{e.label}</span>
              </button>
            {/if}
          </div>
        {/each}
      </div>
    </div>
  </div>
</section>

<style>
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
    font-family: 'Inter', sans-serif;
    display: flex;
    flex-direction: column;
    height: auto;
    min-height: unset;
    max-height: 90vh;
    overflow-y: auto;
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

  /* ---- Equity Framework (Info Modal) ---- */
  .ef-wrap {
    --ef-gap: 12px;
    --ef-row-h: 92px;
    --ef-pill-w: 240px;
    --ef-pill-r: 14px;
    --ef-bar-fg: #fff;
    --ef-bar-bg: #9aa3ad;
  }
  .ef-head {
    margin-bottom: 1rem;
  }
  .ef-head h2 {
    margin: 0 0 0.25rem 0;
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--primary-text);
    text-align: center;
  }
  .ef-head p {
    margin: 0;
    color: #475569;
    font-size: 0.95rem;
    text-align: center;
  }

  .ef-body {
    display: grid;
    gap: var(--ef-gap);
  }

  .ef-row {
    display: grid;
    grid-template-columns: 1fr;
    min-height: var(--ef-row-h);
    transition: grid-template-columns 220ms ease;
    will-change: grid-template-columns;
  }
  .ef-row.is-open {
    grid-template-columns: 1fr var(--ef-pill-w);
    align-items: stretch;
  }

  .ef-bar {
    width: 100%;
    height: var(--ef-row-h);
    background: var(--ef-bar, var(--ef-bar-bg));
    color: var(--ef-bar-fg);
    border: none;
    border-radius: 12px;
    display: grid;
    place-items: center;
    font-weight: 800;
    font-size: 1.15rem;
    letter-spacing: 0.2px;
    cursor: pointer;
    outline: none;
    transition:
      transform 140ms ease,
      box-shadow 140ms ease,
      background 160ms ease;
    box-sizing: border-box;
  }
  .ef-bar:hover {
    transform: translateY(-1px);
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08);
  }
  .ef-bar:focus-visible {
    outline: 3px solid #3b82f6;
    outline-offset: 2px;
  }
  .ef-bar-text {
    padding: 0 16px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .ef-definition {
    background: #f3f4f6;
    color: #111827;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 12px;
    height: 100%;
    box-sizing: border-box;
    display: flex;
    align-items: center;
  }
  .ef-definition p {
    margin: 0;
    line-height: 1.45;
    font-size: 0.95rem;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
  }

  .ef-pill {
    width: var(--ef-pill-w);
    height: 100%;
    background: var(--ef-pill, #9aa3ad);
    color: #fff;
    border: none;
    border-radius: var(--ef-pill-r);
    display: flex;
    align-items: center;
    justify-content: center;
    text-align: center;
    padding: 0 14px;
    font-weight: 800;
    font-size: 1rem;
    cursor: pointer;
    outline: none;
    box-shadow: 0 6px 14px rgba(0, 0, 0, 0.08);
    transition:
      box-shadow 140ms ease,
      transform 140ms ease,
      background 160ms ease;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    box-sizing: border-box;
  }
  .ef-pill:hover {
    transform: translateY(-1px);
  }
  .ef-pill:focus-visible {
    outline: 3px solid #3b82f6;
    outline-offset: 2px;
  }
  .ef-pill-text {
    pointer-events: none;
  }

  @media (max-width: 560px) {
    .ef-row.is-open {
      grid-template-columns: 1fr;
    }
    .ef-pill {
      width: 100%;
      height: 46px;
      margin-top: 8px;
      border-radius: 12px;
    }
  }
</style>
