<script>
    //Local Modules
    import BackButton from "../lib/BackButton.svelte";
    // src/lib/stores.js
    import { currentPolicy } from '../lib/stores/currentPolicy.js';

    const equities = [
        {
            name: 'Procedural',
            color: '#227C9D',
            description: 'Fair and inclusive processes in policy development, implementation, and enforcement. Ensures all stakeholders have meaningful participation opportunities.',
            keyElements: ['Transparent processes', 'Community engagement', 'Accessible participation'],
            assessmentAreas: ['Decision making processes', 'Stakeholder involvement', 'Information accessibility']
        },
        {
            name: 'Structural',
            color: '#17C3B2',
            description: 'Addresses underlying systems and institutions that create inequities. Focuses on reforming organizational structures, legal frameworks, and policies that systematically advantage some groups while disadvantaging others.',
            keyElements: ['Institutional analysis', 'Policy framework', 'System redesign'],
            assessmentAreas: ['Institutional barriers', 'Policy coherence', 'Structure reform']
        },
        {
            name: 'Distributional',
            color: '#FFCB77',
            description: 'Fair allocation of benefits, burdens, and resources. Examines who gets what, when, and how much in policy outcomes.',
            keyElements: ['Resource allocation', 'Benefit distribution', 'Burden sharing'],
            assessmentAreas: ['Impact distribution', 'Access patterns', 'Outcome Disparities']
        },
        {
            name: 'Recognitional',
            color: '#FEB3B1',
            description: 'Recognition of historical, cultural, and social contexts that shape communities’ relationships with water resources and governance.',
            keyElements: ['Cultural recognition', 'Identity affirmation', 'Diverse Perspectives'],
            assessmentAreas: ['Representation analysis', 'Cultural competency', 'Bias identification']
        },
        {
            name: 'Transformational',
            color: '#FE6D73',
            description: 'Goes beyond fixing current systems to fundamentally reimagining them. Create new approaches that center equity from the ground up, building regenerative systems that prevent inequities from occurring.',
            keyElements: ['System transformation', 'Root cause analysis', 'Power redistribution'],
            assessmentAreas: ['Systemic barriers', 'Innovation potential', 'Long term impact']
        }
    ];

</script>

<style>

    /* General Styles */
    .container { max-width: 900px; margin: auto; padding: 2rem; font-family: 'Inter', sans-serif; }

    /* Header and Subtitle */
    .header { text-align: center; margin-bottom: 2rem; }
    .header h1 { font-size: 3rem; font-weight: 700; margin-top: -75px;}
    .header h3 { font-size: 1.5rem; }
    .header p { font-size: 1rem; margin-bottom: 2rem; margin-top: -1rem; color: #333; }

    /* Equity Cards */
    .equity-card { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; background: #EDEDED; border-radius: 12px; }
    .equity-info { padding: 1rem; flex: 1; }

    .chip-groups { display: flex; gap: 2rem; padding: 0.5rem 0; }
    .chip-group, .chip-group * { color: #fff !important; }
    .chip-group { display: flex; flex-wrap: wrap; border-radius: 12px; padding: 0.75rem;}

    .section-title {font-size: 0.8rem; padding: 0.2rem; margin: -0.5rem 0  -0.5rem 5px; }
    .chip-group ul { padding: 0.2rem; padding-top: 0.3rem; margin: 0; font-size: 0.8rem; margin-left: 20px; }
    
    .label { color: #fff; font-weight: 700; padding: 1rem; min-width: 150px; border-radius: 8px; text-align: center; font-size: 1.5rem;}

    /* CTA Section */
    .cta-section { background: #0F3C5F; color: white; border-radius: 12px; padding: 2rem; text-align: center; margin-top: 3rem; }
    .cta-buttons { display: flex; gap: 1rem; justify-content: center; margin-top: 1.5rem; }
    .cta-buttons button { padding: 12px 20px; font-size: 1rem; border: none; border-radius: 6px; cursor: pointer; }
    .cta-buttons .secondary { background: white; color: #0F3C5F; border: 2px solid #fff; }
    .cta-buttons .primary { background: #0F3C5F; color: white; border: 2px solid #fff; }

    @media (max-width: 700px) { .equity-card { flex-direction: column; align-items: flex-start; } .label { width: 100%; } }

</style>
<section>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <div class="container">
        <BackButton />
        <!-- Header -->
        <div class="header">
            <h1> 
                <img src="../../public/dark-tree.png" alt="COEQWAL equity framework information" />
                <span style="color:#0F3C5F">Equity</span> Framework
            </h1>
            <p>
                Our comprehensive equity framework encompasses five critical dimensions that guide policy analysis and ensure inclusive outcomes. 
                Each dimension provides a unique lens for evaluating fairness, justice, and systemic impact across diverse communities. 
            </p>
            <h3>
                The Five Equities
                <span style="display: inline-flex; align-items: center; gap: 0.25em; margin-left: -0.15em;">
                <img src="public/down-arrow.png" alt="Down Arrow" style="height: 0.9em; position: relative; top: 0.1em;">
                </span>
            </h3>
        </div>

        <!-- Equity Cards -->
        {#each equities as equity}
            <div class="equity-card">

                <!-- Description and Bullet-points -->
                <div class="equity-info">
                    <p style="margin-bottom: 1rem;">{equity.description}</p>
                    <div class="chip-groups">
                        <div class="chip-group" style="background: {equity.color}; flex-direction: column; align-items: flex-start; width: 100%;">
                            <div class="section-title">Key Elements</div>
                            <ul>
                                {#each equity.keyElements as key}
                                    <li>{key}</li>
                                {/each}
                            </ul>
                        </div>
                        <div class="chip-group" style="background: {equity.color}; flex-direction: column; align-items: flex-start; width: 100%;">
                            <div class="section-title">Assessment Areas</div>
                            <ul>
                                {#each equity.assessmentAreas as area}
                                    <li>{area}</li>
                                {/each}
                            </ul>
                        </div>
                    </div>

                </div>
                <!-- Label Containers -->
                <div class="label" style="background: {equity.color}; align-self: stretch; display: flex; align-items: center; justify-content: center; min-width: 250px;">
                    {equity.name}
                </div>

            </div>
        {/each}

        <!-- CTA Section-->
        <div class="cta-section">
            <h2>Ready to apply the Framework?</h2>
            <p>Use our AI-powered tools to analyze your policies through these five equity dimensions and get actionable insights for more inclusive outcomes.</p>
            <div class="cta-buttons">
                <button class="secondary" on:click={() => window.location.hash = '#/aview'}>View Sample Analysis</button>
                <button class="primary" on:click={() => window.location.hash = '#/tool'}>Get Started with EquiFlow</button>
            </div>
        </div>

    </div>

</section>
