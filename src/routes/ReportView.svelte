<script>

    // Policies data
    import { currentPolicy } from '../lib/stores/currentPolicy.js';


    // Testing
    const testState = true;
    import test from "../lib/data/test.json";
    import ExportButton from '../lib/ExportButton.svelte';

</script>

<style>
    
    /* (i) Default Empty State */
    .empty-state { display: flex; flex-direction: column; justify-content: center; align-items: center; height: 60vh; border-radius: 18px; margin: 8rem; background: #f9fafb; }
    .empty-icon { margin-bottom: 1rem; }
    .empty-title { text-align: center; color: #374151; font-size: 1.2rem; font-weight: 600; max-width: 440px; margin-bottom: 0.5rem; }
    .empty-desc { text-align: center; color: #374151; font-size: 1.1rem; font-weight: 500; max-width: 440px; margin-bottom: 0.5rem; }
    .empty-hint { text-align: center; color: #6b7280; font-size: 1rem; max-width: 400px; }

    /* --- Testing JSON Structure --- */
    .report-wrapper { padding: 2rem; background: #f9fafb; border-radius: 12px; font-family: sans-serif; max-height: 100vh; overflow-y: auto; }
    h1, h2, h3 { margin-top: 1.5rem; color: #1f2937; }
    hr { margin: 2rem 0; border: 1px solid #e5e7eb; }
    p, li { font-size: 0.95rem; margin-bottom: 0.5rem; color: #374151; }
    ul { padding-left: 1.2rem; }
    .equity-perspective { background: #ffffff; padding: 1rem; border: 1px solid #e5e7eb; border-radius: 8px; margin-bottom: 1.5rem; }

</style>
<section>
    <!-- (i) Default Empty State -->
    {#if !$currentPolicy?.document?.title}
        <div class="empty-state">
            <svg width="56" height="56" fill="none" viewBox="0 0 24 24" class="empty-icon">
                <circle cx="12" cy="12" r="10" fill="#6366f1" opacity="0.15"/>
                <path d="M8 12h8M8 16h5" stroke="#6366f1" stroke-width="2" stroke-linecap="round"/>
                <rect x="7" y="7" width="10" height="10" rx="2" stroke="#6366f1" stroke-width="2"/>
            </svg>
            <p class="empty-title">
                No Document Selected
            </p>
            <p class="empty-desc">
                Please select a document to begin exploring our equity analysis.
            </p>
            <p class="empty-hint">
                Once you've chosen a document, you can ask questions or request deeper insights.
            </p>
        </div>
    {/if}

    <!-- (Demo) Report Content -->
    {#if $currentPolicy?.document?.title}
        <div class="report-wrapper">
            <h1>{$currentPolicy.document.title}</h1>
            <p><strong>Filename:</strong> {$currentPolicy.document.filename}</p>
            <p><em>{$currentPolicy.document.description}</em></p>

            <hr />

            <h2>{$currentPolicy.analysis_sections.general_equity_assessment.title}</h2>
            <p>{$currentPolicy.analysis_sections.general_equity_assessment.summary}</p>

            {#each ['recognitional_equity', 'procedural_equity', 'distributional_equity', 'structural_equity'] as axis}
                <div>
                    <h3>{$currentPolicy.analysis_sections.general_equity_assessment[axis].title}</h3>
                    <p><strong>Positive Findings:</strong> {$currentPolicy.analysis_sections.general_equity_assessment[axis].positive_findings}</p>
                    <p><strong>Concerns:</strong> {$currentPolicy.analysis_sections.general_equity_assessment[axis].concerns}</p>
                    <p><strong>Conclusion:</strong> {$currentPolicy.analysis_sections.general_equity_assessment[axis].conclusion}</p>
                </div>
            {/each}

            <hr />

            <h2>{$currentPolicy.analysis_sections.vulnerable_groups_analysis.title}</h2>
            <p>{$currentPolicy.analysis_sections.vulnerable_groups_analysis.summary}</p>
            <p><strong>Identified Groups and Impacts:</strong> {$currentPolicy.analysis_sections.vulnerable_groups_analysis.identified_groups_and_impacts}</p>
            <p><strong>Equity Assessment:</strong> {$currentPolicy.analysis_sections.vulnerable_groups_analysis.equity_assessment_summary}</p>
            <p><strong>Conclusion:</strong> {$currentPolicy.analysis_sections.vulnerable_groups_analysis.conclusion}</p>

            <hr />

            <h2>{$currentPolicy.analysis_sections.severity_impact_analysis.title}</h2>
            <p>{$currentPolicy.analysis_sections.severity_impact_analysis.summary}</p>
            <p><strong>High Severity Impacts:</strong> {$currentPolicy.analysis_sections.severity_impact_analysis.high_severity_impacts}</p>
            <p><strong>Moderate Severity Impacts:</strong> {$currentPolicy.analysis_sections.severity_impact_analysis.moderate_severity_impacts}</p>
            <p><strong>Equity Implications:</strong> {$currentPolicy.analysis_sections.severity_impact_analysis.equity_implications_of_impacts}</p>
            <p><strong>Conclusion:</strong> {$currentPolicy.analysis_sections.severity_impact_analysis.conclusion}</p>

            <hr />

            <h2>{$currentPolicy.analysis_sections.mitigation_strategies_analysis.title}</h2>
            <p>{$currentPolicy.analysis_sections.mitigation_strategies_analysis.summary}</p>
            <p><strong>Strategies:</strong> {$currentPolicy.analysis_sections.mitigation_strategies_analysis.identified_strategies}</p>
            <p><strong>Equity Assessment:</strong> {$currentPolicy.analysis_sections.mitigation_strategies_analysis.equity_assessment}</p>
            <p><strong>Conclusion:</strong> {$currentPolicy.analysis_sections.mitigation_strategies_analysis.conclusion}</p>

            <hr />

            <h2>{$currentPolicy.overall_summary_and_recommendations.title}</h2>
            <p><strong>Key Equity Gaps:</strong> {$currentPolicy.overall_summary_and_recommendations.key_equity_gaps}</p>
            <p><strong>Key Equity Strengths:</strong> {$currentPolicy.overall_summary_and_recommendations.key_equity_strengths}</p>
            <p><strong>Recommendations:</strong> {$currentPolicy.overall_summary_and_recommendations.recommendations}</p>
            <ExportButton />
        </div>
    {/if}

    <!-- (Test) Report Content
    {#if $currentPolicy?.document?.title}
        <div class="report-wrapper">
            <h1>{test.document.title}</h1>
            <p><strong>Filename:</strong> {test.document.filename}</p>
            <p><em>{test.document.shortDesc}</em></p>

            <hr />

            <h2>Policy Context</h2>
            <p>{test.policy_context.summary}</p>
            <ul>
                <li><strong>Jurisdiction:</strong> {test.policy_context.jurisdiction}</li>
                <li><strong>Enacted:</strong> {test.policy_context.enacted}</li>
                <li><strong>Key Actors:</strong> {test.policy_context.key_actors}</li>
            </ul>

            <hr />

            <h2>Equity Analysis by Perspective</h2>
            {#each test.equity_analysis_by_perspective as perspective}
                <div class="equity-perspective">
                    <h3>{perspective.group}</h3>
                    <p>
                        <strong>{perspective.general_equity_assessment.title}:</strong>
                        {perspective.general_equity_assessment.narrative}
                    </p>

                    {#each [
                        'recognitional_equity',
                        'procedural_equity',
                        'distributional_equity',
                        'structural_equity',
                        'transformational_equity'
                    ] as axis}
                        <div>
                            <h4>
                                {axis
                                    .replace('_equity', '')
                                    .replace('_', ' ')
                                    .replace(/\b\w/g, l => l.toUpperCase())}
                            </h4>
                            <p>{perspective[axis]?.description}</p>
                        </div>
                    {/each}
                </div>
            {/each}

            <hr />

            <h2>{test.vulnerable_groups_analysis.title}</h2>
            <p>{test.vulnerable_groups_analysis.detailed_summary}</p>
            <p><strong>Identified Groups and Impacts:</strong> {test.vulnerable_groups_analysis.identified_groups_and_impacts}</p>
            <p><strong>Equity Assessment:</strong> {test.vulnerable_groups_analysis.equity_assessment}</p>
            <p><strong>Conclusion:</strong> {test.vulnerable_groups_analysis.conclusion}</p>

            <hr />

            <h2>{test.severity_impact_analysis.title}</h2>
            <p>{test.severity_impact_analysis.expansive_summary}</p>
            <p><strong>Benefits:</strong> {test.severity_impact_analysis.detailed_impacts.benefits}</p>
            <p><strong>Burdens:</strong> {test.severity_impact_analysis.detailed_impacts.burdens}</p>
            <p><strong>Conclusion:</strong> {test.severity_impact_analysis.conclusion}</p>

            <hr />

            <h2>{test.mitigation_strategies.title}</h2>
            <p>{test.mitigation_strategies.description}</p>
            <p><strong>Conclusion:</strong> {test.mitigation_strategies.conclusion}</p>

            <hr />

            <h2>{test.overall_summary_and_recommendations.title}</h2>
            <p><strong>Key Equity Gaps:</strong> {test.overall_summary_and_recommendations.key_equity_gaps}</p>
            <p><strong>Key Equity Strengths:</strong> {test.overall_summary_and_recommendations.key_equity_strengths}</p>

            <ul>
                {#each test.overall_summary_and_recommendations.recommendations as rec}
                    <li>{rec}</li>
                {/each}
            </ul>

            <p><strong>Conclusion:</strong> {test.overall_summary_and_recommendations.narrative_conclusion}</p>

            <ExportButton />
        </div>
    {/if} --->

</section>
