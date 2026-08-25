/**
 * Main Application Controller for Non-AI Alkanz Unicode Document Converter
 * 100% Deterministic Document Converter for .docx, .txt, and .pdf
 */

document.addEventListener('DOMContentLoaded', () => {
    const ruleManager = new RuleManager('rules-grid', 'preset-select');
    const editor = new TextEditor('input-editor', 'output-editor', 'font-select', 'replacement-stats');
    const PUNCTUATION_SET = new Set(['،', '؛', '.', ':', '!', '؟', '"', '(', ')', '[', ']', '•']);

    // Register rule change callback
    window.onRuleChanged = () => {
        performLiveConversion();
    };

    loadCustomFonts();
    setupInputEvents();
    setupFontUpload();
    setupActions();

    function setupFontUpload() {
        const btnUploadFont = document.getElementById('btn-upload-font');
        const fontFileInput = document.getElementById('font-file-input');

        if (btnUploadFont && fontFileInput) {
            btnUploadFont.addEventListener('click', () => fontFileInput.click());
            fontFileInput.addEventListener('change', async (e) => {
                if (e.target.files && e.target.files.length > 0) {
                    await uploadFontFile(e.target.files[0]);
                    e.target.value = '';
                }
            });
        }
    }

    async function uploadFontFile(file) {
        updateStatus(`Uploading custom font ${file.name}...`, true);
        try {
            const formData = new FormData();
            formData.append('file', file);

            const res = await fetch('/api/upload-font', {
                method: 'POST',
                body: formData
            });

            const data = await res.json();
            if (data.success) {
                injectFontFace(data.font_name, data.url);
                addFontOption(data.font_name, true);
                updateStatus(`Font ${data.font_name} added successfully!`, false);
            } else {
                alert("Error uploading font: " + (data.detail || "Unknown error"));
            }
        } catch (err) {
            console.error("Font upload error:", err);
            alert("Font upload failed: " + err.message);
        } finally {
            updateStatus("Ready for instant conversion", false);
        }
    }

    async function loadCustomFonts() {
        try {
            const res = await fetch('/api/fonts');
            const data = await res.json();
            if (data.success && data.fonts) {
                const optGroup = document.getElementById('optgroup-custom-fonts');
                if (optGroup) optGroup.innerHTML = '';
                data.fonts.forEach(f => {
                    injectFontFace(f.font_name, f.url);
                    addFontOption(f.font_name, false);
                });
            }
        } catch (e) {
            console.error("Error loading fonts:", e);
        }
    }

    function injectFontFace(fontName, fontUrl) {
        const styleId = `font-face-${fontName.replace(/\s+/g, '-')}`;
        if (document.getElementById(styleId)) return;
        const style = document.createElement('style');
        style.id = styleId;
        style.appendChild(document.createTextNode(`
            @font-face {
                font-family: '${fontName}';
                src: url('${fontUrl}');
                font-weight: normal;
                font-style: normal;
            }
        `));
        document.head.appendChild(style);
    }

    function addFontOption(fontName, selectIt) {
        const optGroup = document.getElementById('optgroup-custom-fonts');
        const fontSelect = document.getElementById('font-select');
        if (!optGroup || !fontSelect) return;

        let opt = Array.from(fontSelect.options).find(o => o.value === fontName);
        if (!opt) {
            opt = document.createElement('option');
            opt.value = fontName;
            opt.textContent = fontName;
            optGroup.appendChild(opt);
        }

        if (selectIt) {
            fontSelect.value = fontName;
            editor.setFont(fontName);
        }
    }

    function setupInputEvents() {
        const outputEditor = document.getElementById('output-editor');
        if (outputEditor) {
            outputEditor.addEventListener('input', () => {
                performLiveConversion();
            });
        }

        const btnUploadTop = document.getElementById('btn-upload-top');
        const fileInput = document.getElementById('file-input');
        if (btnUploadTop && fileInput) {
            btnUploadTop.addEventListener('click', () => fileInput.click());
        }
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                if (e.target.files && e.target.files.length > 0) {
                    uploadAndConvertFile(e.target.files[0]);
                    e.target.value = '';
                }
            });
        }

        const btnUploadPane = document.getElementById('btn-upload-pane');
        const fileInputPane = document.getElementById('file-input-pane');
        if (btnUploadPane && fileInputPane) {
            btnUploadPane.addEventListener('click', () => fileInputPane.click());
        }
        if (fileInputPane) {
            fileInputPane.addEventListener('change', (e) => {
                if (e.target.files && e.target.files.length > 0) {
                    uploadAndConvertFile(e.target.files[0]);
                    e.target.value = '';
                }
            });
        }

        const btnPasteInput = document.getElementById('btn-paste-input');
        if (btnPasteInput) {
            btnPasteInput.addEventListener('click', async () => {
                try {
                    const clipboardText = await navigator.clipboard.readText();
                    if (clipboardText) {
                        editor.setOutputText(clipboardText);
                        performLiveConversion();
                        updateStatus("Text pasted from clipboard successfully!", false);
                    } else {
                        alert("Clipboard is empty! No text found.");
                    }
                } catch (err) {
                    console.error("Clipboard paste error:", err);
                    alert("You can use Ctrl+V or Cmd+V to paste text directly into the text editor.");
                }
            });
        }

        const btnFixSpaced = document.getElementById('btn-fix-spaced');
        if (btnFixSpaced) {
            btnFixSpaced.addEventListener('click', () => {
                const currentText = editor.getOutputText();
                if (!currentText) return;
                const lines = currentText.split('\n');
                const fixed = lines.map(line => rejoinSpacedArabicLetters(line));
                editor.setOutputText(fixed.join('\n'));
                updateStatus("Disconnected letter spaces rejoined successfully!", false);
            });
        }

        const btnReverseFlow = document.getElementById('btn-reverse-flow');
        if (btnReverseFlow) {
            btnReverseFlow.addEventListener('click', () => {
                const currentText = editor.getOutputText();
                if (!currentText) return;
                const lines = currentText.split('\n');
                const flipped = lines.map(line => fixWordReversedLine(line));
                editor.setOutputText(flipped.join('\n'));
                updateStatus("Word flow flipped per line successfully!", false);
            });
        }

        const btnReverseLines = document.getElementById('btn-reverse-lines');
        if (btnReverseLines) {
            btnReverseLines.addEventListener('click', () => {
                const currentText = editor.getOutputText();
                if (!currentText) return;
                const lines = currentText.split('\n');
                lines.reverse();
                editor.setOutputText(lines.join('\n'));
                updateStatus("Vertical line order reversed (top-to-bottom)!", false);
            });
        }

        // Drag and drop events
        const dropZone = document.getElementById('input-drop-zone');
        const dropOverlay = document.getElementById('drop-overlay');

        if (dropZone) {
            ['dragenter', 'dragover'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    if (dropOverlay) dropOverlay.classList.remove('hidden');
                }, false);
            });

            ['dragleave', 'drop'].forEach(eventName => {
                dropZone.addEventListener(eventName, (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    if (dropOverlay) dropOverlay.classList.add('hidden');
                }, false);
            });

            dropZone.addEventListener('drop', (e) => {
                const dt = e.dataTransfer;
                const files = dt ? dt.files : null;
                if (files && files.length > 0) {
                    uploadAndConvertFile(files[0]);
                }
            }, false);
        }
    }

    function sanitizeText(text) {
        if (!text) return "";
        const clean = text.replace(/\r\n/g, '\n').replace(/\r/g, '\n');
        return clean.replace(/[\u200e\u200f\ufeff\u202a-\u202e\xa0]/g, '');
    }

    function rejoinSpacedArabicLetters(line) {
        const cleanLine = line.replace(/ـ/g, '').replace(/\u200c/g, '').replace(/\u200d/g, '');
        if (!cleanLine.trim()) return "";
        const tokens = cleanLine.trim().split(/\s+/);
        const merged = [];
        let buffer = "";

        for (let tok of tokens) {
            const cleanT = tok.replace(/[^\w]/g, '');
            const hasArabic = /[\u0600-\u06ff]/.test(cleanT);
            const isSingleLetter = hasArabic && cleanT.length <= 1;

            if (isSingleLetter) {
                buffer += tok;
            } else {
                if (buffer) {
                    merged.push(buffer);
                    buffer = "";
                }
                merged.push(tok);
            }
        }
        if (buffer) merged.push(buffer);
        return merged.join(' ');
    }

    function fixWordReversedLine(line) {
        if (!line || !line.trim()) return "";
        const tokens = line.trim().split(/\s+/);
        if (tokens.length <= 1) return line.trim();

        tokens.reverse();

        const cleaned = tokens.map(tok => {
            let leading = "";
            let core = tok;
            while (core.length > 1 && PUNCTUATION_SET.has(core[0])) {
                leading += core[0];
                core = core.slice(1);
            }
            return core + leading;
        });

        let res = cleaned.join(' ');
        res = res.replace(/\s+([،؛.:!?])/g, '$1');
        return res.replace(/\s+/g, ' ').trim();
    }

    function performLiveConversion() {
        const rawText = editor.getOutputText();
        if (!rawText) {
            editor.setStats(0);
            return;
        }

        const rules = ruleManager.getRules();
        let converted = sanitizeText(rawText);
        let count = 0;

        const sortedKeys = Object.keys(rules).sort((a, b) => b.length - a.length);

        for (let src of sortedKeys) {
            if (!src) continue;
            const tgt = rules[src];
            const occurrences = (converted.split(src).length - 1);
            if (occurrences > 0) {
                converted = converted.split(src).join(tgt);
                count += occurrences;
            }
        }

        editor.setOutputText(converted);
        editor.setStats(count);
    }

    function showPreloader(titleText, subText) {
        const preloader = document.getElementById('upload-preloader');
        const titleEl = document.getElementById('preloader-title');
        const subEl = document.getElementById('preloader-subtext');
        const percentEl = document.getElementById('preloader-percent-text');
        const circlePath = document.getElementById('preloader-progress-circle');

        if (!preloader) return;
        if (titleText && titleEl) titleEl.textContent = titleText;
        if (subText && subEl) subEl.textContent = subText;

        if (percentEl) percentEl.textContent = '0%';
        if (circlePath) circlePath.setAttribute('stroke-dasharray', '0, 100');

        preloader.classList.remove('hidden');

        let currentPct = 0;
        if (window.preloaderInterval) clearInterval(window.preloaderInterval);
        
        window.preloaderInterval = setInterval(() => {
            if (currentPct < 90) {
                currentPct += Math.floor(Math.random() * 15) + 10;
                if (currentPct > 90) currentPct = 90;
                if (percentEl) percentEl.textContent = `${currentPct}%`;
                if (circlePath) circlePath.setAttribute('stroke-dasharray', `${currentPct}, 100`);
            }
        }, 150);
    }

    function hidePreloader() {
        const preloader = document.getElementById('upload-preloader');
        const percentEl = document.getElementById('preloader-percent-text');
        const circlePath = document.getElementById('preloader-progress-circle');

        if (window.preloaderInterval) clearInterval(window.preloaderInterval);

        if (percentEl) percentEl.textContent = '100%';
        if (circlePath) circlePath.setAttribute('stroke-dasharray', '100, 100');

        setTimeout(() => {
            if (preloader) preloader.classList.add('hidden');
        }, 250);
    }

    async function uploadAndConvertFile(file) {
        updateStatus(`Uploading & extracting ${file.name}...`, true);
        showPreloader("Extracting & Converting Document...", "Applying Lisan al-Dawat rules and preserving original layout");

        try {
            const presetSelect = document.getElementById('preset-select');
            const preset = presetSelect ? presetSelect.value : 'alkanz_normal';
            const customRules = JSON.stringify(ruleManager.getRules());

            const formData = new FormData();
            formData.append('file', file);
            formData.append('preset', preset);
            formData.append('custom_rules_json', customRules);

            const response = await fetch('/api/convert', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                let convertedText = data.converted_text || data.original_text || "";
                
                editor.setOutputText(convertedText);
                editor.setStats(data.replacements_count || 0);

                if (!convertedText) {
                    updateStatus(`Document ${data.filename} loaded, but no selectable text was found.`, true);
                } else {
                    updateStatus(`Document ${data.filename} extracted & converted successfully!`, false);
                }
            } else {
                alert("Error processing document: " + (data.detail || "Unknown error"));
            }
        } catch (err) {
            console.error("File convert error:", err);
            alert("File convert request failed: " + err.message);
        } finally {
            hidePreloader();
            updateStatus("Ready for instant conversion", false);
        }
    }

    function setupActions() {
        const btnLoadSample = document.getElementById('btn-load-sample');
        const btnExportDocx = document.getElementById('btn-export-docx');

        if (btnLoadSample) {
            btnLoadSample.addEventListener('click', () => loadSampleText());
        }

        if (btnExportDocx) {
            btnExportDocx.addEventListener('click', () => exportToDocx());
        }
    }

    async function loadSampleText() {
        updateStatus("Loading sample text...", true);
        try {
            const res = await fetch('/api/sample');
            const data = await res.json();
            if (data.success) {
                editor.setOutputText(data.converted_text || data.original_text);
                editor.setStats(data.replacements_count || 0);
            }
        } catch (e) {
            console.error("Sample load error:", e);
        } finally {
            updateStatus("Ready for instant conversion", false);
        }
    }

    async function exportToDocx() {
        const text = editor.getOutputText();
        if (!text) {
            alert("No text to export! Please convert or enter text first.");
            return;
        }

        const fontSelect = document.getElementById('font-select');
        const fontName = fontSelect ? fontSelect.value : "Amiri";

        const payload = {
            title: "Lisan al-Dawat Converted Document",
            text: text,
            font_name: fontName,
            font_size: 14
        };

        updateStatus("Generating Word document (.docx)...", true);

        try {
            const response = await fetch('/api/export-docx', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error("Failed to create Word document");
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `LSD_Converted_${Date.now()}.docx`;
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        } catch (err) {
            console.error("Docx export error:", err);
            alert("Error exporting Word document: " + err.message);
        } finally {
            updateStatus("Ready for instant conversion", false);
        }
    }

    function updateStatus(msg, isBusy) {
        const statusText = document.getElementById('status-text');
        if (statusText) statusText.textContent = msg;
    }
});
