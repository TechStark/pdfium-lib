# Publishing the WASM npm package

This repository can build a WASM package and publish it to npm from the GitHub Actions workflow.

## What the workflow does

The `WASM` workflow now performs the following steps:

1. Build the PDFium WASM artifacts.
2. Package the generated files into an npm-ready directory.
3. Run a local smoke test against the packaged output.
4. Upload the package as a workflow artifact.
5. Optionally publish to npm when the workflow is started manually with `publish_to_npm=true`.

## Publishing from GitHub Actions

1. Open the Actions tab for the `WASM` workflow.
2. Choose `Run workflow`.
3. Select the target branch.
4. Set `publish_to_npm` to `true`.
5. Start the workflow.

The publish job uses npm OIDC provenance instead of a long-lived token:

```yaml
permissions:
  contents: read
  id-token: write
```

## Versioning

The workflow generates the npm package version automatically from workflow metadata to avoid manual version entry during repeated publishes.

The package version is based on:

- `github.run_number`
- `github.run_attempt`

This keeps publish iterations simple while still producing a unique version each time.

## Release notes template

Use the following template for future npm publishes:

```md
## Release notes

- Build: <link to workflow run>
- Package: @techstark/pdfium
- Version: <generated version>
- Summary: <one sentence>
- Notes:
  - <bullet 1>
  - <bullet 2>
```

## Notes

- The package currently ships the generated WASM bindings and runtime artifacts directly.
- It is intended as a low-level package rather than a high-level PDF SDK.
- For release safety, the workflow validates the package locally before publishing.
