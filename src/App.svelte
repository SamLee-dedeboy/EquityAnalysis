<script>
  // SPA Router for Svelte, Navbar
  import Router from 'svelte-spa-router';

  // Navbar, Routing
  import LogoBar from './lib/LogoBar.svelte';
  import PolicyGallery from './routes/PolicyGallery.svelte';
  import AnalysisView from './routes/AnalysisView.svelte';
  import Tool from './routes/Tool.svelte';
  import InfoView from './routes/InfoView.svelte';
  const routes = { '/': PolicyGallery, '/aview': AnalysisView, '/tool': Tool, '/info': InfoView };
</script>

<style>
  main {
    padding: 1.75rem;
    font-family: 'Inter', system-ui, sans-serif;
  }
</style>

<!-- Main Application Component -->
<LogoBar />

<!-- This <Router> replaces the content dynamically based on URL -->
<main>
  <Router {routes} />
</main>

