<script>
  const exportAnalysis = () => {
    // Replace with actual export logic
    console.log("Exporting analysis...");
  };

  const openChat = () => {
    // Replace with actual chat logic
    console.log("Opening EquiFlow chat...");
  };
</script>

<style>
  .button-container { display: flex; gap: 1rem; margin-top: 1.5rem; justify-content: center; }
  .btn { font-size: 1rem; padding: 0.75rem 1.5rem; border-radius: 0.5rem; font-weight: 500; border: 2px solid #09385B; cursor: pointer; transition: background-color 0.2s ease, color 0.2s ease; }
  .btn.primary { background-color: #09385B; color: white; }
  .btn.primary:hover { background-color: #072B44; }
  .btn.secondary { background-color: #F8F8F8; color: #09385B; }
  .btn.secondary:hover { background-color: #EAEAEA; }
</style>

<div class="button-container">
  <button class="btn primary" on:click={exportAnalysis}>Export Analysis</button>
  <button class="btn secondary" on:click={openChat}>Chat with EquiFlow</button>
</div>

