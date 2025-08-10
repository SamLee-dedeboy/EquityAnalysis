<script>
  let inputText = "";
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
      <div style="display: flex; align-items: flex-start; margin-bottom: 24px;">
        <!-- Bot Avatar Placeholder -->
        <div class="bot-avatar">
          <img
            src="public/botpic.png"
            alt="EquiFlow Logo"
            style="height: 1em; vertical-align: middle;"
          />
        </div>
        <div
          style="background:#f1f5fb;border-radius:12px;padding:18px 20px;max-width:420px;box-shadow:0 2px 8px rgba(0,0,0,0.04);color:#1f2937;"
        >
          <strong
            >Hello! I'm EquiFlow, your AI assistant for policy equity analysis.</strong
          >
          <ul style="margin:12px 0 0 18px;padding:0;font-size:15px;">
            <li>
              Analyze documents for equity impacts across multiple dimensions
            </li>
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
    <input bind:value={inputText} placeholder="Ask about equity impact..." />
    <button
      type="submit"
      aria-label="Send"
      style="height:38px; width:38px; display: flex; align-items: center; justify-content: center;"
    >
      <!-- Other Arrow 
               &#8593; -->
      <img
        src="public/rhs-arrow.png"
        alt="Send"
        style="height: 1em; vertical-align: middle;"
      />
    </button>
  </form>
</div>

<style>
  .chat-container {
  }
  .chat-header {
    background: #0f3c5f;
    color: #fff;
    padding: 16px 32px;
  }
  .chat-header h2 {
    font-size: 18px;
    font-weight: 600;
  }
  .chat-header p {
    font-size: 13px;
    color: #cbd5e1;
  }
  .chat-header,
  .input-bar {
    width: 100%;
    box-sizing: border-box;
  }
  /* --- (3.2) Content --- */
  .chat-content {
    padding: 32px;
    flex: 1;
    overflow-y: auto;
  }
  .bot-avatar {
    aspect-ratio: 1/1;
    width: 1.5em;
    background: var(--primary-interactive);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    margin-right: 16px;
    overflow: hidden;
    min-width: 2.5em;
  }
  /* --- (3.3) Input Bar --- */
  .input-bar {
    display: flex;
    padding: 16px 32px;
    border-top: 1px solid #ddd;
    gap: 12px;
    align-items: center;
    background: #fff;
  }
  .input-bar input {
    flex: 1;
    border: 1px solid #ccc;
    padding: 10px 16px;
    border-radius: 999px;
    font-size: 14px;
  }
  .input-bar input:focus {
    outline: none;
    border-color: #0f3c5f;
  }
  .input-bar button {
    background: #0f3c5f;
    color: #fff;
    border: none;
    padding: 10px 16px;
    border-radius: 999px;
    font-size: 18px;
    cursor: pointer;
  }
  .input-bar button:hover {
    background: #0d304f;
  }
</style>
