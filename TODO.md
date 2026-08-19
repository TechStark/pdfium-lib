# npm package publishing improvement plan

## Status

- [x] Add automatic npm versioning based on workflow run metadata
- [x] Improve package README with install and usage examples
- [x] Add a fresh-install smoke test for the published package
- [ ] Reduce GitHub Actions runtime for the wasm workflow
- [ ] Add a minimal wrapper API for easier consumption
- [ ] Switch initial publish to a prerelease/dist-tag flow (for example `beta`)
- [ ] Add release notes / publish documentation

## Current focus

### 1. Reduce GitHub Actions runtime for the wasm workflow (highest priority)

- [x] Move the fresh-install smoke test out of the default build path so normal pushes are faster
- [x] Cache EMSDK and pip dependencies where practical
- [x] Cache depot tools so repeated runs do not re-download the toolchain unnecessarily
- [x] Cache reusable wasm build outputs across workflow reruns so repeated runs can skip the expensive PDFium/build phases when source inputs are unchanged
- [ ] Reuse build artifacts between packaging and publish jobs
- [ ] Keep the workflow fast enough for frequent iteration while preserving release safety

### 3. Improve package README and usage documentation

- Add installation instructions for Node.js and browsers
- Add a short example showing how to load the generated module
- Clarify that this package ships raw WASM bindings and is not a high-level PDF SDK
- Mention current limitations and the repository link

### 2. Add a fresh-install smoke test

- Create a temporary directory
- Install the generated package from the local tarball or package directory
- Run a minimal import/require check

### 3. Add a minimal wrapper API

- Provide a small `loadPdfium` or `createPdfiumModule` helper
- Keep it intentionally thin and low-risk

### 4. Publish flow polish

- Publish the first public release under a prerelease tag such as `beta`
- Add a short release note template for future publishes

The `@hyzyla/pdfium` package needs updated TypeScript definitions.

Create `pdfium-custom.d.ts`:
```typescript
export interface PDFium {
  // ... existing definitions ...
  
  // Character positioning APIs
  _FPDFText_GetCharBox: (
    textPage: number,
    index: number,
    leftPtr: number,
    rightPtr: number,
    bottomPtr: number,
    topPtr: number
  ) => number;
  
  _FPDFText_GetFontSize: (textPage: number, index: number) => number;
  
  _FPDFText_GetCharOrigin: (
    textPage: number,
    index: number,
    xPtr: number,
    yPtr: number
  ) => number;
  
  // ... other new functions ...
}
```

---

### Task 5: Documentation

Create documentation for the new APIs:

```markdown
## Character Positioning APIs

### FPDFText_GetCharBox
Gets the tight bounding box of a character.

**Parameters:**
- `textPage` - Handle from FPDFText_LoadPage
- `index` - Character index (0-based)
- `left, right, bottom, top` - Pointers to receive coordinates (PDF user space)

**Returns:**
- Non-zero on success, 0 on failure

**Example:**
```javascript
const leftPtr = wasm.malloc(8 * 4);
wasm._FPDFText_GetCharBox(textPage, charIndex, leftPtr, leftPtr+8, leftPtr+16, leftPtr+24);

const left = wasm.HEAPF64[leftPtr / 8];
const right = wasm.HEAPF64[(leftPtr + 8) / 8];
const bottom = wasm.HEAPF64[(leftPtr + 16) / 8];
const top = wasm.HEAPF64[(leftPtr + 24) / 8];

wasm.free(leftPtr);
```

**User Space Coordinates:**
- Origin at bottom-left of page
- Units in points (1/72 inch)
- Y-axis points upward

**To convert to screen coordinates:**
```javascript
screenY = pageHeight - pdfY;  // Flip Y axis
screenX = pdfX;               // No change
```
```

---

## Technical Reference

### PDFium C API Documentation

All functions are documented in the PDFium source:
- Repository: https://pdfium.googlesource.com/pdfium/
- Header: `public/fpdf_text.h`

### Function Signatures

```c
// Get tight bounding box
FPDF_BOOL FPDFText_GetCharBox(FPDF_TEXTPAGE text_page,
                               int index,
                               double* left,
                               double* right,
                               double* bottom,
                               double* top);

// Get origin point
FPDF_BOOL FPDFText_GetCharOrigin(FPDF_TEXTPAGE text_page,
                                  int index,
                                  double* x,
                                  double* y);

// Get font size
double FPDFText_GetFontSize(FPDF_TEXTPAGE text_page, int index);

// Get font information
unsigned long FPDFText_GetFontInfo(FPDF_TEXTPAGE text_page,
                                    int index,
                                    void* buffer,
                                    unsigned long buflen,
                                    int* flags);

// Get character angle (rotation)
double FPDFText_GetCharAngle(FPDF_TEXTPAGE text_page, int index);

// Get character at position
int FPDFText_GetCharIndexAtPos(FPDF_TEXTPAGE text_page,
                                double x,
                                double y,
                                double xTolerance,
                                double yTolerance);

// Get transformation matrix
FPDF_BOOL FPDFText_GetMatrix(FPDF_TEXTPAGE text_page,
                              int index,
                              FS_MATRIX* matrix);
```

---

## Notes

### Important Considerations

1. **Memory Management** - All pointer parameters require memory allocation via `wasmExports.malloc()` and must be freed with `free()`

2. **Coordinate System** - PDF uses bottom-left origin with Y increasing upward. Must convert to screen coordinates (top-left, Y down)

3. **UTF-16 Encoding** - Text returned by `_FPDFText_GetText` is UTF-16 encoded in WASM memory

4. **Thread Safety** - PDFium is NOT thread-safe. All operations must be on the main thread

5. **Error Handling** - Functions return 0 on failure. Always check return values

### Build Time

Building PDFium WASM takes approximately:
- First build: 30-60 minutes (depending on machine)
- Subsequent builds: 5-10 minutes (incremental)

### Known Limitations

- The character positioning APIs may not work correctly for:
  - Type 3 fonts (custom glyph rendering)
  - Very old PDFs without proper text extraction
  - Embedded fonts with incomplete glyph info

---

## Contact & Resources

### Related Projects

- **PDF Editor**: `C:\code\github\embed-pdf-editor`
- **PDFium Repository**: https://pdfium.googlesource.com/pdfium/
- **@hyzyla/pdfium**: https://github.com/hyzyla/pdfium

### Key Files Modified

- `extras/wasm/utils/function-names.js` - Added function exports
- `packages/editor/src/engine/pdfium/low-level.ts` - Client-side integration
- `packages/editor/src/engine/text/char-extractor.ts` - Character extraction logic

### Questions?

Refer to:
- PDFium API docs: https://pdfium.googlesource.com/pdfium/+/refs/heads/main/public/
- Emscripten docs: https://emscripten.org/docs/api_reference/
- PDF spec (ISO 32000): For understanding PDF coordinate systems

---

## Checklist

- [ ] Task 1: Build custom WASM
- [ ] Task 2: Create and run test page
- [ ] Task 3: Integrate with @hyzyla/pdfium
- [ ] Task 4: Add TypeScript definitions
- [ ] Task 5: Write API documentation
- [ ] Verify character positions align with rendered PDF
- [ ] Test on multiple PDF files (simple, complex, scanned)
- [ ] Update embed-pdf-editor to use custom build
- [ ] Performance testing (large PDFs)

---

**Last Updated**: 2026-08-17
**Status**: In Progress - Awaiting WASM build
