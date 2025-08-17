<script>
  import { currentPolicy } from "../lib/stores/currentPolicy.js";
  import ExportButton from "../lib/ExportButton.svelte";

  export let analysisStatus = null; // Prop for analysis loading status. Passed from Tool.svelte

  let reportContentRef; // Declare a variable to hold the DOM reference for PDF export
</script>

<section>
  <!-- Conditional Rendering for Loading, Error, or Empty States -->

  <!-- Case 1: Currently processing a user-uploaded document -->
  {#if $currentPolicy?.id && $currentPolicy.source === 'user' && (analysisStatus !== 'completed' && analysisStatus !== 'failed')}
    <div class="loading-state">
      <div class="spinner-large"></div>
      <p class="loading-title">Generating Equity Analysis Report...</p>
      <p class="loading-desc">Status: {analysisStatus?.replace(/_/g, ' ') || 'Starting'}. This may take a few minutes as the AI processes the document.</p>
      <p class="loading-hint">The analysis indicator in the sidebar will turn green when the chat is ready for detailed questions, and yellow while the file is still being uploaded/processed.</p>
    </div>
  <!-- Case 2: Analysis for a user-uploaded document has failed -->
  {:else if $currentPolicy?.id && $currentPolicy.source === 'user' && analysisStatus === 'failed'}
    <div class="error-state">
      <svg width="56" height="56" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="error-icon">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
      </svg>
      <p class="error-title">Analysis Failed</p>
      <p class="error-desc">We encountered an error while generating the analysis for "{$currentPolicy.document?.title || $currentPolicy.id}".</p>
      <p class="error-hint">Error Details: {$currentPolicy.analysis_error || 'Unknown error.'}</p>
    </div>
  <!-- Case 3: No document selected or loaded (default empty state) -->
  {:else if !$currentPolicy?.document?.title}
    <div class="empty-state">
      <svg width="56" height="56" fill="none" viewBox="0 0 24 24" class="empty-icon">
        <circle cx="12" cy="12" r="10" fill="#6366f1" opacity="0.15" />
        <path d="M8 12h8M8 16h5" stroke="#6366f1" stroke-width="2" stroke-linecap="round" />
        <rect x="7" y="7" width="10" height="10" rx="2" stroke="#6366f1" stroke-width="2" />
      </svg>
      <p class="empty-title">No Document Selected</p>
      <p class="empty-desc">
        Please select a document from the sidebar or upload a new one to begin exploring our equity analysis.
      </p>
      <p class="empty-hint">
        Once you've chosen a document, you can ask questions or request deeper insights.
      </p>
    </div>
  {/if}

  <!-- Main Report Content (only display if analysis is completed, or it's a preprocessed doc) -->
  {#if $currentPolicy?.document?.title && (analysisStatus === 'completed' || $currentPolicy.source === 'preprocessed')}
    <div class="report-wrapper" bind:this={reportContentRef}> <!-- BIND THE DIV TO reportContentRef -->
      <h1>{$currentPolicy.document.title}</h1>
      <p><strong>Filename:</strong> {$currentPolicy.document.filename}</p>
      {#if $currentPolicy.document.size_kb}
        <p><strong>Size (KB):</strong> {$currentPolicy.document.size_kb}</p>
      {/if}

      <hr />

      <!-- NEW: Overall Analysis by Perspective (Main loop through stakeholders) -->
      {#if $currentPolicy.overall_analysis_by_perspective?.length}
        <h2>Comprehensive Analysis by Stakeholder Perspective</h2>
        {#each $currentPolicy.overall_analysis_by_perspective as perspective}
          <!-- Re-using existing .equity-perspective class for each stakeholder group -->
          <div class="equity-perspective">
            <h3>{perspective.group_name}</h3>
            <p><em>Focus: {perspective.group_description}</em></p>

            <!-- Nested loop for each analysis type within this perspective -->
            {#if perspective.analyses}
              <!-- General Equity Assessment for this perspective -->
              {#if perspective.analyses.general_equity_assessment}
                <h4>{perspective.analyses.general_equity_assessment.title}</h4>
                <p>{perspective.analyses.general_equity_assessment.summary}</p>
                {#each ["recognitional_equity", "procedural_equity", "distributional_equity", "structural_equity"] as axis}
                  <div>
                    <h5>
                      {axis
                        .replace('_equity', '')
                        .replace('_', ' ')
                        .replace(/\b\w/g, l => l.toUpperCase())} Equity
                    </h5>
                    <p>
                      <strong>Positive Findings:</strong>
                      {perspective.analyses.general_equity_assessment[axis]?.positive_findings}
                    </p>
                    <p>
                      <strong>Concerns:</strong>
                      {perspective.analyses.general_equity_assessment[axis]?.concerns}
                    </p>
                    <p>
                      <strong>Conclusion:</strong>
                      {perspective.analyses.general_equity_assessment[axis]?.conclusion}
                    </p>
                  </div>
                {/each}
              {/if}

              <hr /> <!-- Re-using original hr for separation between analysis types -->

              <!-- Vulnerable Groups Analysis for this perspective -->
              {#if perspective.analyses.vulnerable_groups_analysis}
                <h4>{perspective.analyses.vulnerable_groups_analysis.title}</h4>
                <p>{perspective.analyses.vulnerable_groups_analysis.summary}</p>
                <p>
                  <strong>Identified Groups and Impacts:</strong>
                  {perspective.analyses.vulnerable_groups_analysis.identified_groups_and_impacts}
                </p>
                <p>
                  <strong>Equity Assessment:</strong>
                  {perspective.analyses.vulnerable_groups_analysis.equity_assessment_summary}
                </p>
                <p>
                  <strong>Conclusion:</strong>
                  {perspective.analyses.vulnerable_groups_analysis.conclusion}
                </p>
              {/if}

              <hr />

              <!-- Severity of Impact Analysis for this perspective -->
              {#if perspective.analyses.severity_impact_analysis}
                <h4>{perspective.analyses.severity_impact_analysis.title}</h4>
                <p>{perspective.analyses.severity_impact_analysis.summary}</p>
                <p>
                  <strong>High Severity Impacts:</strong>
                  {perspective.analyses.severity_impact_analysis.high_severity_impacts}
                </p>
                <p>
                  <strong>Moderate Severity Impacts:</strong>
                  {perspective.analyses.severity_impact_analysis.moderate_severity_impacts}
                </p>
                <p>
                  <strong>Equity Implications:</strong>
                  {perspective.analyses.severity_impact_analysis.equity_implications_of_impacts}
                </p>
                <p>
                  <strong>Conclusion:</strong>
                  {perspective.analyses.severity_impact_analysis.conclusion}
                </p>
              {/if}

              <hr />

              <!-- Mitigation Strategies Analysis for this perspective -->
              {#if perspective.analyses.mitigation_strategies_analysis}
                <h4>{perspective.analyses.mitigation_strategies_analysis.title}</h4>
                <p>{perspective.analyses.mitigation_strategies_analysis.summary}</p>
                <p>
                  <strong>Strategies:</strong>
                  {perspective.analyses.mitigation_strategies_analysis.identified_strategies}
                </p>
                <p>
                  <strong>Equity Assessment:</strong>
                  {perspective.analyses.mitigation_strategies_analysis.equity_assessment}
                </p>
                <p>
                  <strong>Conclusion:</strong>
                  {perspective.analyses.mitigation_strategies_analysis.conclusion}
                </p>
              {/if}

            {/if} <!-- End if perspective.analyses -->
          </div>
          <hr /> <!-- Use original hr for separation between perspectives -->
        {/each}
      {/if} <!-- End if overall_analysis_by_perspective -->

      <!-- Overall Summary & Recommendations (Remains at top level) -->
      {#if $currentPolicy.overall_summary_and_recommendations}
        <h2>{$currentPolicy.overall_summary_and_recommendations.title}</h2>
        <p>
          <strong>Key Equity Gaps:</strong>
          {$currentPolicy.overall_summary_and_recommendations.key_equity_gaps}
        </p>
        <p>
          <strong>Key Equity Strengths:</strong>
          {$currentPolicy.overall_summary_and_recommendations.key_equity_strengths}
        </p>
        <p>
          <strong>Recommendations:</strong>
          {$currentPolicy.overall_summary_and_recommendations.recommendations}
        </p>
      {/if}

      <!-- Export Button -->
      <ExportButton policyId={$currentPolicy?.id} reportContentElement={reportContentRef} />
    </div>
  {/if}
</section>

<style>
  /* (i) Default Empty State */
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

  /* NEW Loading State Styles */
  .loading-state, .error-state {
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      height: 60vh;
      border-radius: 18px;
      margin: 8rem;
      background: #f9fafb;
      text-align: center;
  }
  .spinner-large {
      border: 6px solid rgba(0, 0, 0, 0.1);
      width: 50px;
      height: 50px;
      border-radius: 50%;
      border-left-color: #0d6efd; /* Use primary interactive color for spinner */
      animation: spin 1s ease infinite;
      margin-bottom: 1.5rem;
  }
  .loading-title {
      font-size: 1.5rem;
      font-weight: 600;
      color: #374151;
      margin-bottom: 0.8rem;
  }
  .loading-desc {
      font-size: 1.1rem;
      color: #6b7280;
      max-width: 500px;
      margin-bottom: 0.5rem;
  }
  .loading-hint {
      font-size: 0.9rem;
      color: #6b7280; /* Ensure this is the original color */
      max-width: 400px; /* Ensure this is the original max-width */
  }
  
  /* NEW Error State Styles */
  .error-state .error-icon {
      width: 56px;
      height: 56px;
      color: #ef4444; /* Red color for error */
      margin-bottom: 1rem;
  }
  .error-state .error-title {
      font-size: 1.4rem;
      font-weight: 600;
      color: #dc2626;
      margin-bottom: 0.5rem;
  }
  .error-state .error-desc {
      font-size: 1.05rem;
      color: #b91c1c;
      max-width: 440px;
      margin-bottom: 0.5rem;
  }
  .error-state .error-hint {
      font-size: 0.95rem;
      color: #991b1b;
  }

  /* --- Testing JSON Structure (Report Content) --- */
  .report-wrapper {
    padding: 2rem;
    background: #f9fafb;
    border-radius: 12px;
    font-family: sans-serif;
    max-height: 100vh;
    overflow-y: auto;
  }
  h1,
  h2,
  h3 { /* Keep only h1, h2, h3 as per original */
    margin-top: 1.5rem;
    color: #1f2937;
  }
  hr {
    margin: 2rem 0;
    border: 1px solid #e5e7eb;
  }
  p,
  li {
    font-size: 0.95rem;
    margin-bottom: 0.5rem;
    color: #374151;
  }
  ul {
    padding-left: 1.2rem;
  }
  .equity-perspective {
    background: #ffffff;
    padding: 1rem;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    margin-bottom: 1.5rem;
  }

  /* Keyframe for spinner animation */
  @keyframes spin {
    0% {
      transform: rotate(0deg);
    }
    100% {
      transform: rotate(360deg);
    }
  }
</style>