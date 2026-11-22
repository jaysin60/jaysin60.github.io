/* ==========================================================================
   data.js  —  THE ONLY FILE YOU NORMALLY NEED TO EDIT
   ==========================================================================

   This site pulls your repositories live from the GitHub API, so anything new
   you push to https://github.com/jaysin60 will show up here automatically.

   Use the three things below to curate how they look:

   1. FEATURED      — repos pinned to the top, in this exact order.
   2. OVERRIDES     — nicer descriptions / tags / a custom link for any repo.
                      GitHub's own description is used when there's no override.
   3. HIDDEN        — repos you don't want on the page (large forks, etc).

   To add a project that is NOT on GitHub, add an object to FEATURED with a
   `url` field pointing anywhere (a demo, a write-up, a notebook, etc).

   Everything else (name, bio, experience, skills) lives in index.html.
   ========================================================================== */

window.SITE_DATA = {
  githubUser: 'jaysin60',

  /* 1. PINNED PROJECTS -----------------------------------------------------
     Add new objects here to feature them first. Only `repo` is required. */
  FEATURED: [
    { repo: 'looped-transformer' },
    { repo: 'cost-saver-claude-harness' },
    { repo: 'grooming' },
  ],

  /* 2. CUSTOM COPY ---------------------------------------------------------
     Key = exact repository name. Any field is optional. */
  OVERRIDES: {
    'looped-transformer': {
      blurb:
        'Turning a pretrained coding LM into a looped (latent-recurrent) transformer. A laptop/Colab-scale reproduction of the Dory1.0 idea: split the model into input / recurrent / output blocks, apply the shared block k times, train with loop-count sampling + TBPTL + LoRA. Includes honest small-scale results — even the negative one.',
      tags: ['PyTorch', 'LLM Research', 'LoRA', 'Colab'],
      badge: 'Research',
    },
    'cost-saver-claude-harness': {
      blurb:
        'A Claude Code plugin that keeps expensive models for judgment and routes mechanical work to cheap ones. Five model-tiered agents plus a live dashboard showing every subagent, tool call and token — so you can see where the spend is actually going.',
      tags: ['TypeScript', 'Claude Code', 'Agents', 'Cost Ops'],
      badge: 'Tooling',
    },
    grooming: {
      blurb:
        'A small Python package for cleaning up messy text — strips the extra lines and noise out of code and documents. Built purely on nltk and re, with no heavy dependencies.',
      tags: ['Python', 'NLP', 'nltk'],
    },
    jevgrep: {
      blurb:
        'Find code by asking what it does. A CLI for coding agents that discovers relevant files and source context instead of dumping raw grep output into the context window.',
      tags: ['TypeScript', 'CLI', 'Dev Tools'],
    },
    'opensearch-late-interaction': {
      blurb:
        'OpenSearch plugin for late-interaction retrieval models (ColBERT / ColPali / ColQwen). Exploration of multi-vector retrieval inside an OpenSearch index.',
      tags: ['Java', 'OpenSearch', 'Retrieval'],
    },
  },

  /* 3. REPOS TO LEAVE OFF THE PAGE ---------------------------------------- */
  HIDDEN: ['spark'], // plain fork of apache/spark, not my own work

  /* Fallback shown if the GitHub API is unreachable / rate-limited.
     Handy for viewing the page offline. Keep roughly in sync with above. */
  OFFLINE_PROJECTS: [
    {
      name: 'looped-transformer',
      html_url: 'https://github.com/jaysin60/looped-transformer',
      language: 'Python',
      fork: false,
      stargazers_count: 0,
    },
    {
      name: 'cost-saver-claude-harness',
      html_url: 'https://github.com/jaysin60/cost-saver-claude-harness',
      language: 'TypeScript',
      fork: false,
      stargazers_count: 0,
    },
    {
      name: 'grooming',
      html_url: 'https://github.com/jaysin60/grooming',
      language: 'Python',
      fork: false,
      stargazers_count: 0,
    },
    {
      name: 'jevgrep',
      html_url: 'https://github.com/jaysin60/jevgrep',
      language: 'TypeScript',
      fork: true,
      stargazers_count: 0,
    },
    {
      name: 'opensearch-late-interaction',
      html_url: 'https://github.com/jaysin60/opensearch-late-interaction',
      language: 'Java',
      fork: true,
      stargazers_count: 0,
    },
  ],
};
