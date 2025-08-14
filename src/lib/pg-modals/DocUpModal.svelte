<script>

    import { createEventDispatcher } from 'svelte';
    const dispatch = createEventDispatcher();
    function closeModal() {
        dispatch('close');
    }
    
</script>



<section>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet"/>

    <!-- Backdrop -->
    <button
      type="button"
      class="modal-backdrop"
      on:click={closeModal}
      aria-label="Close modal"
      tabindex="0"
    ></button>
    <div class="modal">
        <!-- Close Button -->
        <button class="modal-close-btn" on:click={closeModal}>    
            <img src="circle-x.svg" alt="Close" />
        </button>
        <!-- Modal Wrapper -->
        <div class="ef-wrap">
            <!-- Header -->
            <header class="ef-head">
                <p>Upload a policy document and get an interactive, equity-focused analysis with actionable insights, powered by the Equity Framework. 
                    Visualize impacts, explore key metrics, and interact with tailored recommendations-- all in one place.</p>
            </header>
            <!-- Stepper -->
            <div class="eq-stepper" role="list" aria-label="Analysis steps">
            <div class="eq-step" role="listitem">
                <div class="eq-dot">1</div>
                <div class="eq-label">Upload Policy</div>
            </div>

            <div class="eq-arrow" aria-hidden="true">
                <svg viewBox="0 0 64 16" width="64" height="16">
                <line x1="0" y1="8" x2="54" y2="8" />
                <polyline points="48,2 60,8 48,14" />
                </svg>
            </div>

            <div class="eq-step" role="listitem">
                <div class="eq-dot">2</div>
                <div class="eq-label">AI Equity Analysis</div>
            </div>

            <div class="eq-arrow" aria-hidden="true">
                <svg viewBox="0 0 64 16" width="64" height="16">
                <line x1="0" y1="8" x2="54" y2="8" />
                <polyline points="48,2 60,8 48,14" />
                </svg>
            </div>

            <div class="eq-step" role="listitem">
                <div class="eq-dot">3</div>
                <div class="eq-label">Visualize &amp; Explore</div>
            </div>

            <div class="eq-arrow" aria-hidden="true">
                <svg viewBox="0 0 64 16" width="64" height="16">
                <line x1="0" y1="8" x2="54" y2="8" />
                <polyline points="48,2 60,8 48,14" />
                </svg>
            </div>

            <div class="eq-step" role="listitem">
                <div class="eq-dot">4</div>
                <div class="eq-label">Download &amp; Share</div>
            </div>
            </div>
            <!-- Upload Area -->
            <div class="upload-area">
                <!-- Upload Context -->
                <p> No policy uploaded yet.
                    <br> Upload a PDF policy document to begin analysis
                </p>
                <!-- Placeholder Button -->
                <button on:click={() => (window.location.hash = "#/tool")}>Upload Policy</button>
            </div>
            <!-- Recent Documents Section (Static) -->
            <div class="recent-documents" style="margin-top:2rem;">
              <h3 style="font-size:1rem; margin-bottom:0.5rem; text-align:left;">Recent Documents</h3>
              <ul style="list-style:none; padding:0; margin:0;">
              <li style="padding:0.4rem 0; display:flex; align-items:center; gap:0.5rem;">
                <span style="flex:1;">Equity_Policy_2024.pdf</span>
                <button style="background:none; border:none; color:var(--primary-interactive); cursor:pointer; font-size:0.95em;">Open</button>
              </li>
              <li style="padding:0.4rem 0; display:flex; align-items:center; gap:0.5rem;">
                <span style="flex:1;">Community_Health_Review.pdf</span>
                <button style="background:none; border:none; color:var(--primary-interactive); cursor:pointer; font-size:0.95em;">Open</button>
              </li>
              <li style="padding:0.4rem 0; display:flex; align-items:center; gap:0.5rem;">
                <span style="flex:1;">Housing_Equity_Analysis.pdf</span>
                <button style="background:none; border:none; color:var(--primary-interactive); cursor:pointer; font-size:0.95em;">Open</button>
              </li>
              </ul>
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
      width: auto;
      min-width: 340px;
      max-width: 95vw;
      min-height: 0;
      z-index: 100;
      box-shadow: 0 0 32px rgba(0, 0, 0, 0.28);
      font-family: 'Inter', sans-serif;
      display: flex;
      flex-direction: column;
      align-items: stretch;
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
    /* --- Header --- */
    .ef-head {
      margin-bottom: 1rem;
    }
    .ef-head p {
      margin: 0;
      color: #000000;
      font-size: 0.95rem;
      text-align: center;
    }
    /* --- Upload Area --- */
    .upload-area {
      background-color: var(--primary-background);
      border: 2px dashed grey;
      border-radius: 8px;
      padding: 2rem;
      margin-top: 1.5rem;
      text-align: center;
    }
    .upload-area p {
      text-align: center;
    }
    .upload-area button {
      background: var(--primary-interactive);
      color: white;
      margin-top: 1rem;
      display: block;
      margin-left: auto;
      margin-right: auto;
      border-radius: 8px;
      padding: 0.5rem 1rem;
      font-size: 1.1em;
      font-weight: 500;
      border: none;
      cursor: pointer;
      transition: background 0.2s;
      box-shadow: none;
      outline: none;
    }
    .upload-area button:hover {
      background-color: var(--primary-interactive-hover);
      color: white;
    }

    /* Stepper */
    .eq-stepper {
      --dot-size: 44px;
      --dot-bg: #c9d4de;
      --dot-border: #657b8c;
      --text: #111827;
      --arrow: #000;
      --gap: 28px;
      --font: 'Inter', sans-serif;
    }
    .eq-stepper {
      display: flex;
      align-items: center;
      justify-content: center;
      gap: var(--gap);
      flex-wrap: wrap;
      font-family: var(--font);
    }
    .eq-step {
      display: grid;
      grid-template-rows: auto auto;
      justify-items: center;
      row-gap: 8px;
      min-width: max-content;
    }
    .eq-dot {
      width: var(--dot-size);
      height: var(--dot-size);
      border-radius: 999px;
      background: var(--dot-bg);
      border: 2px solid var(--dot-border);
      display: grid;
      place-items: center;
      font-weight: 700;
      color: #0b2239;
      line-height: 1;
      font-size: 1rem;
    }
    .eq-label {
      color: var(--text);
      font-size: 0.95rem;
      text-align: center;
      white-space: nowrap;
    }
    .eq-arrow svg {
      display: block;
    }
    .eq-arrow line,
    .eq-arrow polyline {
      stroke: var(--arrow);
      stroke-width: 2;
      fill: none;
      stroke-linecap: round;
      stroke-linejoin: round;
    }
    @media (max-width: 560px) {
      .eq-stepper {
        gap: 18px;
      }
      .eq-label {
        font-size: 0.9rem;
      }
      .eq-arrow svg {
        width: 48px;
      }
    }
</style>