<script>
  import { onMount, tick } from 'svelte';
  import { slide } from 'svelte/transition';

  // Importing Local Modules
  import LogoBar from '../lib/LogoBar.svelte';
  import ChatPanel from '../lib/ChatPanel.svelte';

  // Importing View Components
  import EmptyPage from '../lib/EmptyPage.svelte';
  import AnalysisView from './AnalysisView.svelte'; // The main report view component

  // Importing Stores
  import { server_address } from '../constants'; // Assumed to be "http://localhost:8000"
  import {
    currentPolicy,
    fetchPolicies,
    fetchPolicyDataById,
  } from '../lib/stores/currentPolicy.js';

  // --- State Variables ---
  let policies = []; // Dynamically loaded and updated from API
  let isUploading = false; // True if file upload/VS creation is in progress
  let currentSessionId = null; // Stores the Session ID (which is also the document_id for user uploads)
  let analysisPollingTimer = null; // Timer for polling analysis status
  let analysisResultFetched = false; // Flag to prevent multiple fetches/displays of the full analysis JSON
  let currentDoc = null; // Full policy object for AnalysisView to render

  const ANALYSIS_POLLING_INTERVAL_MS = 5000; // Poll every 5 seconds for analysis status

  // --- Lifecycle Hook ---
  onMount(async () => {
    currentPolicy.set(null); // Clear any previous selection when component mounts
    currentDoc = null;
    currentSessionId = null;
    analysisResultFetched = false;
    if (analysisPollingTimer) clearInterval(analysisPollingTimer);

    await loadInitialPolicies(); // Load existing policies from API (DB + preprocessed)
  });

  // Function to load policies from the backend (both preprocessed and user-uploaded)
  async function loadInitialPolicies() {
    try {
      policies = await fetchPolicies();
      policies = policies.map(p => ({
        ...p,
        analysis_status:
          p.analysis_status ||
          (p.source === 'preprocessed' ? 'completed' : 'unknown'),
        analysis_error: p.analysis_error || null,
      }));
      console.log('Loaded policies:', policies);
    } catch (err) {
      console.error('Network error loading initial policies list:', err);
    }
  }

  // Function to load a specific policy's full data (either preprocessed or user-uploaded)
  async function loadPolicyData(policyId) {
    // Reset fetched flag when a new policy is clicked to ensure fresh display for a NEW policy.
    if ($currentPolicy?.id !== policyId) {
      analysisResultFetched = false; // Reset only if a different policy is being selected
    }

    const selectedPolicy = policies.find(p => p.id === policyId);
    if (selectedPolicy) {
      currentPolicy.set(selectedPolicy); // Set initial metadata to the store
      currentDoc = selectedPolicy; // Also update currentDoc immediately

      if (analysisPollingTimer) clearInterval(analysisPollingTimer);
      analysisPollingTimer = null;

      // Handle completed/failed/preprocessed documents by fetching full data
      if (
        selectedPolicy.analysis_status === 'completed' ||
        selectedPolicy.analysis_status === 'failed' || // Even failed ones, we load their full (failed) data if available
        selectedPolicy.source === 'preprocessed'
      ) {
        currentSessionId = policyId; // Ensure currentSessionId is set for chat
        // Await the full data fetch and update of currentPolicy and currentDoc
        await displayAnalysisResult(policyId);
      } else if (selectedPolicy.source === 'user') {
        // If it's an in-progress user doc, set currentSessionId and initiate polling
        currentSessionId = policyId;
        analysisPollingTimer = setInterval(
          () => pollAnalysisStatus(currentSessionId),
          ANALYSIS_POLLING_INTERVAL_MS
        );
        pollAnalysisStatus(currentSessionId); // Initial immediate poll
      } else {
        currentSessionId = null; // No active session for preprocessed or other types (though preprocessed now sets it)
      }
    } else {
      console.warn(`Policy with ID ${policyId} not found in the list.`);
      currentPolicy.set(null);
      currentDoc = null; // Clear currentDoc
      currentSessionId = null; // Clear currentSessionId
    }
    chatPanel = true; // Open chat panel when a document is selected/loaded
  }

  // handleFileUpload function for the upload button
  async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // --- Reset all relevant state for a new upload session ---
    if (analysisPollingTimer) clearInterval(analysisPollingTimer);
    currentSessionId = null;
    analysisResultFetched = false;
    currentPolicy.set(null); // Clear any currently selected policy in the store
    currentDoc = null; // Clear currentDoc on new upload start
    isUploading = true; // Set upload state to true for UI feedback

    const formData = new FormData();
    formData.append('file', file);

    // Add a temporary entry to the policies list immediately to show processing in sidebar
    const tempId = `temp-${Date.now()}`; // Temporary ID for optimistic update
    const tempPolicyEntry = {
      id: tempId,
      document: {
        title: file.name,
        filename: file.name,
        size_kb: Math.round(file.size / 1024),
        upload_date_utc: new Date().toISOString(),
      },
      source: 'user',
      analysis_status: 'pending', // Initial status for this new entry
      analysis_error: null, // No error yet
    };
    policies = [tempPolicyEntry, ...policies]; // Add to top of sidebar list
    currentPolicy.set(tempPolicyEntry); // Select this newly uploaded/processing entry
    currentDoc = tempPolicyEntry; // Set currentDoc for optimistic update

    try {
      const response = await fetch(`${server_address}/upload`, {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();

      if (response.ok && result.success) {
        currentSessionId = result.session_id; // Get the real session ID from backend

        policies = policies.map(p =>
          p.id === tempId
            ? {
                ...p,
                id: currentSessionId,
                analysis_status: result.analysis_status,
              }
            : p
        );
        // Also update currentPolicy with the real ID, so ReportView uses the correct ID for polling
        currentPolicy.update(p => ({
          ...p,
          id: currentSessionId,
          analysis_status: result.analysis_status,
        }));
        currentDoc = {
          ...currentDoc,
          id: currentSessionId,
          analysis_status: result.analysis_status,
        }; // <--- Update currentDoc with real ID/status

        // Start polling for analysis status
        analysisPollingTimer = setInterval(
          () => pollAnalysisStatus(currentSessionId),
          ANALYSIS_POLLING_INTERVAL_MS
        );
        pollAnalysisStatus(currentSessionId); // Initial immediate poll
        chatPanel = true;
      } else {
        console.error('Upload failed:', result.message || 'Unknown error');
        policies = policies.filter(p => p.id !== tempId); // Remove if upload failed at this stage
        currentPolicy.set(null);
        currentDoc = null; // Clear selection on failure
      }
    } catch (error) {
      console.error('Upload network error:', error);
      policies = policies.map(p =>
        p.id === tempId
          ? {
              ...p,
              analysis_status: 'failed',
              analysis_error: 'Network error during upload.',
            }
          : p
      );
      currentPolicy.update(p => ({
        ...p,
        analysis_status: 'failed',
        analysis_error: 'Network error during upload.',
      }));
      currentDoc = {
        ...currentDoc,
        analysis_status: 'failed',
        analysis_error: 'Network error during upload.',
      };
    } finally {
      isUploading = false; // Reset upload state
    }
  }

  // Polling function for analysis status (updates sidebar and ReportView state)
  async function pollAnalysisStatus(sessionId) {
    if (analysisResultFetched) {
      clearInterval(analysisPollingTimer);
      analysisPollingTimer = null;
      return;
    }

    try {
      const response = await fetch(
        `${server_address}/get_analysis_status/${sessionId}`
      );
      if (!response.ok) {
        console.error('Polling error:', response.status, await response.text());
        clearInterval(analysisPollingTimer);
        analysisPollingTimer = null;
        // Update the specific policy entry in 'policies' array to reflect failure
        policies = policies.map(p =>
          p.id === sessionId
            ? {
                ...p,
                analysis_status: 'failed',
                analysis_error: 'Failed to get status.',
              }
            : p
        );
        currentPolicy.update(p => ({
          ...p,
          analysis_status: 'failed',
          analysis_error: 'Failed to get status.',
        }));
        currentDoc = {
          ...currentDoc,
          analysis_status: 'failed',
          analysis_error: 'Failed to get status.',
        }; // Update currentDoc
        return;
      }

      const result = await response.json();
      const newStatus = result.analysis_status;

      // Update the specific policy entry in 'policies' array and currentPolicy store
      policies = policies.map(p =>
        p.id === sessionId
          ? {
              ...p,
              analysis_status: newStatus,
              analysis_error: result.analysis_error,
            }
          : p
      );
      currentPolicy.update(p => ({
        ...p,
        analysis_status: newStatus,
        analysis_error: result.analysis_error,
      }));
      currentDoc = {
        ...currentDoc,
        analysis_status: newStatus,
        analysis_error: result.analysis_error,
      }; // Update currentDoc

      if (newStatus === 'completed') {
        clearInterval(analysisPollingTimer);
        analysisPollingTimer = null;
        await displayAnalysisResult(sessionId);
      } else if (newStatus === 'failed') {
        clearInterval(analysisPollingTimer);
        analysisPollingTimer = null;
        console.error(
          `Analysis for ${sessionId} failed: ${result.analysis_error}`
        );
      }
    } catch (error) {
      console.error('Network error during analysis status polling:', error);
      clearInterval(analysisPollingTimer);
      analysisPollingTimer = null;
      policies = policies.map(p =>
        p.id === sessionId
          ? {
              ...p,
              analysis_status: 'failed',
              analysis_error: 'Network error.',
            }
          : p
      );
      currentPolicy.update(p => ({
        ...p,
        analysis_status: 'failed',
        analysis_error: 'Network error.',
      }));
      currentDoc = {
        ...currentDoc,
        analysis_status: 'failed',
        analysis_error: 'Network error.',
      }; // Update currentDoc
    }
  }

  // Function to display the full JSON analysis result once completed
  async function displayAnalysisResult(sessionId) {
    if (
      $currentPolicy?.id === sessionId &&
      $currentPolicy?.overall_analysis_by_perspective
    ) {
      console.log(
        'Full analysis result already present in store for this session. Skipping API call.'
      );
      analysisResultFetched = true; // Mark as fetched since we have it
      return;
    }

    analysisResultFetched = false; // Always reset before potentially fetching new data

    try {
      // Use fetchPolicyDataById to get the full policy data (handles both user and preprocessed)
      const fullPolicyData = await fetchPolicyDataById(sessionId);

      if (
        fullPolicyData.analysis_status === 'completed' ||
        fullPolicyData.analysis_status === 'failed'
      ) {
        policies = policies.map(p => {
          if (p.id === sessionId) {
            return {
              ...p,
              ...fullPolicyData, // Merge full data including overall_analysis_by_perspective
            };
          }
          return p;
        });
        await tick(); // Ensure DOM updates are pending before setting full data
        currentPolicy.set(fullPolicyData); // Set the full data to the store
        currentDoc = fullPolicyData; // Update currentDoc with full data
        currentSessionId = sessionId;
        analysisResultFetched = true; // Mark as fetched after successful full load
        console.log(
          'Analysis completed. Chat should be active for session:',
          currentSessionId
        );
      } else {
        console.error(
          "Analysis result was not 'completed' or 'failed' when fetched:",
          fullPolicyData.analysis_status
        );
        analysisResultFetched = false; // Reset if status is not final
        currentPolicy.update(p => ({
          ...p,
          analysis_status: fullPolicyData.analysis_status,
          analysis_error:
            fullPolicyData.analysis_error ||
            'Unexpected status when retrieving full report.',
        }));
        currentDoc = {
          ...currentDoc,
          analysis_status: fullPolicyData.analysis_status,
          analysis_error:
            fullPolicyData.analysis_error ||
            'Unexpected status when retrieving full report.',
        };
      }
    } catch (error) {
      console.error('Error fetching analysis result:', error);
      analysisResultFetched = false;
      // Ensure currentPolicy and currentDoc reflect the failure
      currentPolicy.update(p => ({
        ...p,
        analysis_status: 'failed',
        analysis_error:
          error.message || 'Network error while fetching analysis report.',
      }));
      currentDoc = {
        ...currentDoc,
        analysis_status: 'failed',
        analysis_error:
          error.message || 'Network error while fetching analysis report.',
      };
    }
  }

  // Handle End Session triggered from ChatPanel
  async function handleEndSessionFromChat() {
    if (!currentSessionId) return;

    if (analysisPollingTimer) {
      clearInterval(analysisPollingTimer);
      analysisPollingTimer = null;
    }
    isUploading = false;
    analysisResultFetched = false;

    policies = policies.filter(p => p.id !== currentSessionId);
    currentPolicy.set(null);
    currentDoc = null;
    currentSessionId = null;

    chatPanel = false;
  }

  // State Variables, Third Panel (Overview) - Original position
  let chatPanel = false;
</script>

<section>
  <div class="screen-layout">
    <!-- (i) Sidebar Logo Overlay -->
    <div style="position:absolute;top:0;left:0;width:320px;z-index:100;">
      <LogoBar />
    </div>

    <!-- (1) Panel, Sidebar -->
    <aside class="sidebar">
      <!-- (1.1) Upload Button -->
      <label
        class="upload-button"
        class:uploading={isUploading}
        style="display:flex;align-items:center;gap:6px;padding:8px 10px; min-width:100%; width:100%; justify-content:center; cursor:pointer;"
      >
        <img src="docup.svg" alt="Upload" style="width:18px;height:18px;" />
        <span style="white-space:nowrap;">
          {#if isUploading}
            Uploading...
          {:else}
            Upload
          {/if}
        </span>
        <input
          type="file"
          accept=".txt,.pdf,.docx,.html,.md,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,text/plain"
          style="display:none"
          on:change={handleFileUpload}
          disabled={isUploading}
        />
      </label>

      <!-- (1.2) Policies Section -->
      <div class="policies">
        <ul style="list-style: none; padding: 0; margin: 0;">
          {#each policies as policy (policy.id)}
            <li
              class:selected={$currentPolicy?.id === policy.id}
              style="margin-top: 6px; border: 1px solid #e5e7eb; border-radius: 8px;
                     background: {$currentPolicy?.id === policy.id
                ? '#e0e7ef'
                : 'none'};
                     color: {$currentPolicy?.id === policy.id
                ? '#0F3C5F'
                : '#1f2937'};"
            >
              <button
                type="button"
                style="cursor:pointer; padding:12px 16px; background:none; border:none; width:100%; text-align:left; border-radius:8px; font-size:14px;
                       color:{$currentPolicy?.id === policy.id
                  ? '#0F3C5F'
                  : '#1f2937'};
                       font-weight:{$currentPolicy?.id === policy.id
                  ? '600'
                  : '400'};
                       display:flex; justify-content:space-between; align-items:center;"
                on:click={() => loadPolicyData(policy.id)}
              >
                <!-- Displays filename, then title, then ID -->
                {policy.document?.filename ||
                  policy.document?.title ||
                  policy.id}

                {#if policy.source === 'user'}
                  <span
                    class="analysis-status-dot"
                    class:status-pending={policy.analysis_status ===
                      'pending' ||
                      policy.analysis_status === 'waiting_vs_processing' ||
                      policy.analysis_status === 'analysis_generating'}
                    class:status-completed={policy.analysis_status ===
                      'completed'}
                    class:status-failed={policy.analysis_status === 'failed'}
                    title="Analysis Status: {policy.analysis_status?.replace(
                      /_/g,
                      ' '
                    ) || 'Unknown'}"
                    style="width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-left: 8px; flex-shrink: 0;"
                  ></span>
                {/if}
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
            on:click={async () => {
              // This clears frontend list of user-uploaded docs.
              // Backend cleanup for specific user data would require explicit API calls for each doc.
              policies = policies.filter(p => p.source === 'preprocessed');
              currentPolicy.set(null); // Deselect any policy
              currentSessionId = null; // Clear active session ID if it was a user upload
              analysisStatus = null; // Reset analysis status display
              analysisResultFetched = false;
              if (analysisPollingTimer) {
                clearInterval(analysisPollingTimer);
                analysisPollingTimer = null;
              }
              chatPanel = false; // Close chat panel
            }}
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
        title={chatPanel ? 'Close Chat' : 'Open Chat'}
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
          {#if $currentPolicy}
            <AnalysisView />
          {:else}
            <EmptyPage></EmptyPage>
          {/if}
        </div>
      </div>

      <!-- (3) Panel, Main Chat -->
      {#if chatPanel}
        <div class="chat-panel" in:slide={{ axis: 'x' }}>
          <ChatPanel
            {currentSessionId}
            analysisIsGenerating={$currentPolicy?.analysis_status !==
              'completed' &&
              $currentPolicy?.analysis_status !== 'failed' &&
              currentSessionId !== null}
            on:endSession={handleEndSessionFromChat}
          ></ChatPanel>
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
  .upload-button.uploading {   /* Uploading state color for button  */
    background: #6c757d;
    cursor: not-allowed;
    opacity: 0.8;
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
  .analysis-status-dot {  /* Analysis Status Dots (added these classes and styles) */
    width: 10px;
    height: 10px;
    border-radius: 50%;
    display: inline-block;
    margin-left: 8px;
    flex-shrink: 0;
    transition: background-color 0.3s ease;
  }
  .analysis-status-dot.status-pending,
  .analysis-status-dot.status-waiting_vs_processing,
  .analysis-status-dot.status-analysis_generating {
    background-color: #ff9800; /* Orange for in-progress, distinct from background */
  }
  .analysis-status-dot.status-completed {
    background-color: #4caf50; /* Green for completed */
  }
  .analysis-status-dot.status-failed {
    background-color: #f44336; /* Red for failed */
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
