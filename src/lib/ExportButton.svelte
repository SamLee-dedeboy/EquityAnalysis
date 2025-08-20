<script>
  import html2pdf from 'html2pdf.js';

  export let policyId;
  export let reportContentElement;

  let isExporting = false;

  async function exportToPdf() {
    if (!reportContentElement) {
      console.error('Report content element not found for PDF export.');
      alert(
        'Report content not found for export. Please ensure a document is selected.'
      );
      return;
    }

    isExporting = true;

    let filename = `equity_analysis_report_${policyId || 'unknown'}.pdf`;
    if (reportContentElement.querySelector('h1')) {
      filename =
        reportContentElement
          .querySelector('h1')
          .textContent.trim()
          .replace(/[^a-z0-9]/gi, '_')
          .toLowerCase() + '_equity_analysis.pdf';
    } else if (reportContentElement.querySelector('p strong')) {
      filename =
        reportContentElement
          .querySelector('p strong')
          .textContent.trim()
          .replace(/[^a-z0-9]/gi, '_')
          .toLowerCase() + '_equity_analysis.pdf';
    }

    const opt = {
      margin: [0.75, 0.5, 0.75, 0.5], // Slightly more top/bottom margin
      filename: filename,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: {
        scale: 2, // Keep scale at 2 or 3 for good resolution
        logging: true,
        useCORS: true, // Important if you have images from different origins
        scrollY: 0, // Start capturing from the very top
        // Attempt to capture the full scrollable height
        windowHeight: reportContentElement.scrollHeight,
        windowWidth: reportContentElement.scrollWidth,
      },
      jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' },
      pagebreak: {
        mode: ['css', 'avoid-all', 'legacy'],
      },
    };

    const originalReportWrapperStyle = reportContentElement.style.cssText;
    const parentReportPanel = reportContentElement.parentElement; // .report-content
    const grandParentReportChatContainer = parentReportPanel
      ? parentReportPanel.parentElement
      : null; // .report-panel
    const greatGrandParentScreenLayout = grandParentReportChatContainer
      ? grandParentReportChatContainer.parentElement
      : null; // .screen-layout

    const originalParentReportPanelStyle = parentReportPanel
      ? parentReportPanel.style.cssText
      : '';
    const originalGrandParentReportChatContainerStyle =
      grandParentReportChatContainer
        ? grandParentReportChatContainer.style.cssText
        : '';
    const originalGreatGrandParentScreenLayoutStyle =
      greatGrandParentScreenLayout
        ? greatGrandParentScreenLayout.style.cssText
        : '';

    // Apply temporary styles
    if (reportContentElement) {
      reportContentElement.style.overflowY = 'visible';
      reportContentElement.style.height = 'auto';
      reportContentElement.style.maxHeight = 'none';
    }
    if (parentReportPanel) {
      parentReportPanel.style.overflowY = 'visible';
      parentReportPanel.style.height = 'auto';
      parentReportPanel.style.maxHeight = 'none';
    }
    if (grandParentReportChatContainer) {
      grandParentReportChatContainer.style.overflow = 'visible';
      grandParentReportChatContainer.style.height = 'auto';
      grandParentReportChatContainer.style.maxHeight = 'none';
    }
    if (greatGrandParentScreenLayout) {
      greatGrandParentScreenLayout.style.overflow = 'visible';
      greatGrandParentScreenLayout.style.height = 'auto';
      greatGrandParentScreenLayout.style.maxHeight = 'none';
    }

    try {
      await html2pdf().set(opt).from(reportContentElement).save();
      console.log('PDF export successful!');
    } catch (error) {
      console.error('PDF export failed:', error);
      alert('Failed to export PDF. Please try again.');
    } finally {
      // --- Restore original styles ---
      if (reportContentElement) {
        reportContentElement.style.cssText = originalReportWrapperStyle;
      }
      if (parentReportPanel) {
        parentReportPanel.style.cssText = originalParentReportPanelStyle;
      }
      if (grandParentReportChatContainer) {
        grandParentReportChatContainer.style.cssText =
          originalGrandParentReportChatContainerStyle;
      }
      if (greatGrandParentScreenLayout) {
        greatGrandParentScreenLayout.style.cssText =
          originalGreatGrandParentScreenLayoutStyle;
      }

      isExporting = false;
    }
  }
</script>

<div class="button-container">
  <button
    class="btn primary"
    on:click={exportToPdf}
    disabled={!reportContentElement || isExporting}
  >
    {#if isExporting}
      Generating PDF...
    {:else}
      Export Analysis
    {/if}
  </button>
</div>

<style>
  .button-container {
    display: flex;
    gap: 1rem;
    margin-top: 1.5rem;
    justify-content: center;
  }
  .btn {
    font-size: 1rem;
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    font-weight: 500;
    border: 2px solid #09385b;
    cursor: pointer;
    transition:
      background-color 0.2s ease,
      color 0.2s ease;
  }
  .btn.primary {
    background-color: #09385b;
    color: white;
  }
  .btn.primary:hover {
    background-color: #072b44;
  }
  .btn.secondary {
    background-color: #f8f8f8;
    color: #09385b;
  }
  .btn.secondary:hover {
    background-color: #eaeaea;
  }

  .btn:disabled {
    background-color: #a0a0a0;
    border-color: #888888;
    color: #cccccc;
    cursor: not-allowed;
    opacity: 0.7;
  }
</style>
