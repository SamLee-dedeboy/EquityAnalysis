<div class="empty-state">
  <svg
    width="56"
    height="56"
    fill="none"
    viewBox="0 0 24 24"
    class="empty-icon"
  >
    <circle cx="12" cy="12" r="10" fill="#6366f1" opacity="0.15" />
    <path
      d="M8 12h8M8 16h5"
      stroke="#6366f1"
      stroke-width="2"
      stroke-linecap="round"
    />
    <rect
      x="7"
      y="7"
      width="10"
      height="10"
      rx="2"
      stroke="#6366f1"
      stroke-width="2"
    />
  </svg>
  <p class="empty-title">No Document Selected</p>
  <p class="empty-desc">
    Please select a document to begin exploring our equity analysis.
  </p>
  <p class="empty-hint">
    Once you've chosen a document, you can ask questions or request deeper
    insights.
  </p>
</div>

<style>
  .empty-state {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 60vh;
    border-radius: 18px;
    margin: 8rem;
    background: #f9fafb;
  }
  .empty-icon {
    margin-bottom: 1rem;
  }
  .empty-title {
    text-align: center;
    color: #374151;
    font-size: 1.2rem;
    font-weight: 600;
    max-width: 440px;
    margin-bottom: 0.5rem;
  }
  .empty-desc {
    text-align: center;
    color: #374151;
    font-size: 1.1rem;
    font-weight: 500;
    max-width: 440px;
    margin-bottom: 0.5rem;
  }
  .empty-hint {
    text-align: center;
    color: #6b7280;
    font-size: 1rem;
    max-width: 400px;
  }
</style>
