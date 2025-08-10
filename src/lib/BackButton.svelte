<script>
  // You can optionally pass a custom hash/route
  export let destination = "#/";
</script>

<button
  class="back-button"
  on:click={() => (window.location.hash = destination)}
>
  <img
    src="arrow-left.svg"
    alt="Back"
    style="width: 1.5rem; height: 1.5rem; "
  />
  Back
</button>

<style>
  .back-button {
    position: absolute;
    top: 0.8rem;
    right: 1rem;
    background: var(--primary-interactive);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.7em 1em 0.7em 0.7em; /* reduced left padding */
    font-size: 1.1em;
    font-family: "Inter", sans-serif;
    font-weight: 500;
    cursor: pointer;
    z-index: 10;
    display: flex;
    display: inline-flex;
    gap: 0.5rem;
    align-items: center;
    transition: background 0.2s;
  }

  .back-button:hover {
    background: #1a2547;
  }
</style>
