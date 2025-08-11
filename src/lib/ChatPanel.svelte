<script>
  import { createEventDispatcher, tick } from 'svelte';

  // Props passed from Tool.svelte
  export let currentSessionId = null;
  export let analysisIsGenerating = false; // True if the background analysis is still running

  // Internal state for the chat panel
  let inputText = "";
  // Messages array to store chat history
  let messages = [
    // The initial bot message with its original HTML structure, flagged as raw HTML
    {
      type: "bot-initial",
      contentHtml: `
        <div style="display: flex; align-items: flex-start; margin-bottom: 24px;">
          <div class="bot-avatar" style="height: 1.5em; width: 1.5em; background: var(--primary-interactive); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 16px; overflow: hidden; min-width: 2.5em;">
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
      `
    }
  ];
  let isQuerying = false; // True when a query is being sent and a response awaited
  let noteAnalysisGeneratingDisplayed = false; // Flag to show "Note: Full analysis report..." only once per query

  const dispatch = createEventDispatcher();

  // Function to dynamically add messages to the chatbox
  async function addMessage(content, type = "status") {
    messages = [...messages, { type, content }];
    await tick(); // Wait for DOM update to ensure scrollHeight is correct
    const chatboxElement = document.querySelector(".chat-messages");
    if (chatboxElement) {
      chatboxElement.scrollTop = chatboxElement.scrollHeight; // Scroll to bottom
    }
  }

  // Handle user query submission
  async function handleSubmitQuery() {
    const query = inputText.trim();
    const focusAreaValue = "general"; // Always send as 'general' for now
    const customInstructions = null;

    if (!query || !currentSessionId || isQuerying) {
      return;
    }

    // Display note about background analysis if it's still running
    if (analysisIsGenerating && !noteAnalysisGeneratingDisplayed) {
        addMessage("Note: Full analysis report is still generating in the left panel. Your query will use the currently indexed document content.", "status");
        noteAnalysisGeneratingDisplayed = true;
    } else if (!analysisIsGenerating) {
        noteAnalysisGeneratingDisplayed = false; // Reset flag if analysis is no longer generating
    }

    // Add user message to chatbox
    addMessage(query, "user"); // Original design had no "Focus: General Analysis" text for user message
    inputText = ""; // Clear input field

    isQuerying = true; // Set querying state to true

    let payload = {
      session_id: currentSessionId,
      query: query,
      focus_area: focusAreaValue,
      custom_instructions: customInstructions,
    };

    try {
      const response = await fetch("http://localhost:8000/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        let errorMsg = `Server responded with an error: ${response.status}`;
        try { const errData = await response.json(); errorMsg = errData.detail || errorMsg; } catch (e) {}
        throw new Error(errorMsg);
      }

      const result = await response.json();
      addMessage(result.answer, "bot"); // No sources at this time

    } catch (error) {
      console.error("Query error:", error);
      addMessage(`An error occurred: ${error.message}`, "status");
    } finally {
      isQuerying = false; // Reset querying state
    }
  }

  // Handle "End Chat" button click
  async function handleEndSession() {
    if (!currentSessionId || isQuerying) return;

    addMessage("Ending session...", "status");
    isQuerying = true; // Temporarily disable inputs

    try {
      const response = await fetch("http://localhost:8000/end-session", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: currentSessionId }),
      });
      const result = await response.json();

      if (response.ok && result.success) {
        addMessage("Session ended. All resources cleaned up.", "status");
        dispatch('endSession'); // Notify parent (Tool.svelte) to reset its state
        // Reset ChatPanel's internal state
        inputText = "";
        messages = [
          {
            type: "bot-initial",
            contentHtml: `
              <div style="display: flex; align-items: flex-start; margin-bottom: 24px;">
                <div class="bot-avatar" style="height: 1.5em; width: 1.5em; background: var(--primary-interactive); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 16px; overflow: hidden; min-width: 2.5em;">
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
            `
          }
        ];
        currentSessionId = null;
        analysisIsGenerating = false;
        noteAnalysisGeneratingDisplayed = false;
      } else {
        addMessage(`Error ending session: ${result.message || "Unknown error."}`, "status");
      }
    } catch (error) {
      console.error("End session network error:", error);
      addMessage("Network or server error during session end.", "status");
    } finally {
      isQuerying = false;
    }
  }
