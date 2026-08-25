/**
 * Document Viewer Module
 * Handles zoom, pan, rotation, and document page preview rendering.
 */

class DocViewer {
    constructor(viewportId, imgId, placeholderId) {
        self = this;
        this.viewport = document.getElementById(viewportId);
        this.img = document.getElementById(imgId);
        this.placeholder = document.getElementById(placeholderId);
        this.zoom = 100;
        this.rotation = 0;
        this.pages = [];
        this.currentPageIdx = 0;

        this.initControls();
    }

    initControls() {
        const btnIn = document.getElementById('btn-zoom-in');
        const btnOut = document.getElementById('btn-zoom-out');
        const btnReset = document.getElementById('btn-zoom-reset');
        const btnRotate = document.getElementById('btn-filter-rotate');

        if (btnIn) btnIn.addEventListener('click', () => this.setZoom(this.zoom + 15));
        if (btnOut) btnOut.addEventListener('click', () => this.setZoom(this.zoom - 15));
        if (btnReset) btnReset.addEventListener('click', () => this.resetView());
        if (btnRotate) btnRotate.addEventListener('click', () => this.rotateImage(90));
    }

    loadPage(pageData) {
        if (!pageData || !pageData.image_base64) return;
        
        this.placeholder.classList.add('hidden');
        this.img.classList.remove('hidden');
        this.img.src = pageData.image_base64;
        this.resetView();
    }

    setZoom(level) {
        this.zoom = Math.max(40, Math.min(300, level));
        const zoomLabel = document.getElementById('zoom-level');
        if (zoomLabel) zoomLabel.textContent = `${this.zoom}%`;
        this.applyTransform();
    }

    rotateImage(deg) {
        this.rotation = (this.rotation + deg) % 360;
        this.applyTransform();
    }

    resetView() {
        this.zoom = 100;
        this.rotation = 0;
        const zoomLabel = document.getElementById('zoom-level');
        if (zoomLabel) zoomLabel.textContent = '100%';
        this.applyTransform();
    }

    applyTransform() {
        const scale = this.zoom / 100;
        this.img.style.transform = `scale(${scale}) rotate(${this.rotation}deg)`;
    }
}

window.DocViewer = DocViewer;
