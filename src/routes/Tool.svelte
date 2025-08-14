<script>
  import { onMount, tick } from "svelte"; // Import tick for DOM updates
  import { slide } from "svelte/transition";

  // Importing Local Modules
  import LogoBar from "../lib/LogoBar.svelte";
  import ReportView from "./_ReportView.svelte";
  import ChatPanel from "../lib/ChatPanel.svelte";

  import {
    currentPolicy,
    fetchPolicies,
    fetchPolicyDataById,
  } from "../lib/stores/currentPolicy.js";
  import EmptyPage from "../lib/EmptyPage.svelte";
  import AnalysisView from "./AnalysisView.svelte";

  import { server_address } from "../constants";
  let policies = []; // This will now be dynamically loaded and updated from the API
  let isUploading = false; // True if file upload/VS creation is in progress
  let analysisStatus = null; // 'pending', 'waiting_vs_processing', 'analysis_generating', 'completed', 'failed'
  let currentSessionId = null; // Stores the session ID for the current user upload
  let analysisPollingTimer = null;
  let analysisResultFetched = false; // Flag to prevent multiple fetches/displays of the full analysis JSON

  const ANALYSIS_POLLING_INTERVAL_MS = 5000; // Poll every 5 seconds for analysis status

  // --- Lifecycle Hook ---
  // onMount(async () => {
  //   currentPolicy.set(null); // Clear any previous selection when component mounts
  //   await loadInitialPolicies(); // Load existing policies from API
  // });

  // Function to load policies from the backend
  async function loadInitialPolicies() {
    try {
      policies = await fetchPolicies();
      policies = policies.map((p) => ({
        ...p,
        analysis_status:
          p.analysis_status ||
          (p.source === "preprocessed" ? "completed" : "unknown"),
      }));
      // const res = await fetch(`${server_address}/api/policies`);
      // if (res.ok) {
      //   // Ensure that fetched policies have a default analysis_status if it's missing (e.g., for preprocessed)
      //   policies = await res.json();
      //   policies = policies.map((p) => ({
      //     ...p,
      //     analysis_status:
      //       p.analysis_status ||
      //       (p.source === "preprocessed" ? "completed" : "unknown"),
      //   }));
      // } else {
      //   console.error(
      //     "Failed to load initial policies list:",
      //     res.status,
      //     await res.text()
      //   );
      // }
    } catch (err) {
      console.error("Network error loading initial policies list:", err);
    }
  }

  // Function to load a specific policy's full data (either preprocessed or user-uploaded)
  async function loadPolicyData(policyId) {
    analysisStatus = null; // Reset analysis status for the UI when a new policy is clicked
    analysisResultFetched = false; // Reset fetching flag for the new policy

    // Find the policy in our local 'policies' array to get its basic info
    const selectedPolicy = policies.find((p) => p.id === policyId);
    if (selectedPolicy) {
      // Set the currentPolicy store with the basic metadata first. This immediately updates the sidebar selection.
      currentPolicy.set(selectedPolicy);
      // currentDoc = selectedPolicy; // Pass this basic info to ReportView immediately

      // If the selected policy is preprocessed or already marked completed (from a prior session/load)
      if (
        selectedPolicy.source === "preprocessed" ||
        selectedPolicy.analysis_status === "completed"
      ) {
        try {
          // Fetch the full detailed data for display in ReportView
          // const res = await fetch(`${server_address}/api/policies/${policyId}`);
          const fullPolicyData = await fetchPolicyDataById(policyId);
          currentPolicy.set(fullPolicyData); // Update store with full detailed data
          // currentDoc = fullPolicyData; // Update local reference for ReportView
          analysisStatus = "completed"; // Explicitly set status to completed for UI
        } catch (err) {
          console.error("Error loading full policy data:", err);
          analysisStatus = "failed";
          currentPolicy.update((p) => ({
            ...p,
            analysis_status: "failed",
            analysis_error: "Network error loading report data.",
          }));
          // currentDoc = {
          //   ...currentDoc,
          //   analysis_status: "failed",
          //   analysis_error: "Network error loading report data.",
          // };
        }
      } else if (
        selectedPolicy.source === "user" &&
        selectedPolicy.analysis_status !== "failed"
      ) {
        // If it's a user upload and not yet completed or failed, start/continue polling
        currentSessionId = policyId; // For user uploads, the policy ID is the session ID
        analysisStatus = selectedPolicy.analysis_status; // Use the existing status from the sidebar list

        // Clear any existing polling timer from a previous session
        if (analysisPollingTimer) {
          clearInterval(analysisPollingTimer);
        }
        // Start polling for status updates
        analysisPollingTimer = setInterval(
          () => pollAnalysisStatus(currentSessionId),
          ANALYSIS_POLLING_INTERVAL_MS
        );
        pollAnalysisStatus(currentSessionId); // Initial immediate poll to display current status
      } else if (
        selectedPolicy.source === "user" &&
        selectedPolicy.analysis_status === "failed"
      ) {
        // If it's a user upload that previously failed, ensure UI reflects that
        analysisStatus = "failed";
        currentPolicy.update((p) => ({
          ...p,
          analysis_status: "failed",
          analysis_error:
            selectedPolicy.analysis_error || "Analysis previously failed.",
        }));
        // currentDoc = {
        //   ...currentDoc,
        //   analysis_status: "failed",
        //   analysis_error:
        //     selectedPolicy.analysis_error || "Analysis previously failed.",
        // };
      }
    } else {
      console.warn(`Policy with ID ${policyId} not found in the list.`);
      currentPolicy.set(null); // Clear if not found
      // currentDoc = null;
      analysisStatus = null; // No status if no policy selected
    }
    chatPanel = true; // Open chat panel when a document is selected/loaded
  }

  // NEW: handleFileUpload function for the upload button
  async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    // --- Reset all relevant state for a new upload session ---
    if (analysisPollingTimer) {
      clearInterval(analysisPollingTimer);
      analysisPollingTimer = null;
    }
    currentSessionId = null;
    analysisStatus = null;
    analysisResultFetched = false;
    currentPolicy.set(null); // Clear any currently selected policy in the store
    // currentDoc = null; // Clear ReportView content

    isUploading = true; // Set upload state to true for UI feedback (changes button color)

    const formData = new FormData();
    formData.append("file", file);

    // Add a temporary entry to the policies list immediately to show processing in sidebar
    // This uses a temporary ID that will be replaced by the real session_id from the backend
    const tempId = `temp-${Date.now()}`;
    const tempPolicyEntry = {
      id: tempId,
      document: {
        title: file.name,
        filename: file.name,
        size_kb: Math.round(file.size / 1024),
        upload_date_utc: new Date().toISOString(),
      },
      source: "user",
      analysis_status: "pending", // Initial status for this new entry
      analysis_error: null, // No error yet
    };
    policies = [tempPolicyEntry, ...policies]; // Add to top of sidebar list
    currentPolicy.set(tempPolicyEntry); // Select this newly uploaded/processing entry
    // currentDoc = tempPolicyEntry; // Pass to ReportView for immediate display of loading state

    try {
      const response = await fetch(`${server_address}/upload`, {
        method: "POST",
        body: formData,
      });
      const result = await response.json();

      if (response.ok && result.success) {
        currentSessionId = result.session_id; // Get the real session ID from backend
        analysisStatus = result.analysis_status; // This should be "pending"

        policies = policies.map((p) =>
          p.id === tempId
            ? { ...p, id: currentSessionId, analysis_status: analysisStatus }
            : p
        );

        // Also update currentPolicy with the real ID, so ReportView uses the correct ID for polling
        currentPolicy.update((p) => ({
          ...p,
          id: currentSessionId,
          analysis_status: analysisStatus,
        }));
        // currentDoc = {
        //   ...currentDoc,
        //   id: currentSessionId,
        //   analysis_status: analysisStatus,
        // };

        // Start polling for analysis status
        analysisPollingTimer = setInterval(
          () => pollAnalysisStatus(currentSessionId),
          ANALYSIS_POLLING_INTERVAL_MS
        );
        pollAnalysisStatus(currentSessionId); // Initial immediate poll to display first status
        chatPanel = true; // Open chat panel automatically for new uploads
      } else {
        console.error("Upload failed:", result.message || "Unknown error");
        analysisStatus = "failed";
        policies = policies.filter((p) => p.id !== tempId); // Remove if upload failed at this stage
        currentPolicy.set(null); // Clear selection
        // currentDoc = null;
      }
    } catch (error) {
      console.error("Upload network error:", error);
      analysisStatus = "failed";
      policies = policies.map((p) =>
        p.id === tempId
          ? {
              ...p,
              analysis_status: "failed",
              analysis_error: "Network error during upload.",
            }
          : p
      );
      currentPolicy.update((p) => ({
        ...p,
        analysis_status: "failed",
        analysis_error: "Network error during upload.",
      }));
      // currentDoc = {
      //   ...currentDoc,
      //   analysis_status: "failed",
      //   analysis_error: "Network error during upload.",
      // };
    } finally {
      isUploading = false; // Reset upload state
    }
  }

  // NEW: Polling function for analysis status (updates sidebar and ReportView state)
  async function pollAnalysisStatus(sessionId) {
    // If analysis result for this session is already fetched and displayed, stop polling
    if (analysisResultFetched) {
      clearInterval(analysisPollingTimer);
      analysisPollingTimer = null;
      analysisStatus = "completed"; // Ensure state is completed
      return;
    }

    try {
      const response = await fetch(
        `${server_address}/get_analysis_status/${sessionId}`
      );
      if (!response.ok) {
        console.error("Polling error:", response.status, await response.text());
        analysisStatus = "failed";
        clearInterval(analysisPollingTimer);
        analysisPollingTimer = null;
        // Update the specific policy entry in 'policies' array to reflect failure
        policies = policies.map((p) =>
          p.id === sessionId
            ? {
                ...p,
                analysis_status: "failed",
                analysis_error: "Failed to get status.",
              }
            : p
        );
        currentPolicy.update((p) => ({
          ...p,
          analysis_status: "failed",
          analysis_error: "Failed to get status.",
        })); // Also update currentPolicy
        // currentDoc = {
        //   ...currentDoc,
        //   analysis_status: "failed",
        //   analysis_error: "Failed to get status.",
        // }; // Update local for ReportView
        return;
      }

      const result = await response.json();
      const newStatus = result.analysis_status;

      analysisStatus = newStatus; // Update global analysisStatus for ReportView to react

      // Update the specific policy entry in 'policies' array with the new status and error (if any)
      policies = policies.map((p) =>
        p.id === sessionId
          ? {
              ...p,
              analysis_status: newStatus,
              analysis_error: result.analysis_error,
            }
          : p
      );
      currentPolicy.update((p) => ({
        ...p,
        analysis_status: newStatus,
        analysis_error: result.analysis_error,
      })); // Update currentPolicy store
      // currentDoc = {
      //   ...currentDoc,
      //   analysis_status: newStatus,
      //   analysis_error: result.analysis_error,
      // }; // Update local for ReportView

      if (newStatus === "completed") {
        clearInterval(analysisPollingTimer);
        analysisPollingTimer = null;
        await displayAnalysisResult(sessionId); // Fetch and display the full JSON
      } else if (newStatus === "failed") {
        clearInterval(analysisPollingTimer);
        analysisPollingTimer = null;
        console.error(
          `Analysis for ${sessionId} failed: ${result.analysis_error}`
        );
      }
    } catch (error) {
      console.error("Network error during analysis status polling:", error);
      analysisStatus = "failed";
      clearInterval(analysisPollingTimer);
      analysisPollingTimer = null;
      policies = policies.map((p) =>
        p.id === sessionId
          ? {
              ...p,
              analysis_status: "failed",
              analysis_error: "Network error.",
            }
          : p
      );
      currentPolicy.update((p) => ({
        ...p,
        analysis_status: "failed",
        analysis_error: "Network error.",
      }));
      // currentDoc = {
      //   ...currentDoc,
      //   analysis_status: "failed",
      //   analysis_error: "Network error.",
      // };
    }
  }

  // NEW: Function to display the full JSON analysis result once completed
  async function displayAnalysisResult(sessionId) {
    if (analysisResultFetched) {
      console.log(
        "Analysis result already fetched, skipping duplicate display."
      );
      return;
    }
    analysisResultFetched = true; // Mark as fetched to prevent re-fetching

    try {
      const response = await fetch(
        `${server_address}/get_analysis_result/${sessionId}`
      );
      if (!response.ok) {
        console.error(
          "Failed to retrieve analysis result:",
          response.status,
          await response.text()
        );
        analysisResultFetched = false; // Allow re-attempt if the fetch itself fails
        analysisStatus = "failed";
        currentPolicy.update((p) => ({
          ...p,
          analysis_status: "failed",
          analysis_error: "Failed to retrieve analysis report data.",
        }));
        // currentDoc = {
        //   ...currentDoc,
        //   analysis_status: "failed",
        //   analysis_error: "Failed to retrieve analysis report data.",
        // };
        return;
      }

      const result = await response.json();
      if (result.analysis_status === "completed") {
        // Update the policies list with the full data for the completed item
        policies = policies.map((p) => {
          if (p.id === sessionId) {
            return {
              ...p,
              ...result.analysis_data,
              analysis_status: "completed",
            }; // Merge full data into the existing policy object
          }
          return p;
        });
        // Important: Set the full analysis data to currentPolicy store and local currentDoc
        await tick(); // Ensure DOM updates are pending before setting full data
        currentPolicy.set(result.analysis_data);
        // currentDoc = result.analysis_data; // Also update local currentDoc for ReportView
        analysisStatus = "completed"; // Ensure the global analysisStatus reflects completion
      } else {
        // This case should ideally not be hit if pollAnalysisStatus works correctly
        console.error(
          "Analysis result was not 'completed' when fetched via get_analysis_result:",
          result.analysis_status
        );
        analysisResultFetched = false;
        analysisStatus = "failed";
        currentPolicy.update((p) => ({
          ...p,
          analysis_status: "failed",
          analysis_error: "Unexpected status when retrieving full report.",
        }));
        // currentDoc = {
        //   ...currentDoc,
        //   analysis_status: "failed",
        //   analysis_error: "Unexpected status when retrieving full report.",
        // };
      }
    } catch (error) {
      console.error("Error fetching analysis result:", error);
      analysisResultFetched = false;
      analysisStatus = "failed";
      currentPolicy.update((p) => ({
        ...p,
        analysis_status: "failed",
        analysis_error: "Network error while fetching analysis report.",
      }));
      // currentDoc = {
      //   ...currentDoc,
      //   analysis_status: "failed",
      //   analysis_error: "Network error while fetching analysis report.",
      // };
    }
  }

  // Handle End Session triggered from ChatPanel
  async function handleEndSessionFromChat() {
    if (!currentSessionId) return;

    // Reset Tool.svelte's state associated with the session that just ended
    if (analysisPollingTimer) {
      clearInterval(analysisPollingTimer);
      analysisPollingTimer = null;
    }
    isUploading = false;
    analysisStatus = null;
    analysisResultFetched = false;

    // Remove the ended policy from the sidebar list
    // This will automatically cause currentPolicy.set(null) if the ended policy was selected
    policies = policies.filter((p) => p.id !== currentSessionId);
    currentPolicy.set(null); // Explicitly clear the selected policy in the store
    // currentDoc = null; // Clear ReportView content
    currentSessionId = null; // Clear active session ID

    chatPanel = false; // Close chat panel as the session has ended and nothing new is selected
  }

  // State Variables, Third Panel (Overview) - Original position
  let chatPanel = false;
  // Chat Logic - Original position
  // let currentDoc = null; // Will be set by loadPolicyData and displayAnalysisResult

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

      <!-- (1.1) Upload Button -->
      <label
        class="upload-button"
        class:uploading={isUploading}
        style="display:flex;align-items:center;gap:6px;padding:8px 10px; min-width:100%; width:100%; justify-content:center; cursor:pointer;"
      >
        <img
          src="public/docup.svg"
          alt="Upload"
          style="width:18px;height:18px;"
        />
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
                {policy.document?.title || policy.id}
                <!-- Display title, fallback to ID -->
                {#if policy.source === "user"}
                  <span
                    class="analysis-status-dot"
                    class:status-pending={policy.analysis_status ===
                      "pending" ||
                      policy.analysis_status === "waiting_vs_processing" ||
                      policy.analysis_status === "analysis_generating"}
                    class:status-completed={policy.analysis_status ===
                      "completed"}
                    class:status-failed={policy.analysis_status === "failed"}
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
              // Filters policies to only keep those sourced as 'preprocessed'.
              // This is a local frontend-only clear. Backend cleanup requires explicit calls.
              policies = policies.filter((p) => p.source === "preprocessed");
              currentPolicy.set(null); // Deselect any policy
              // currentDoc = null; // Clear ReportView content
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
          {#if $currentPolicy}
            <!-- <ReportView {currentDoc} {analysisStatus} /> -->
            <AnalysisView />
          {:else}
            <EmptyPage></EmptyPage>
          {/if}
        </div>
      </div>

      <!-- (3) Panel, Main Chat -->
      {#if chatPanel}
        <div class="chat-panel" in:slide={{ axis: "x" }}>
          <ChatPanel
            {currentSessionId}
            analysisIsGenerating={analysisStatus !== "completed" &&
              analysisStatus !== "failed" &&
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
  /* NEW: Uploading state color for button (added this class and style) */
  .upload-button.uploading {
    background: #6c757d; /* A muted grey, consistent with disabled states */
    cursor: not-allowed;
    opacity: 0.8; /* Slightly less opaque */
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

  /* NEW: Analysis Status Dots (added these classes and styles) */
  .analysis-status-dot {
    /* Base styles are inline in HTML to preserve original button layout */
    transition: background-color 0.3s ease; /* Smooth color transition */
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

