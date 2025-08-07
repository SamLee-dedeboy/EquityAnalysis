<script>

  // Importing Local Modules
  import LogoBar from "../lib/LogoBar.svelte";
  import BackButton from "../lib/BackButton.svelte";
  import ReportView from "./ReportView.svelte";

  // Policies data
  import policies from "../lib/data/structured.json";
  import { currentPolicy } from '../lib/stores/currentPolicy.js';

  // Resetting currentPolicy Store Variable 
  import { onMount } from 'svelte';
    onMount(() => {
    currentPolicy.set(null);
  });

  // State Variables, Third Panel (Overview)
  let chatPanel = false;
  // Chat Logic 
  let currentDoc = null;
  let inputText = ''

</script>

<style>

  /* --- Layout --- */
  .screen-layout { position: absolute; top: 0; left: 0; right: 0; bottom: 0; display: flex; font-family: system-ui, sans-serif; background: #fff; color: #1f2937; }

  /* --- (1) Panel, Sidebar --- */
  .sidebar { width: 320px; height: 100%; padding: 24px; display: flex; flex-direction: column; border-right: 1px dotted #ccc; background: #fff; }
  .sidebar h2 { font-size: 16px; font-weight: 600; margin: 36px 0 12px; }
  /* (1.1) Upload Button*/
  .upload-button { font-size: 13px; border-radius: 6px; cursor: pointer; background: #0F3C5F; color: #fff; }
  .upload-button:hover { background: #0d304f; }
  /* (1.2) Policy Selection */
  .policies { margin-top: 24px; }
  .policies li.selected { background: #e0e7ef; color: #0F3C5F; border-radius: 8px; transition: background 0.15s; }
  .policies li.selected button { color: #0F3C5F; font-weight: 600; }

  /* --- (2) Panel, Overview --- */
  .report-panel { position: absolute; top: 0; bottom: 0; left: 320px; z-index: 500; display: flex; height: 100%; transition: width 0.3s cubic-bezier(.4,0,.2,1); }
  .report-content { flex: 1; background: #f9fafb; border-right: 1px solid #e5e7eb; box-shadow: 2px 0 8px rgba(0,0,0,0.04); display: flex; flex-direction: column; }

  /* --- (3) Panel, Chat --- */
  .chat { position: absolute; top: 0; right: 0; width: 420px; height: 100%; display: flex; flex-direction: column; background: #fff; z-index: 600; box-shadow: -2px 0 8px rgba(0,0,0,0.04); transition: left 0.3s cubic-bezier(.4,0,.2,1), width 0.3s cubic-bezier(.4,0,.2,1);}
  /* --- (3.1) Header --- */
  .chat-header { background: #0F3C5F; color: #fff; padding: 16px 32px;}
  .chat-header h2 { font-size: 18px; font-weight: 600; }
  .chat-header p { font-size: 13px; color: #cbd5e1; }
  .chat-header, .input-bar { width: 100%; box-sizing: border-box; }
  /* --- (3.2) Content --- */
  .chat-content { padding: 32px; flex: 1; overflow-y: auto; }
  .bot-avatar { aspect-ratio: 1/1; width: 2.5em; background: #0C395A; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 16px; overflow: hidden; min-width: 2.5em; }
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

        <!-- (1.2) Policies Section -->
        <div class="policies">
            <ul style="list-style: none; padding: 0; margin: 0;">
              {#each policies as policy}
                <li
                  class:selected={$currentPolicy === policy}
                  style="margin-top: 6px; border: 1px solid #e5e7eb; border-radius: 8px; background: {$currentPolicy === policy ? '#e0e7ef' : 'none'}; color: {$currentPolicy === policy ? '#0F3C5F' : '#1f2937'};"
                >
                  <button
                    type="button"
                    style="cursor:pointer; padding:12px 16px; background:none; border:none; width:100%; text-align:left; border-radius:8px; font-size:14px; color:{$currentPolicy === policy ? '#0F3C5F' : '#1f2937'}; font-weight:{$currentPolicy === policy ? '600' : '400'};"
                    on:click={() => {
                      if ($currentPolicy === policy) {
                        currentPolicy.set(null);
                        chatPanel = false;
                      } else {
                        currentPolicy.set(policy);
                        chatPanel = true;
                      }
                    }}
                  >
                    {policy.document.title}
                  </button>
                </li>
              {/each}
            </ul>
        </div>

      <!-- (1.3) Recent Documents Section -->
      <div class="recent" style="margin-top: auto; padding: 18px 20px; width: 100%;">
        <div class="recent-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
          <span style="font-weight: 600; color: #0F3C5F; font-size: 15px;">Recent Documents</span>
          <button class="clear" style="background: none; border: none; color: #0F3C5F; font-size: 13px; cursor: pointer; padding: 4px 10px; border-radius: 6px; transition: background 0.15s;">
        Clear
          </button>
        </div>
        <div style="color: #6b7280; font-size: 14px; padding-left: 2px;">
          This is a placeholder for recent documents.
        </div>
      </div>

    </aside>

    <!-- (2) Panel, Report -->
    <div class="report-panel" style="width: {chatPanel ? '50%' : 'calc(100% - 320px)'};">
        <div class="report-content">
          <!-- Report Header?
          <h1 style="text-align: center; position: absolute; width: 100%;">Equity Analysis Report</h1> -->
          <ReportView {currentDoc} />
        </div>
    </div>


    <!-- (3) Panel, Main Chat -->
    {#if chatPanel}
      <div class="chat" style="left: calc(320px + 50%); width: calc(100% - 320px - 50%);">

        <!-- (3.1) Header with Logo -->
        <div class="chat-header">
            <h2>EquiFlow AI Assistant</h2>
            <p>Intelligent Policy Equity Analysis</p>
        </div>

        <!-- (3.2) Chat Box -->
        <div class="chat-content">

          <div class="chat-messages">
            <div style="display: flex; align-items: flex-start; margin-bottom: 24px;">
              <!-- Bot Avatar Placeholder -->
              <div class="bot-avatar">
                <img src="public/botpic.png" alt="EquiFlow Logo" style="height: 1em; vertical-align: middle;">
              </div>
              <div style="background:#f1f5fb;border-radius:12px;padding:18px 20px;max-width:420px;box-shadow:0 2px 8px rgba(0,0,0,0.04);color:#1f2937;">
                <strong>Hello! I'm EquiFlow, your AI assistant for policy equity analysis.</strong>
                <ul style="margin:12px 0 0 18px;padding:0;font-size:15px;">
                  <li>Analyze documents for equity impacts across multiple dimensions</li>
                  <li>Answer detailed questions about specific policy sections</li>
                  <li>Provide actionable recommendations for improvement</li>
                  <li>Compare policies across equity frameworks</li>
                </ul>
              </div>
            </div>
          </div>

        </div>

        <!-- (3.3) Input Bar -->
        <form class="input-bar" on:submit|preventDefault={() => {}}>
            <input bind:value={inputText} placeholder="Ask about equity impact..."/>
            <button type="submit" aria-label="Send" style="height:38px; width:38px; display: flex; align-items: center; justify-content: center;">
              <!-- Other Arrow 
               &#8593; -->
              <img src="public/rhs-arrow.png" alt="Send" style="height: 1em; vertical-align: middle;">
            </button>
        </form>

      </div>
    {/if}

  </div>

</section>

