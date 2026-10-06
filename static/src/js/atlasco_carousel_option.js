/** @odoo-module **/
/*
 * Atlasco — homepage hero carousel snippet options.
 *
 * The hero slides live on the atlasco.home.slide model rather than in a
 * per-website view override, because the 2026-07-22 COW reset wiped the
 * client's editor-built carousel and a model survives a module upgrade. The
 * cost of that choice was that add / delete / reorder disappeared from the
 * Website editor — the client could only reach them from the backend menu.
 *
 * This option gives those three actions back in the editor, writing straight
 * to the model, so the carousel is both client-editable AND upgrade-proof.
 * Replacing a slide's picture is handled by the normal image widget (the
 * template renders the field through t-field, so Odoo owns that node).
 *
 * Mirrors the structure of atlasco_video_option.js (AtlascoVideoReplace).
 */
import options from "@web_editor/js/editor/snippets.options";

const MODEL = "atlasco.home.slide";

options.registry.AtlascoHeroCarousel = options.Class.extend({
    /**
     * @override
     */
    start: function () {
        this.orm = this.bindService("orm");
        this.notification = this.bindService("notification");
        return this._super(...arguments);
    },

    // ---------------------------------------------------------------- utils

    /**
     * The slide the user currently has selected. The editor targets the
     * carousel section, so resolve the active slide from the DOM.
     */
    _activeSlide: function () {
        const target = this.$target[0];
        return (
            target.querySelector(".atl-hero-slide.is-active") ||
            target.querySelector(".atl-hero-slide")
        );
    },

    _slideId: function (el) {
        return el ? parseInt(el.dataset.slideId, 10) : NaN;
    },

    _allSlideIds: function () {
        return [...this.$target[0].querySelectorAll(".atl-hero-slide")]
            .map((el) => this._slideId(el))
            .filter((id) => !Number.isNaN(id));
    },

    /**
     * Model writes bypass the editor's own dirty-tracking, so the DOM and the
     * DB diverge until the page is re-rendered. Reload rather than trying to
     * patch the carousel in place — the JS carousel keeps index state that a
     * partial DOM edit would desync.
     */
    _reload: function () {
        this.notification.add("Slide saved. Reloading the editor…", {
            type: "success",
        });
        window.location.reload();
    },

    // -------------------------------------------------------------- actions

    /**
     * Create a blank slide after the current one and reload so it renders.
     * Sequence is placed between the current slide and the next, leaving room
     * for further inserts without a full resequence.
     */
    addSlide: async function () {
        const current = this._activeSlide();
        const ids = this._allSlideIds();
        let sequence = 10 * (ids.length + 1);
        const currentId = this._slideId(current);
        if (!Number.isNaN(currentId)) {
            const [rec] = await this.orm.read(MODEL, [currentId], ["sequence"]);
            if (rec) {
                sequence = rec.sequence + 5;
            }
        }
        await this.orm.create(MODEL, [
            {
                name: "New slide",
                sequence: sequence,
                show_overlay: false,
            },
        ]);
        this._reload();
    },

    /**
     * Remove the selected slide. Refuses on the last remaining one — the
     * homepage template falls back to the legacy static hero when no slides
     * exist, which looks like the carousel broke rather than like an
     * intentional delete.
     */
    deleteSlide: async function () {
        const ids = this._allSlideIds();
        if (ids.length <= 1) {
            this.notification.add(
                "This is the last slide. Add another before deleting this one.",
                { type: "warning" }
            );
            return;
        }
        const id = this._slideId(this._activeSlide());
        if (Number.isNaN(id)) {
            return;
        }
        await this.orm.unlink(MODEL, [id]);
        this._reload();
    },

    /**
     * Swap sequences with the neighbouring slide.
     *
     * @param {boolean|string} previewMode unused, required by the options API
     * @param {string} widgetValue "prev" or "next"
     */
    moveSlide: async function (previewMode, widgetValue) {
        const ids = this._allSlideIds();
        const id = this._slideId(this._activeSlide());
        const i = ids.indexOf(id);
        const j = widgetValue === "prev" ? i - 1 : i + 1;
        if (i === -1 || j < 0 || j >= ids.length) {
            this.notification.add("Already at the end of the carousel.", {
                type: "info",
            });
            return;
        }
        const recs = await this.orm.read(MODEL, [ids[i], ids[j]], ["sequence"]);
        const byId = Object.fromEntries(recs.map((r) => [r.id, r.sequence]));
        await this.orm.write(MODEL, [ids[i]], { sequence: byId[ids[j]] });
        await this.orm.write(MODEL, [ids[j]], { sequence: byId[ids[i]] });
        this._reload();
    },
});

export default {
    AtlascoHeroCarousel: options.registry.AtlascoHeroCarousel,
};
