# PDFium-lib Character Positioning APIs Enhancement

## Background

We are building a PDF editor (https://github.com/user/embed-pdf-editor) that requires accurate character-level text positioning for features like:

1. **Text Selection Overlay** - Blue highlight boxes when selecting text should align perfectly with rendered PDF text
2. **Search with Highlight** - Highlighting search results accurately
3. **Accessible Text Layers** - Screen readers need precise text positions

### The Problem

Currently, `@hyzyla/pdfium` (which wraps pdfium-lib) only exposes basic text APIs:
- `_FPDFText_LoadPage` - Load text page
- `_FPDFText_CountChars` - Count characters  
- `_FPDFText_GetText` - Get text content

But it does **NOT** expose character positioning APIs like `FPDFText_GetCharBox`, which are essential for:
- Getting bounding box of each character (x, y, width, height)
- Building text selection layers
- Accurate font metrics

### Current Workaround

The editor currently uses heuristic positioning (estimating positions based on margins and font sizes), but this is inaccurate for:
- Complex layouts (multi-column, tables)
- Proper kerning
- Rotated text
- Real PDF with varying fonts

## What Was Done

### 1. Modified `extras/wasm/utils/function-names.js`

Added the following functions to the export list:

```javascript
const additionalFunctions = [
  'FPDFText_GetCharBox',        // Get tight bounding box of a character
  'FPDFText_GetLooseCharBox',   // Get loose bounding box covering entire glyph  
  'FPDFText_GetCharOrigin',     // Get origin point of a character (for cursor)
  'FPDFText_GetFontSize',       // Get font size of a character
  'FPDFText_GetFontInfo',       // Get font name and flags
  'FPDFText_GetCharAngle',      // Get rotation angle of a character
  'FPDFText_GetCharIndexAtPos', // Get character index at a position
  'FPDFText_GetTextRenderMode', // Get text rendering mode
  'FPDFText_GetMatrix',         // Get transformation matrix
];
```

**Commit**: `d1517bc` - "feat: add FPDFText character positioning APIs for accurate text selection"

## TODO Tasks

### Task 1: Build and Test Custom WASM

**Steps:**

1. Ensure build environment is ready:
   ```bash
   # Requirements:
   # - Python 3.x
   # - depot_tools (gclient, gn, ninja)
   # - Emscripten SDK (emsdk)
   # - Node.js
   # - Doxygen
   ```

2. Build PDFium for WASM:
   ```bash
   cd C:\code\github\pdfium-lib
   python make.py run task build-pdfium target=wasm
   ```

3. Generate WASM bindings:
   ```bash
   python make.py run task generate target=wasm config=release
   ```

4. Verify functions are exported:
   ```bash
   # Check generated JS file contains our functions
   grep "FPDFText_GetCharBox" build/emscripten/wasm/release/node/pdfium.js
   ```

**Success Criteria:**
- WASM builds without errors
- `pdfium.js` and `pdfium.wasm` are generated
- All 9 new functions are present in the export list

---

### Task 2: Create Test Page

Create a simple test to verify the new APIs work:

```html
<!-- test-char-position.html -->
<!DOCTYPE html>
<html>
<head>
    <title>FPDFText_GetCharBox Test</title>
</head>
<body>
    <h1>Character Position Test</h1>
    <input type="file" id="pdfFile" accept=".pdf">
    <canvas id="pdfCanvas"></canvas>
    <pre id="output"></pre>

    <script type="module">
        import { PDFiumLibrary } from './build/emscripten/wasm/release/node/pdfium.esm.js';
        
        document.getElementById('pdfFile').addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;
            
            const buffer = await file.arrayBuffer();
            const library = await PDFiumLibrary.init();
            const doc = await library.loadDocument(new Uint8Array(buffer));
            const page = doc.getPage(0);
            
            // Get text page
            const textPage = library.module._FPDFText_LoadPage(page._pageIdx);
            
            // Get character positions using new API
            const charCount = library.module._FPDFText_CountChars(textPage);
            
            const output = document.getElementById('output');
            output.textContent = `Characters: ${charCount}\n\n`;
            
            // Allocate memory for doubles
            const ptr = library.module.wasmExports.malloc(8 * 4);
            
            for (let i = 0; i < Math.min(10, charCount); i++) {
                // Call FPDFText_GetCharBox
                const result = library.module._FPDFText_GetCharBox(
                    textPage, i, ptr, ptr+8, ptr+16, ptr+24
                );
                
                if (result) {
                    const left = library.module.HEAPF64[ptr/8];
                    const right = library.module.HEAPF64[(ptr+8)/8];
                    const bottom = library.module.HEAPF64[(ptr+16)/8];
                    const top = library.module.HEAPF64[(ptr+24)/8];
                    
                    output.textContent += `Char ${i}: (${left}, ${bottom}) - (${right}, ${top})\n`;
                }
            }
            
            library.module.wasmExports.free(ptr);
            library.module._FPDFText_ClosePage(textPage);
            doc.destroy();
            library.destroy();
        });
    </script>
</body>
</html>
```

**Success Criteria:**
- Test page loads PDF successfully
- Character bounding boxes are printed to console
- No JavaScript errors about missing functions

---

### Task 3: Integrate with @hyzyla/pdfium

Two options:

**Option A: Publish as separate package**
```bash
# Create package.json
npm init -y
# Name: @yourname/pdfium with character APIs
# Version: 2.1.14-custom

# Publish to npm (private or public)
npm publish
```

**Option B: Local replacement**
```bash
# Copy built files to embed-pdf-editor project
cp build/emscripten/wasm/release/node/* \
   C:\code\github\embed-pdf-editor\node_modules\.pnpm\@hyzyla+pdfium@2.1.13\node_modules\@hyzyla\pdfium\dist\
```

Update `embed-pdf-editor` to use the custom build in `package.json`:
```json
{
  "dependencies": {
    "@hyzyla/pdfium": "file:../pdfium-lib/build/emscripten/wasm/release"
  }
}
```

---

### Task 4: Update Type Definitions

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
