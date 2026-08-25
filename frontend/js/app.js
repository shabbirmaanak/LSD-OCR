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
    setupMobileTabs();

    function setupMobileTabs() {
        const tabInput = document.getElementById('tab-input');
        const tabOutput = document.getElementById('tab-output');
        const tabSettings = document.getElementById('tab-settings');

        const paneInput = document.getElementById('pane-input');
        const paneOutput = document.getElementById('pane-output');
        const sectionSettings = document.getElementById('section-settings');

        if (!tabInput || !tabOutput || !tabSettings || !paneInput || !paneOutput) return;

        function setActiveTab(activeTab) {
            [tabInput, tabOutput, tabSettings].forEach(t => {
                t.classList.remove('bg-blue-600', 'text-white', 'shadow');
                t.classList.add('text-slate-300', 'hover:bg-slate-700/60');
            });

            activeTab.classList.remove('text-slate-300', 'hover:bg-slate-700/60');
            activeTab.classList.add('bg-blue-600', 'text-white', 'shadow');

            if (window.innerWidth < 1024) {
                if (activeTab === tabInput) {
                    paneInput.classList.remove('hidden');
                    paneOutput.classList.add('hidden');
                    if (sectionSettings) sectionSettings.classList.add('hidden');
                } else if (activeTab === tabOutput) {
                    paneInput.classList.add('hidden');
                    paneOutput.classList.remove('hidden');
                    if (sectionSettings) sectionSettings.classList.add('hidden');
                } else if (activeTab === tabSettings) {
                    paneInput.classList.add('hidden');
                    paneOutput.classList.add('hidden');
                    if (sectionSettings) sectionSettings.classList.remove('hidden');
                }
            }
        }

        tabInput.addEventListener('click', () => setActiveTab(tabInput));
        tabOutput.addEventListener('click', () => setActiveTab(tabOutput));
        tabSettings.addEventListener('click', () => setActiveTab(tabSettings));

        window.addEventListener('resize', () => {
            if (window.innerWidth >= 1024) {
                paneInput.classList.remove('hidden');
                paneOutput.classList.remove('hidden');
                if (sectionSettings) sectionSettings.classList.remove('hidden');
            } else {
                setActiveTab(tabInput);
            }
        });

        if (window.innerWidth < 1024) {
            setActiveTab(tabInput);
        }
    }

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
        updateStatus(`جاري رفع الخط المخصص ${file.name}...`, true);
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
                updateStatus(`تمت إضافة الخط ${data.font_name} بنجاح!`, false);
            } else {
                alert("حدث خطأ أثناء رفع الخط: " + (data.detail || "أمر غير معروف"));
            }
        } catch (err) {
            console.error("Font upload error:", err);
            alert("فشل رفع الخط / Font upload error: " + err.message);
        } finally {
            updateStatus("جاهز للتحويل المباشر السريع", false);
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
        const inputArea = document.getElementById('input-editor');
        if (inputArea) {
            inputArea.addEventListener('input', () => {
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
                        editor.setInputText(clipboardText);
                        performLiveConversion();
                        updateStatus("تم لصق النص من الحافظة بنجاح!", false);
                    } else {
                        alert("الحافظة فارغة! لا يوجد نص في الحافظة.");
                    }
                } catch (err) {
                    console.error("Clipboard paste error:", err);
                    alert("يمكنك استخدام اختصار المفاتيح (Ctrl+V أو Cmd+V) لصق النص مباشرة في مربع النص.");
                }
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
        return text.replace(/[\r\u200e\u200f\ufeff\u202a-\u202e\xa0]/g, '');
    }

    function fixReversedArabicLine(line) {
        const cleanLine = line.replace(/ـ/g, '').replace(/\u200c/g, '').replace(/\u200d/g, '');
        if (!cleanLine.trim()) return "";

        if (/^\s*Page\s+\d+\s+of\s+\d+\s*$/i.test(cleanLine)) {
            return cleanLine.trim();
        }

        const hasArabic = /[\u0600-\u06ff]/.test(cleanLine);
        if (!hasArabic) return cleanLine.trim();

        const placeholders = {};
        let engCount = 0;
        const protectedLine = cleanLine.replace(/[a-zA-Z]+/g, match => {
            const key = `__ENG${engCount++}__`;
            placeholders[key] = match;
            return key;
        });

        let rev = protectedLine.split('').reverse().join('');
        for (let key in placeholders) {
            const revKey = key.split('').reverse().join('');
            rev = rev.replace(revKey, placeholders[key]);
        }
        return rev.trim();
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
            const isLetterPiece = hasArabic && cleanT.length <= 2 && !PUNCTUATION_SET.has(tok);

            if (isLetterPiece) {
                buffer += tok;
            } else {
                if (buffer) {
                    merged.push(buffer);
                    buffer = "";
                }
                merged.push(tok);
            }
        }

        if (buffer) {
            merged.push(buffer);
        }
        return merged.join(' ');
    }

    function autoFixArabicSentenceFlow(text) {
        if (!text) return "";
        const cleanText = sanitizeText(text);
        const lines = cleanText.split('\n');

        const fixedLines = lines.map(line => {
            const rawLine = line.replace(/ـ/g, '').replace(/\u200c/g, '').replace(/\u200d/g, '');
            if (!rawLine.trim()) return "";

            const tokens = rawLine.trim().split(/\s+/);
            if (!tokens || tokens.length === 0) return "";

            const isTypeAReversed = (
                rawLine.includes('لمضم') || rawLine.includes('يـعالدلا') ||
                tokens.some(w => w.endsWith('دلا') || w.endsWith('لاا'))
            );

            if (isTypeAReversed) {
                return fixReversedArabicLine(line);
            }

            const singleLetterCount = tokens.filter(t => {
                const c = t.replace(/[^\w]/g, '');
                return c.length <= 2 && /[\u0600-\u06ff]/.test(c);
            }).length;

            if (singleLetterCount >= 2) {
                return rejoinSpacedArabicLetters(line);
            }

            return rawLine.trim();
        });
        return fixedLines.join('\n');
    }

    function performLiveConversion() {
        const rawText = editor.getInputText();
        if (!rawText) {
            editor.setOutputText("");
            editor.setStats(0);
            return;
        }

        const normalizedText = autoFixArabicSentenceFlow(rawText);
        let cleanedText = normalizedText.replace(/ـ/g, '').replace(/\u200c/g, '').replace(/\u200d/g, '').replace(/`/g, '');

        const rules = ruleManager.getRules();
        
        // Client-side instant deterministic conversion
        let converted = cleanedText;
        let count = 0;

        // Sort rules by pattern length descending
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
        updateStatus("جاري رفع واستخراج المستند...", true);
        showPreloader("جاري استخراج ومعالجة المستند...", "تطبيق قواعد لسان الدعوة وضبط تدفق السطور تلقائياً");

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
                let extractedText = data.original_text || "";
                let convertedText = data.converted_text || "";
                
                let fixedInput = autoFixArabicSentenceFlow(extractedText);
                editor.setInputText(fixedInput);
                
                if (convertedText) {
                    let fixedOutput = autoFixArabicSentenceFlow(convertedText);
                    editor.setOutputText(fixedOutput);
                    editor.setStats(data.replacements_count || 0);
                } else {
                    performLiveConversion();
                }

                if (!extractedText && !convertedText) {
                    alert("ملاحظة: هذا المستند لا يحتوي على نص قابل للتحديد (قد يكون صورة ممسوحة ضوئياً).");
                }
                
                updateStatus(`تم استخراج وتحويل المستند ${data.filename} بنجاح!`, false);
            } else {
                alert("حدث خطأ أثناء معالجة المستند: " + (data.detail || "أمر غير معروف"));
            }
        } catch (err) {
            console.error("File convert error:", err);
            alert("فشل الاتصال بالخادم / File convert request failed: " + err.message);
        } finally {
            hidePreloader();
            updateStatus("جاهز للتحويل المباشر السريع", false);
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
        updateStatus("جاري تحميل النص العينة...", true);
        try {
            const res = await fetch('/api/sample');
            const data = await res.json();
            if (data.success) {
                editor.setInputText(data.original_text);
                editor.setOutputText(data.converted_text);
                editor.setStats(data.replacements_count);
            }
        } catch (e) {
            console.error("Sample load error:", e);
        } finally {
            updateStatus("جاهز للتحويل المباشر السريع", false);
        }
    }

    async function exportToDocx() {
        const text = editor.getOutputText();
        if (!text) {
            alert("لا يوجد نص للتصدير! يرجى تحويل أو كتابة نص أولاً.");
            return;
        }

        const fontSelect = document.getElementById('font-select');
        const fontName = fontSelect ? fontSelect.value : "Amiri";

        const payload = {
            title: "مستند لسان الدعوة المحول",
            text: text,
            font_name: fontName,
            font_size: 14
        };

        updateStatus("جاري إنشاء وتنسيق مستند وورد (RTL Word .docx)...", true);

        try {
            const response = await fetch('/api/export-docx', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                throw new Error("تعذر إنشاء مستند وورد");
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
            alert("حدث خطأ أثناء تصدير مستند وورد: " + err.message);
        } finally {
            updateStatus("جاهز للتحويل المباشر السريع", false);
        }
    }

    function updateStatus(msg, isBusy) {
        const statusText = document.getElementById('status-text');
        if (statusText) statusText.textContent = msg;
    }
});
