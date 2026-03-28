# Plan: Add great-docs integration

## Great-Docs commands

```
Usage: great-docs [OPTIONS] COMMAND [ARGS]...

  Great Docs - Beautiful documentation for Python packages.

  Great Docs generates professional documentation sites with auto-generated
  API references, CLI documentation, smart navigation, and modern styling.

  Get started with 'great-docs init' to set up your docs, then use 'great-docs
  build' to generate your site.

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  init                Initialize great-docs in your project (one-time...
  build               Build your documentation site.
  preview             Preview your documentation locally.
  uninstall           Remove great-docs from your project.
  config              Generate a great-docs.yml configuration file.
  scan                Discover package exports and preview what can be...
  setup-github-pages  Set up automatic deployment to GitHub Pages.
  check-links         Check for broken links in source code and...
  changelog           Generate a Changelog page from GitHub Releases.
  proofread           Check spelling and grammar in documentation files...
  seo                 Audit SEO health of your documentation site.
  lint                Lint documentation quality for your package.
```


## Build command
- `great-docs build`

## Preview command
- `great-docs preview`

### Task 1: Implement feature
- [ ] Add quarto to pyproject and rebuild local install
- [ ] Build site with great-docs and start local preview 
