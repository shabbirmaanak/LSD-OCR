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
            "善": "هو",
            "善": "هو",
            "周": "الله",
            ";;": "گ",
            "ss": "ے",
            "ee": "پ",
            "pp": "چ",
            "qq": "ٹ",
            "ww": "ں",
            "T": "ے",
            "t": "ے"
        };

        this.init();
    }

    init() {
        if (this.presetSelect) {
            this.presetSelect.addEventListener('change', (e) => {
                this.loadPreset(e.target.value);
            });
        }

        const btnAdd = document.getElementById('btn-add-rule');
        if (btnAdd) {
            btnAdd.addEventListener('click', () => this.addRulePair('', ''));
        }

        const btnToggle = document.getElementById('btn-toggle-rules');
        const panel = document.getElementById('rules-editor-panel');
        if (btnToggle && panel) {
            btnToggle.addEventListener('click', () => {
                panel.classList.toggle('hidden');
            });
        }

        this.renderRules();
    }

    loadPreset(presetKey) {
        if (presetKey === 'alkanz_normal') {
            this.rules = {
                "كك": "گ", "سس": "ے", "ثث": "پ", "حح": "چ", "طط": "ٹ", "نن": "ں",
                "صص": "ژ", "ضض": "ڈ", "ظظ": "ڑ", "善": "هو", ";;": "گ", "ss": "ے", "ee": "پ",
                "pp": "چ", "qq": "ٹ", "ww": "ں"
            };
        } else if (presetKey === 'alkanz_urdu') {
            this.rules = {
                "ثث": "پ", "حح": "چ", "كك": "گ", "طط": "ٹ", "نن": "ں", "سس": "ے", "善": "هو"
            };
        } else if (presetKey === 'kanzmarjan') {
            this.rules = {
                "كك": "گ", "سس": "ے", "ثث": "پ", "حح": "چ", "طط": "ٹ", "نن": "ں",
                ";;": "گ", "ss": "ے", "ee": "پ", "pp": "چ", "qq": "ٹ", "ww": "ں", "善": "هو"
            };
        } else if (presetKey === 'amiri_urdu') {
            this.rules = {
                "گ": "گ", "پ": "پ", "چ": "چ", "ٹ": "ٹ", "ے": "ے", "ں": "ں", "善": "هو"
            };
        }
        this.renderRules();
        if (window.onRuleChanged) window.onRuleChanged();
    }

    renderRules() {
        if (!this.grid) return;
        this.grid.innerHTML = '';

        Object.keys(this.rules).forEach(src => {
            const tgt = this.rules[src];
            this.createRuleElement(src, tgt);
        });
    }

    createRuleElement(src, tgt) {
        const item = document.createElement('div');
        item.className = 'flex items-center gap-1 bg-white p-1.5 rounded-lg border border-[#e4ded5] shadow-sm';

        item.innerHTML = `
            <input type="text" value="${src}" class="rule-src w-full text-center bg-[#f7f4ee] border border-stone-200 rounded py-1 px-1 font-mono text-xs focus:outline-none focus:border-[#0f4c81]" placeholder="Code">
            <span class="text-stone-400 font-bold text-xs">➔</span>
            <input type="text" value="${tgt}" class="rule-tgt w-full text-center bg-[#f7f4ee] border border-stone-200 rounded py-1 px-1 font-mono text-xs focus:outline-none focus:border-[#0f4c81]" placeholder="Target">
            <button class="btn-del-rule text-stone-400 hover:text-rose-600 px-1 transition" title="Delete Rule">
                <i class="fa-solid fa-xmark"></i>
            </button>
        `;

        const inputSrc = item.querySelector('.rule-src');
        const inputTgt = item.querySelector('.rule-tgt');
        const btnDel = item.querySelector('.btn-del-rule');

        let oldSrc = src;

        const updateRule = () => {
            const newSrc = inputSrc.value.trim();
            const newTgt = inputTgt.value;

            if (oldSrc !== newSrc) {
                delete this.rules[oldSrc];
                oldSrc = newSrc;
            }

            if (newSrc) {
                this.rules[newSrc] = newTgt;
            }

            if (window.onRuleChanged) window.onRuleChanged();
        };

        inputSrc.addEventListener('change', updateRule);
        inputTgt.addEventListener('change', updateRule);

        btnDel.addEventListener('click', () => {
            delete this.rules[oldSrc];
            item.remove();
            if (window.onRuleChanged) window.onRuleChanged();
        });

        this.grid.appendChild(item);
    }

    addRulePair(src, tgt) {
        this.rules[src] = tgt;
        this.createRuleElement(src, tgt);
        if (window.onRuleChanged) window.onRuleChanged();
    }

    getRules() {
        return this.rules;
    }
}

window.RuleManager = RuleManager;
