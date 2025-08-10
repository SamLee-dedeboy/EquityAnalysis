<script>
  //
</script>

<div class="info-tab-wrapper">
  <button
    class="info-tab"
    type="button"
    on:click={() => (window.location.hash = "#/info")}
  >
    <img
      class="it-icon"
      src="network.svg"
      style="filter: brightness(100);"
      alt="COEQWAL equity framework information"
    />
  </button>
</div>

<style>
  .info-tab-wrapper {
    position: fixed;
    top: 40%;
    right: 0;
    z-index: 1000;
    transform: translateY(-50%);
  }
  .info-tab {
    background: var(--primary-interactive);
    color: #fff;
    border-radius: 8px 0 0 8px;
    box-shadow: -2px 2px 8px rgba(0, 0, 0, 0.15);
    padding: 12px 16px;
    display: flex;
    align-items: center;
    cursor: pointer;
    min-width: 48px;
    min-height: 48px;
    transition: background 0.2s;
    border: none;
    outline: none;
  }
  .info-tab:hover {
    background: #1a2547;
  }
  .it-icon {
    width: 22px;
    height: 22px;
  }
</style>
