<script>
  // Importing Local Modules
  import LogoBar from "../lib/LogoBar.svelte";
  import BackButton from "../lib/BackButton.svelte";
  import ReportView from "./_ReportView.svelte";
  import ChatPanel from "../lib/ChatPanel.svelte";

  // Policies data
  import policies from "../lib/data/structured.json";
  import { currentPolicy } from "../lib/stores/currentPolicy.js";
  import { slide } from "svelte/transition";

  // Resetting currentPolicy Store Variable
  import { onMount } from "svelte";
  import AnalysisView from "./AnalysisView.svelte";
  import EmptyPage from "../lib/EmptyPage.svelte";
  onMount(() => {
    currentPolicy.set(null);
  });

  // State Variables, Third Panel (Overview)
  let chatPanel = false;
  // Chat Logic
  let currentDoc = null;
</script>

<section>
  <div class="screen-layout">
    <!-- (i) Sidebar Logo Overlay -->
    <div style="position:absolute;top:0;left:0;width:320px;z-index:100;">
      <LogoBar />
    </div>
    <!-- (ii) Top Right Back Button -->

    <!-- (1) Panel, Sidebar -->
    <aside class="sidebar">
      <!-- <div
        style="position:absolute;top:4px;right:4px;z-index:1000; pointer-events: none; width:320px; display:flex; justify-content:flex-end;"
      >
        <div style="pointer-events: auto;">
          <BackButton />
        </div>
      </div> -->
      <!-- <h2>Document Analysis</h2> -->
      <!-- (1.1) Upload Button -->
      <label
        class="upload-button"
        style="display:flex;align-items:center;gap:6px;padding:8px 10px; min-width:100%; width:100%; justify-content:center; cursor:pointer;"
      >
        <img
          src="public/docup-btn.png"
          alt="Upload"
          style="width:18px;height:18px;"
        />
        <span style="white-space:nowrap;">Upload (PDF)</span>
        <input
          type="file"
          accept=".txt,.pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
          style="display:none"
          on:change={(e) => {
            /* handle file upload here */
          }}
        />
      </label>

      <!-- (1.2) Policies Section -->
      <div class="policies">
        <ul style="list-style: none; padding: 0; margin: 0;">
          {#each policies as policy}
            <li
              class:selected={$currentPolicy === policy}
              style="margin-top: 6px; border: 1px solid #e5e7eb; border-radius: 8px; background: {$currentPolicy ===
              policy
                ? '#e0e7ef'
                : 'none'}; color: {$currentPolicy === policy
                ? '#0F3C5F'
                : '#1f2937'};"
            >
              <button
                type="button"
                style="cursor:pointer; padding:12px 16px; background:none; border:none; width:100%; text-align:left; border-radius:8px; font-size:14px; color:{$currentPolicy ===
                policy
                  ? '#0F3C5F'
                  : '#1f2937'}; font-weight:{$currentPolicy === policy
                  ? '600'
                  : '400'};"
                on:click={() => {
                  if ($currentPolicy === policy) {
                    currentPolicy.set(null);
                    chatPanel = false;
                  } else {
                    currentPolicy.set(policy);
                    // chatPanel = true;
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
      <div
        class="recent"
        style="margin-top: auto; padding: 18px 20px; width: 100%;"
      >
        <div
          class="recent-header"
          style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;"
        >
          <span style="font-weight: 600; color: #0F3C5F; font-size: 15px;"
            >Recent Documents</span
          >
          <button
            class="clear"
            style="background: none; border: none; color: #0F3C5F; font-size: 13px; cursor: pointer; padding: 4px 10px; border-radius: 6px; transition: background 0.15s;"
          >
            Clear
          </button>
        </div>
        <div style="color: #6b7280; font-size: 14px; padding-left: 2px;">
          This is a placeholder for recent documents.
        </div>
      </div>
    </aside>

    <!-- (2) Panel, Report -->
    <div class="report-chat-container">
      <!-- Chat Toggle Button -->
      <button
        class="chat-toggle-btn"
        on:click={() => (chatPanel = !chatPanel)}
        title={chatPanel ? "Close Chat" : "Open Chat"}
      >
        <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
          {#if chatPanel}
            <!-- Close icon (X) -->
            <path
              d="M18 6L6 18M6 6l12 12"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
          {:else}
            <!-- Chat bubble icon -->
            <path
              d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"
            />
          {/if}
        </svg>
      </button>

      <div class="report-panel">
        <div class="report-content">
          <!-- Report Header?
          <h1 style="text-align: center; position: absolute; width: 100%;">Equity Analysis Report</h1> -->
          <!-- <ReportView {currentDoc} /> -->
          {#if !$currentPolicy?.document?.title}
            <EmptyPage></EmptyPage>
          {:else}
            <AnalysisView />
          {/if}
        </div>
      </div>

      <!-- (3) Panel, Main Chat -->
      {#if chatPanel}
        <div class="chat-panel" in:slide={{ axis: "x" }}>
          <ChatPanel></ChatPanel>
        </div>
      {/if}
    </div>
  </div>
</section>

<style>
  /* --- Layout --- */
  .screen-layout {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    display: flex;
    font-family: system-ui, sans-serif;
    background: #fff;
    color: #1f2937;
  }

  /* --- (1) Panel, Sidebar --- */
  .sidebar {
    width: 320px;
    height: 100%;
    padding: 24px;
    padding-top: 7rem;
    display: flex;
    flex-direction: column;
    border-right: 1px dotted #ccc;
    background: #fff;
    position: relative;
  }
  .sidebar h2 {
    font-size: 16px;
    font-weight: 600;
    margin: 36px 0 12px;
  }
  /* (1.1) Upload Button*/
  .upload-button {
    font-size: 13px;
    border-radius: 6px;
    cursor: pointer;
    background: #0f3c5f;
    color: #fff;
  }
  .upload-button:hover {
    background: #0d304f;
  }
  /* (1.2) Policy Selection */
  .policies {
    margin-top: 24px;
  }
  .policies li.selected {
    background: #e0e7ef;
    color: #0f3c5f;
    border-radius: 8px;
    transition: background 0.15s;
  }
  .policies li.selected button {
    color: #0f3c5f;
    font-weight: 600;
  }

  /* --- (2) Panel, Overview --- */

  .report-chat-container {
    display: flex;
    width: 100%;
  }
  .report-panel {
    display: flex;
    flex-grow: 1;
    min-width: 65%;
    overflow: auto;
  }
  .chat-panel {
  }
  .report-content {
    flex: 1;
    background: #f9fafb;
    border-right: 1px solid #e5e7eb;
    box-shadow: 2px 0 8px rgba(0, 0, 0, 0.04);
    display: flex;
    flex-direction: column;
  }

  /* --- Chat Toggle Button --- */
  .chat-toggle-btn {
    position: absolute;
    top: 24px;
    right: 24px;
    background: #0f3c5f;
    color: #fff;
    border: none;
    border-radius: 50%;
    width: 40px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: background 0.15s;
    z-index: 100;
  }
  .chat-toggle-btn:hover {
    background: #0d304f;
  }
</style>
