<script>
    import { createEventDispatcher } from 'svelte';
    export let selectedEquity;
    const dispatch = createEventDispatcher();

    function close() {
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

</script>

{#if selectedEquity}
  <div
    class="modal-backdrop"
    role="button"
    tabindex="0"
    on:click={close}
    on:keydown={handleBackdropKeydown}
  >
    <div
      class="modal"
      role="dialog"
      aria-modal="true"
      tabindex="-1"
      on:click|stopPropagation
      on:keydown|stopPropagation={noop}
    >
      <button class="modal-close-btn" aria-label="Close modal" on:click={close}>
        <img src="circle-x.svg" alt="Close" />
      </button>

        {#each efItems as item}
        {#if item.id === selectedEquity}
            <div class="modal-content">
            <h2 style="color: {item.color}; margin-top: 0;">{item.label}</h2>
            <p>{item.def}</p>
            </div>
        {/if}
        {/each}
    </div>
  </div>
{/if}


<style>
  .modal-backdrop {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.5);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  .modal {
    background: white;
    border-radius: 8px;
    padding: 1.5rem;
    max-width: 600px;
    width: 90%;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    position: relative;
  }
  .modal-close-btn {
    position: absolute;
    top: 1.2rem;
    right: 1.2rem;
    background: none;
    border: none;
    z-index: 101;
    padding: 0.5rem;
    border-radius: 50%;
    transition: background-color 0.2s ease;
    cursor: pointer;
  }
  .modal-close-btn:hover {
    background-color: rgba(0, 0, 0, 0.1);
  }
  .modal-close-btn img {
    height: 1.5rem;
    width: 1.5rem;
    display: block;
  }
</style>