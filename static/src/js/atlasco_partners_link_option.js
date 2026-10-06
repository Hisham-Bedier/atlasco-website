/** @odoo-module **/
/*
 * Atlasco — "Show all partners" link snippet option (ClickUp 869eg533x).
 *
 * Root cause of "Partners section: link edit doesn't save/work": the
 * honeycomb in the home page Partners section (#atlPartnerComb) is EMPTY in
 * the server-rendered HTML - every hex <a> tag, including the "Show all
 * partners" CTA, is built at runtime by initPartnerComb()/buildComb() in
 * atlasco.js. So double-clicking that CTA in the Website Editor and using
 * the generic Link dialog only edits a transient DOM node: even if the
 * click-through COW save appears to succeed, the very next page load calls
 * comb.innerHTML = '' and rebuilds every hex from content.home_partners_
 * showall_url (falling back to '/partners'), silently discarding the
 * inline edit. The field itself (content.home_partners_showall_url,
 * atlasco_content_views.xml "Partners (editorial)" group) is real and does
 * correctly drive the rendered href - there was just no editor-facing
 * control wired to it, unlike the fields the AtlascoVideoReplace/
 * AtlascoFontStyle options already cover for the video and font blocks.
 *
 * Same persistence pattern as those two: reads data-link-model/id/field off
 * the selected element (see #atlPartnerComb in homepage.xml) and writes the
 * new URL straight to that field via orm.write(), then updates the live DOM
 * (data-showall-url attribute + the already-rendered CTA hex's href, if
 * present) so the change is visible immediately without a reload.
 */
import options from "@web_editor/js/editor/snippets.options";

options.registry.AtlascoPartnersLink = options.Class.extend({
    /**
     * @override
     */
    start: function () {
        this.orm = this.bindService("orm");
        return this._super(...arguments);
    },

    /**
     * @see this.selectClass for parameters
     */
    setPartnersShowAllUrl: function (previewMode, widgetValue, params) {
        if (previewMode) {
            return;
        }
        const target = this.$target[0];
        const url = (widgetValue || "").trim() || "/partners";

        // Reflect immediately: the attribute atlasco.js reads on load, and
        // the already-rendered CTA hex (if the comb has finished building).
        target.setAttribute("data-showall-url", url);
        const ctaLink = target.querySelector("a.atl-pe-hex-cta");
        if (ctaLink) {
            ctaLink.setAttribute("href", url);
        }

        const model = target.dataset.linkModel;
        const resId = parseInt(target.dataset.linkId, 10);
        const field = target.dataset.linkField;
        if (model && resId && field) {
            return this.orm.write(model, [resId], { [field]: url });
        }
    },

    /**
     * @override
     */
    _computeWidgetState: function (methodName, params) {
        if (methodName === "setPartnersShowAllUrl") {
            return this.$target[0].getAttribute("data-showall-url") || "";
        }
        return this._super(...arguments);
    },
});

export default {
    AtlascoPartnersLink: options.registry.AtlascoPartnersLink,
};