</script>

<div class="chat-container">
  <!-- (3.1) Header with Logo -->
  <div class="chat-header">
    <h2>EquiFlow AI Assistant</h2>
    <p>Intelligent Policy Equity Analysis</p>
  </div>

  <!-- (3.2) Chat Box -->
  <div class="chat-content">
    <div class="chat-messages">
      {#each messages as message}
        {#if message.type === 'bot-initial'}
          <!-- Render the initial complex bot message -->
          {@html message.contentHtml}
        {:else if message.type === 'user'}
          <!-- User message -->
          <div style="display: flex; align-items: flex-end; margin-bottom: 24px; justify-content: flex-end;">
            <div style="background:#e0e7ef;border-radius:12px;padding:18px 20px;max-width:420px;box-shadow:0 2px 8px rgba(0,0,0,0.04);color:#0F3C5F;">
              <p style="margin:0;">{message.content}</p>
            </div>
          </div>
        {:else if message.type === 'bot'}
          <!-- Bot response message -->
          <div style="display: flex; align-items: flex-start; margin-bottom: 24px;">
            <div class="bot-avatar" style="height: 1.5em; width: 1.5em; background: var(--primary-interactive); border-radius: 50%; display: flex; align-items: center; justify-content: center; margin-right: 16px; overflow: hidden; min-width: 2.5em;">
              <img src="public/botpic.png" alt="EquiFlow Logo" style="height: 1em; vertical-align: middle;">
            </div>
            <div style="background:#f1f5fb;border-radius:12px;padding:18px 20px;max-width:420px;box-shadow:0 2px 8px rgba(0,0,0,0.04);color:#1f2937;">
              <p style="margin:0;">{message.content}</p>
            </div>
          </div>
        {:else if message.type === 'status'}
          <!-- Status message, centered with spinner if "Analyzing..." or "Ending session..." -->
          <div style="display: flex; justify-content: center; margin-bottom: 12px;">
            <div style="font-style: italic; color: #666; font-size: 0.9em; padding: 8px 15px; border-radius: 8px; background-color: #f8f8f8; display: flex; align-items: center; gap: 8px;">
                {#if message.content.includes('Analyzing...') || message.content.includes('Ending session...')}
                    <div class="spinner-small"></div>
                {/if}
                {message.content}
            </div>
          </div>
        {/if}
      {/each}

      {#if isQuerying && messages.at(-1)?.type !== 'status'}
        <!-- General "Analyzing..." status for current query if not already showing status -->
        <div style="display: flex; justify-content: center; margin-bottom: 12px;">
            <div style="font-style: italic; color: #666; font-size: 0.9em; padding: 8px 15px; border-radius: 8px; background-color: #f8f8f8; display: flex; align-items: center; gap: 8px;">
                <div class="spinner-small"></div> Analyzing...
            </div>
        </div>
      {/if}
    </div>
  </div>

  <!-- Analysis Focus Selector - HTML retained, value currently ignored for API calls -->
  <!-- Note: Styles applied via the global style tag for 'select' elements in templates.html if applicable. -->
  <div class="focus-area-selector" style="padding: 16px 32px 0 32px;">
    <label for="analysis-focus" style="font-weight: bold; margin-right: 10px; color: #1f2937;">Select Analysis Focus:</label>
    <select id="analysis-focus" name="analysis-focus" disabled={!currentSessionId || isQuerying}
      style="padding: 10px 16px; border: 1px solid #ccc; border-radius: 999px; font-size: 14px; flex-grow: 1; height: 38px;">
      <option value="general">General COEQWAL Analysis</option>
      <option value="vulnerable_groups">Focus: Vulnerable Groups</option>
      <option value="severity_of_impact">Focus: Severity of Impact</option>
      <option value="mitigation_strategies">
        Focus: Mitigation Strategies
      </option>
      <option disabled>──────────────────</option>
      <option value="add_custom">+ Create Custom Focus...</option>
    </select>
  </div>

  <!-- (3.3) Input Bar -->
  <form class="input-bar" on:submit|preventDefault={handleSubmitQuery}>
    <input
      bind:value={inputText}
      placeholder="Ask about equity impact..."
      disabled={!currentSessionId || isQuerying}
      style="flex: 1; border: 1px solid #ccc; padding: 10px 16px; border-radius: 999px; font-size: 14px;"
    />
    <button
      type="submit"
      aria-label="Send"
      style="height:38px; width:38px; display: flex; align-items: center; justify-content: center; background: #0f3c5f; color: #fff; border: none; padding: 10px 16px; border-radius: 999px; font-size: 18px; cursor: pointer;"
      disabled={!currentSessionId || isQuerying || !inputText.trim()}
    >
      <img
        src="public/rhs-arrow.png"
        alt="Send"
        style="height: 1em; vertical-align: middle;"
      />
    </button>
  </form>

  <!-- End Chat Button -->
  <div class="end-chat-area" style="padding: 16px 32px; border-top: 1px solid #ddd; text-align: right;">
    <button
      on:click={handleEndSession}
      disabled={!currentSessionId || isQuerying}
      style="background-color: #dc3545; color: white; border: none; padding: 10px 15px; border-radius: 5px; cursor: pointer;"
    >
      End Chat & Clean Up Resources
    </button>
  </div>
</div>

<style>
  /* --- Original Styles (Copied Directly) --- */
  .chat-container {
    height: 100%; /* Ensure it takes full height of its parent container */
    display: flex;
    flex-direction: column;
  }
  .chat-header {
    background: #0f3c5f;
    color: #fff;
    padding: 16px 32px;
  }
  .chat-header h2 {
    font-size: 18px;
    font-weight: 600;
    margin: 0; /* Override default margin */
  }
  .chat-header p {
    font-size: 13px;
    color: #cbd5e1;
    margin: 0; /* Override default margin */
  }
  .chat-header,
  .input-bar {
    width: 100%;
    box-sizing: border-box;
  }
  /* --- (3.2) Chat Content & Messages --- */
  .chat-content {
    flex: 1; /* Allows content area to grow and take available space */
    overflow-y: auto; /* Adds scrollbar when messages exceed height */
  }
  .chat-messages {
    padding: 32px; /* Inner padding for messages */
    min-height: 100%; /* Ensure content fills at least its container height */
    display: flex;
    flex-direction: column; /* Stack messages vertically */
  }

  /* --- Original .bot-avatar style, used for bot messages --- */
  .bot-avatar {
    aspect-ratio: 1/1;
    width: 1.5em; /* Matches original width */
    height: 1.5em; /* Ensures square aspect ratio */
    background: var(--primary-interactive);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    overflow: hidden;
    min-width: 2.5em; /* Matches original min-width */
    flex-shrink: 0; /* Prevent it from shrinking */
  }
  .bot-avatar img {
    height: 1em; /* Matches original img height */
    vertical-align: middle;
  }

  /* --- (3.3) Input Bar & Button Styles --- */
  .input-bar {
    display: flex;
    padding: 16px 32px;
    border-top: 1px solid #ddd;
    gap: 12px;
    align-items: center;
    background: #fff;
  }
  .input-bar input:focus {
    outline: none;
    border-color: #0f3c5f;
  }
  .input-bar button:hover {
    background: #0d304f;
  }

  /* --- Disabled Styles (Inherited from general project CSS/templates.html where applicable) --- */
  .input-bar input:disabled,
  .input-bar button:disabled,
  select:disabled {
    background-color: #e9ecef; /* Lighter background for disabled elements */
    cursor: not-allowed;
    opacity: 0.7;
  }
  .input-bar button:disabled {
    background-color: #6c757d; /* Grey button for disabled */
  }

  /* --- NEW: Spinner Small (copied from previous instructions) --- */
  .spinner-small {
    border: 2px solid rgba(0, 0, 0, 0.1);
    width: 16px;
    height: 16px;
    border-radius: 50%;
    border-left-color: #0d6efd; /* Use primary interactive color */
    animation: spin 1s ease infinite;
    flex-shrink: 0;
  }
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
</style>