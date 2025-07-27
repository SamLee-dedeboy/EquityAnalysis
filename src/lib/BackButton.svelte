<script>
  // You can optionally pass a custom hash/route
  export let destination = '#/';
</script>

<style>

    .back-button {
        position: absolute;
        top: 0.8rem;
        right: 1rem;
        background: #0C395A;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.7em 1em 0.7em 0.7em; /* reduced left padding */
        font-size: 1.1em;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        cursor: pointer;
        z-index: 10;
        display: flex;
        align-items: center;
    }
        
    .back-button:hover { background: #1a2547; }

</style>

<button class="back-button" on:click={() => window.location.hash = destination}>
    &#8592; Back
</button>

