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

<div class="button-container">
  <button class="btn primary" on:click={exportAnalysis}>Export Analysis</button>
  <button class="btn secondary" on:click={openChat}>Chat with EquiFlow</button>
</div>

<style>
  .button-container {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
    justify-content: center;
  }
  .btn {
    font-size: 1rem;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    font-weight: 500;
    border: 2px solid #09385b;
    cursor: pointer;
    transition:
      background-color 0.2s ease,
      color 0.2s ease;
  }
  .btn.primary {
    background-color: #09385b;
    color: white;
  }
  .btn.primary:hover {
    background-color: #072b44;
  }
  .btn.secondary {
    background-color: #f8f8f8;
    color: #09385b;
  }
  .btn.secondary:hover {
    background-color: #eaeaea;
  }
</style>
