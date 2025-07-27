<script>

  // Importing Local Module
  import LogoBar from "../lib/LogoBar.svelte";
  import BackButton from "../lib/BackButton.svelte";
  import ReportView from "./ReportView.svelte";
  // Policies data
  import policies from "../lib/data/structured.json";

  // State Variables, Third Panel (Overview)
  let chatPanel = false;

  // Chat Logic 
  let currentDoc = null;

  // Misc.
  let inputText = ''
  
</script>

<style>

  /* --- Layout --- */
  .screen-layout { position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; font-family: system-ui, sans-serif; background: #fff; color: #1f2937; }

  /* --- (1) Panel, Sidebar --- */
  .sidebar { width: 320px; padding: 24px; display: flex; flex-direction: column; justify-content: space-between; border-right: 1px dotted #ccc; background: #fff; }
  .sidebar h2 { font-size: 16px; font-weight: 600; margin: 36px 0 12px; }
  /* (1.1) Upload Button*/
  .upload-button { font-size: 13px; padding: 8px 12px; border-radius: 6px; cursor: pointer; border: none; background: #0F3C5F; color: #fff; margin-bottom: -100px;}
  .upload-button:hover { background: #0d304f; }
  /* (1.2) Policy Selection */
  .policies {
    margin-top: 24px;
  }
  .policies li.selected { background: #e0e7ef; color: #0F3C5F; border-radius: 8px; transition: background 0.15s; }
  .policies li.selected button { color: #0F3C5F; font-weight: 600; }
  /* (1.3) Recent Documents */
  .recent { font-size: 13px; }
  .recent-header { display: flex; justify-content: space-between; margin-bottom: 8px; color: #444; }
  .clear { background: none; color: #0F3C5F; border: none; font-size: 12px; cursor: pointer; }

  /* --- (2) Panel, Overview --- */
  .report-panel { position: absolute; top: 0; bottom: 0; left: 320px; width: 640px; /* Increased width from 480px to 640px */ z-index: 500; display: flex; height: 100%; }
  .report-content { flex: 1; width: 100%; height: 100%; background: #f9fafb; border-right: 1px solid #e5e7eb; box-shadow: 2px 0 8px rgba(0,0,0,0.04); display: flex; flex-direction: column; }
  .report-panel { /* NOTE: Animation */
    transition: width 0.3s cubic-bezier(.4,0,.2,1);
  }

  /* --- (3) Panel, Chat --- */
  .chat { width: 100%; position: absolute; top: 0; right: 0; width: 420px; height: 100%; display: flex; flex-direction: column; min-width: 0; background: #fff; z-index: 600; box-shadow: -2px 0 8px rgba(0,0,0,0.04); transition: right 0.3s cubic-bezier(.4,0,.2,1); }
  /* --- (3.1) Header --- */
  .chat-header { background: #0F3C5F; color: #fff; padding: 16px 32px;}
  .chat-header h2 { font-size: 18px; font-weight: 600; }
  .chat-header p { font-size: 13px; color: #cbd5e1; }
  .chat-header, .input-bar { width: 100%; box-sizing: border-box; }
  /* --- (3.2) Content --- */
  .chat-content { padding: 32px; flex: 1; overflow-y: auto; }
  /* --- (3.3) Input Bar --- */
  .input-bar { display: flex; padding: 16px 32px; border-top: 1px solid #ddd; gap: 12px; align-items: center; background: #fff; }
  .input-bar input { flex: 1; border: 1px solid #ccc; padding: 10px 16px; border-radius: 999px; font-size: 14px; }
  .input-bar input:focus { outline: none; border-color: #0F3C5F; }
  .input-bar button { background: #0F3C5F; color: #fff; border: none; padding: 10px 16px; border-radius: 999px; font-size: 18px; cursor: pointer; }
  .input-bar button:hover { background: #0d304f; }


</style>

<section>

  <div class="screen-layout">
    
    <!-- (i) Sidebar Logo Overlay -->
    <div style="position:absolute;top:0;left:0;width:320px;z-index:100;">
      <LogoBar />
    </div>
    <!-- (ii) Top Right Back Button -->
    <div style="position:absolute;top:4px;right:4px;z-index:1000; pointer-events: none; width:320px; display:flex; justify-content:flex-end;">
      <div style="pointer-events: auto;">
        <BackButton />
      </div>
    </div>

    <!-- (1) Panel, Sidebar -->
    <aside class="sidebar">

      <div class="sidebar-top">
        <h2>Document Analysis</h2>
        <!-- (1.1) Upload Button -->
          <label class="upload-button" style="display:flex;align-items:center;gap:6px;padding:8px 10px; min-width:100%; width:100%; justify-content:center; cursor:pointer;">
            <img src="public/docup-btn.png" alt="Upload" style="width:18px;height:18px;" />
            <span style="white-space:nowrap;">Upload (PDF)</span>
            <input
              type="file"
              accept=".txt,.pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
              style="display:none"
              on:change="{(e) => { /* handle file upload here */ }}"
            />
          </label>
      </div>

      <!-- (1.2) Policies Section -->
      <div class="policies">
        <ul style="list-style: none; padding: 0; margin: 0;">
          {#each policies as policy}
        <li class:selected={currentDoc === policy} style="margin-bottom: 6px; border: 1px solid #e5e7eb; border-radius: 8px;">
          <button
            type="button"
            style="cursor:pointer; padding:12px 16px; background:none; border:none; width:100%; text-align:left; border-radius:8px; font-size:14px; color:#1f2937;"
            on:click={() => currentDoc = policy}
          >
            {policy.document.filename}
          </button>
        </li>
          {/each}
        </ul>
      </div>

      <!-- (1.3) Recent Documents Section -->
      <div class="recent">
        <div class="recent-header">
          <span>Recent Documents (Hardcoded)</span>
          <button class="clear">Clear</button>
        </div>
        This is a placeholder for recent documents.
      </div>

    </aside>

    <!-- (2) Panel, Report -->
    <div class="report-panel" style="width: {chatPanel ? '640px' : 'calc(100% - 320px)'};">
        <div class="report-content">
            <h1 style="text-align: center">Report-Style View</h1>
            <ReportView {currentDoc} />
        </div>
    </div>


    <!-- (3) Panel, Main Chat -->
    {#if chatPanel}
      <div class="chat" style="left: calc(320px + 640px); width: calc(100% - 320px - 640px);">

        <!-- (3.1) Header with Logo -->
        <div class="chat-header">
            <h2>EquiFlow AI Assistant</h2>
            <p>Intelligent Policy Equity Analysis</p>
        </div>

        <!-- (3.2) Chat Box -->
        <div class="chat-content">
        </div>

        <!-- (3.3) Input Bar -->
        <form class="input-bar" on:submit|preventDefault={() => {}}>
            <input bind:value={inputText} placeholder="Ask about equity impact..."/>
            <button type="submit" aria-label="Send" style="height:38px; width:38px; display: flex; align-items: center; justify-content: center;">
              &#8593;
            </button>
        </form>

      </div>
    {/if}

  </div>

  <!-- (Dev.) Toggle Button for thirdPanel -->
  <button
    style="position:fixed;bottom:86px;right:24px;z-index:999;background:#e0e7ef;color:#0F3C5F;border:1px solid #0F3C5F;border-radius:999px;padding:10px 20px;font-size:14px;cursor:pointer;"
    on:click={() => chatPanel = !chatPanel}>
    Toggle Chat Panel (Dev)
  </button>

</section>

