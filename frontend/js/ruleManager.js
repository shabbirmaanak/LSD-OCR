/**
 * Rule Manager Module for Alkanz / Unicode Character Replacements
 */

class RuleManager {
    constructor(gridId, presetSelectId) {
        this.grid = document.getElementById(gridId);
        this.presetSelect = document.getElementById(presetSelectId);
        this.rules = {
            "كك": "گ",
            "سس": "ے",
            "ثث": "پ",
            "حح": "چ",
            "جج": "چ",
            "طط": "ٹ",
            "نن": "ں",
            "صص": "ژ",
            "ضض": "ڈ",
            "ظظ": "ڑ",
            "؛": "چهے",
            ";;": "گ",
            "ss": "ے",
            "ee": "پ",
            "pp": "چ",
            "qq": "ٹ",
            "ww": "ں"
        };

        this.init();
    }

    init() {
        if (this.presetSelect) {
            this.presetSelect.addEventListener('change', (e) => {
                this.loadPreset(e.target.value);
            });
        }
        this.render();
    }

    loadPreset(presetName) {
        if (presetName === 'alkanz_normal') {
            this.rules = {
                "كك": "گ", "سس": "ے", "ثث": "پ", "حح": "چ", "جج": "چ",
                "طط": "ٹ", "نن": "ں", "صص": "ژ", "ضض": "ڈ", "ظظ": "ڑ",
                "؛": "چهے", ";;": "گ", "ss": "ے", "ee": "پ", "pp": "چ", "qq": "ٹ", "ww": "ں"
            };
        } else if (presetName === 'alkanz_urdu') {
            this.rules = {
                "ثث": "پ", "حح": "چ", "كك": "گ", "طط": "ٹ", "نن": "ں",
                "صص": "ژ", "ضض": "ڈ", "ظظ": "ڑ", "سس": "ے"
            };
        } else if (presetName === 'kanzmarjan') {
            this.rules = {
                "كك": "گ", "سس": "ے", "ثث": "پ", "حح": "چ", "طط": "ٹ", "نن": "ں",
                ";;": "گ", "ss": "ے", "ee": "پ", "pp": "چ", "qq": "ٹ", "ww": "ں"
            };
        } else if (presetName === 'amiri_urdu') {
            this.rules = {
                "گ": "گ", "پ": "پ", "چ": "چ", "ٹ": "ٹ", "ے": "ے", "ں": "ں"
            };
        }
        this.render();
        if (window.onRuleChanged) window.onRuleChanged();
    }

    render() {
        if (!this.grid) return;
        this.grid.innerHTML = '';

        Object.keys(this.rules).forEach(key => {
            const row = document.createElement('div');
            row.className = 'flex items-center justify-between bg-stone-50 border border-stone-200 p-2 rounded-lg text-xs';
            row.innerHTML = `
                <div class="flex items-center gap-1.5">
                    <span class="font-mono bg-stone-200 text-stone-800 px-1.5 py-0.5 rounded">${key}</span>
                    <span class="text-stone-400">➔</span>
                    <span class="font-bold text-amber-900">${this.rules[key]}</span>
                </div>
                <button data-key="${key}" class="btn-remove-rule text-rose-500 hover:text-rose-700 transition">
                    <i class="fa-solid fa-xmark text-xs"></i>
                </button>
            `;
            this.grid.appendChild(row);
        });

        this.grid.querySelectorAll('.btn-remove-rule').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const k = e.currentTarget.getAttribute('data-key');
                delete this.rules[k];
                this.render();
                if (window.onRuleChanged) window.onRuleChanged();
            });
        });
    }

    getRules() {
        return this.rules;
    }
}
