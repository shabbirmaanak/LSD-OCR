/**
 * Editor Module for Non-AI Alkanz Converter
 */

class TextEditor {
    constructor(inputId, outputId, fontSelectId, statsId) {
        this.input = document.getElementById(inputId);
        this.output = document.getElementById(outputId);
        this.fontSelect = document.getElementById(fontSelectId);
        this.stats = document.getElementById(statsId);

        this.init();
    }

    init() {
        if (this.input) {
            this.input.setAttribute('dir', 'rtl');
            this.input.style.direction = 'rtl';
            this.input.style.textAlign = 'right';
        }
        if (this.output) {
            this.output.setAttribute('dir', 'rtl');
            this.output.style.direction = 'rtl';
            this.output.style.textAlign = 'right';
        }

        if (this.fontSelect && this.output) {
            this.fontSelect.addEventListener('change', (e) => {
                const font = e.target.value;
                this.setFont(font);
            });
        }

        const btnCopy = document.getElementById('btn-copy-text');
        if (btnCopy) {
            btnCopy.addEventListener('click', () => this.copyToClipboard());
        }

        const btnClear = document.getElementById('btn-clear-input');
        if (btnClear) {
            btnClear.addEventListener('click', () => {
                if (this.input) this.input.value = '';
                if (this.output) this.output.value = '';
                this.setStats(0);
            });
        }
    }

    setFont(fontName) {
        if (!this.output) return;
        if (fontName === 'Scheherazade New') {
            this.output.style.fontFamily = "'Scheherazade New', serif";
        } else if (fontName === 'Arial') {
            this.output.style.fontFamily = "Arial, sans-serif";
        } else {
            this.output.style.fontFamily = `'${fontName}', 'Amiri', serif`;
        }
    }

    getInputText() {
        if (this.output && this.output.value) return this.output.value;
        return this.input ? this.input.value : "";
    }

    setInputText(val) {
        if (this.input) this.input.value = val;
        if (this.output) this.output.value = val;
    }

    setOutputText(val) {
        if (this.output) this.output.value = val;
    }

    getOutputText() {
        return this.output ? this.output.value : "";
    }

    setStats(replacementsCount) {
        if (this.stats) {
            this.stats.innerHTML = `<span>${replacementsCount} Replacements Made</span>`;
        }
    }

    copyToClipboard() {
        if (!this.output || !this.output.value) return;
        navigator.clipboard.writeText(this.output.value)
            .then(() => {
                const btn = document.getElementById('btn-copy-text');
                const orig = btn.innerHTML;
                btn.innerHTML = `<i class="fa-solid fa-check text-emerald-400"></i> <span>Copied!</span>`;
                setTimeout(() => { btn.innerHTML = orig; }, 2000);
            })
            .catch(err => console.error("Clipboard copy error:", err));
    }
}

window.TextEditor = TextEditor;
