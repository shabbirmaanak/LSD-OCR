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
                "صص": "ژ", "ضض": "ڈ", "ظظ": "ڑ", ";;": "گ", "ss": "ے", "ee": "پ",
                "pp": "چ", "qq": "ٹ", "ww": "ں"
            };
        } else if (presetKey === 'alkanz_urdu') {
            this.rules = {
                "ثث": "پ", "حح": "چ", "كك": "گ", "طط": "ٹ", "نن": "ں", "سس": "ے"
            };
        } else if (presetKey === 'kanzmarjan') {
            this.rules = {
                "كك": "گ", "سس": "ے", "ثث": "پ", "حح": "چ", "طط": "ٹ", "نن": "ں",
                ";;": "گ", "ss": "ے", "ee": "پ", "pp": "چ", "qq": "ٹ", "ww": "ں"
            };
        } else if (presetKey === 'amiri_urdu') {
            this.rules = {
                "گ": "گ", "پ": "پ", "چ": "چ", "ٹ": "ٹ", "ے": "ے", "ں": "ں"
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
            this.renderRuleItem(src, tgt);
        });
    }

    renderRuleItem(src, tgt) {
        const item = document.createElement('div');
        item.className = 'bg-slate-900 border border-slate-700/80 rounded-lg p-1.5 flex items-center justify-between gap-1';
        item.innerHTML = `
            <input type="text" value="${src}" class="rule-src w-12 bg-slate-950 border border-slate-700 rounded text-center text-amber-300 font-mono focus:outline-none">
            <span class="text-slate-500">➔</span>
            <input type="text" value="${tgt}" class="rule-tgt w-12 bg-slate-950 border border-slate-700 rounded text-center text-emerald-300 font-mono focus:outline-none">
            <button class="rule-del text-slate-500 hover:text-rose-400 text-xs px-1">×</button>
        `;

        const srcInput = item.querySelector('.rule-src');
        const tgtInput = item.querySelector('.rule-tgt');
        const delBtn = item.querySelector('.rule-del');

        const updateHandler = () => {
            this.syncRulesFromDOM();
            if (window.onRuleChanged) window.onRuleChanged();
        };

        srcInput.addEventListener('input', updateHandler);
        tgtInput.addEventListener('input', updateHandler);
        delBtn.addEventListener('click', () => {
            item.remove();
            this.syncRulesFromDOM();
            if (window.onRuleChanged) window.onRuleChanged();
        });

        this.grid.appendChild(item);
    }

    addRulePair(src, tgt) {
        this.renderRuleItem(src, tgt);
        this.syncRulesFromDOM();
    }

    syncRulesFromDOM() {
        const newRules = {};
        if (!this.grid) return;
        const items = this.grid.children;
        for (let item of items) {
            const src = item.querySelector('.rule-src').value.trim();
            const tgt = item.querySelector('.rule-tgt').value.trim();
            if (src) {
                newRules[src] = tgt;
            }
        }
        this.rules = newRules;
    }

    getRules() {
        return this.rules;
    }
}

window.RuleManager = RuleManager;
