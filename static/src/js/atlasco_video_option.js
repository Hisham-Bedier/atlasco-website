/** @odoo-module **/
/*
 * Atlasco — "Replace video" snippet option.
 * Lets a Website-editor user click a background/tile video block and upload
 * a new self-hosted mp4. The chosen file is written back to the bound
 * content field (e.g. about_video_src / careers_hero_video / vsrc) so it
 * persists, keeping the muted autoplay loop design intact.
 *
 * This posts a plain multipart file upload to a dedicated controller
 * (/atlasco_website/video/upload) instead of using Odoo's Media Dialog.
 * The Media Dialog's own upload (/web_editor/attachment/add_data) is
 * JSON-RPC: the browser must base64-encode the ENTIRE file into one JSON
 * body first, which is fine for images but means holding a ~33% larger
 * string in memory and one giant JSON POST for a many-hundred-MB video -
 * exactly the kind of upload that hangs or fails outright, which is what
 * happened trying to replace a culture-page video. A real <input type=file>
 * + FormData upload streams the file instead of buffering it as JSON text.
 */
import options from "@web_editor/js/editor/snippets.options";

options.registry.AtlascoVideoReplace = options.Class.extend({
    /**
     * Snippet-option method — triggered by the "Replace video" we-button
     * (data-replace-video). Opens a native file picker, uploads the chosen
     * video, then applies + persists the resulting URL.
     */
    replaceVideo: function () {
        const target = this.$target[0];
        const videoEl = target.querySelector("video");
        if (!videoEl) {
            return;
        }
        const model = target.dataset.videoModel;
        const resId = target.dataset.videoId;
        const field = target.dataset.videoField;

        const input = document.createElement("input");
        input.type = "file";
        input.accept = "video/*";
        return new Promise((resolve) => {
            input.addEventListener("change", async () => {
                const file = input.files && input.files[0];
                if (!file) {
                    resolve();
                    return;
                }
                const formData = new FormData();
                formData.append("file", file);
                formData.append("model", model);
                formData.append("res_id", resId);
                formData.append("field", field);
                formData.append("csrf_token", odoo.csrf_token);

                let result;
                try {
                    const response = await fetch("/atlasco_website/video/upload", {
                        method: "POST",
                        body: formData,
                    });
                    result = await response.json();
                } catch (e) {
                    result = { error: "Upload failed. Please try again." };
                }

                if (result && result.url) {
                    videoEl.setAttribute("src", result.url);
                    const source = videoEl.querySelector("source");
                    if (source) {
                        source.setAttribute("src", result.url);
                    }
                    if (videoEl.load) {
                        videoEl.load();
                    }
                } else {
                    this.call("notification", "add", (result && result.error) || "Upload failed. Please try again.", {
                        type: "danger",
                    });
                }
                resolve();
            });
            input.click();
        });
    },
});

export default {
    AtlascoVideoReplace: options.registry.AtlascoVideoReplace,
};
