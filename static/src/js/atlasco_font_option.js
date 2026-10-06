/** @odoo-module **/
/*
 * Atlasco — "Font" snippet option for hand-coded static blocks (Partners,
 * Industries, Products, Services, ...). These pages have no t-field/content
 * binding, so there is nowhere for Odoo's built-in text-toolbar font
 * controls to persist a change - see the "font editing on static blocks"
 * ticket. This option instead targets the block's own wrapper (any element
 * carrying class "atl-font-editable") and writes the chosen font-family /
 * font-size onto an atlasco.block.style record via orm.write(), the same
 * persistence pattern AtlascoVideoReplace uses for videos.
 *
 * The wrapper applies the choice live via two CSS custom properties
 * (--atl-dyn-font-family / --atl-dyn-font-size, see atlasco.css), so no
 * !important fights with the page's own CSS are needed - pages that only
 * inherit the sitewide font pick it up automatically, and pages with their
 * own scoped font-family/font-size rules route those specific declarations
 * through the same variables (with their original value as the fallback).
 */
import options from "@web_editor/js/editor/snippets.options";

options.registry.AtlascoFontStyle = options.Class.extend({
    /**
     * @override
     */
    start: function () {
        this.orm = this.bindService("orm");
        return this._super(...arguments);
    },

    //--------------------------------------------------------------------------
    // Options
    //--------------------------------------------------------------------------

    /**
     * @see this.selectClass for parameters
     */
    selectFontFamily: function (previewMode, widgetValue, params) {
        this._setVar("--atl-dyn-font-family", widgetValue);
        if (!previewMode) {
            this._persist({ font_family: widgetValue || false });
        }
    },

    /**
     * @see this.selectClass for parameters
     */
    selectFontSize: function (previewMode, widgetValue, params) {
        this._setVar("--atl-dyn-font-size", widgetValue);
        if (!previewMode) {
            this._persist({ font_size: widgetValue || false });
        }
    },

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    _setVar: function (name, value) {
        if (value) {
            this.$target[0].style.setProperty(name, value);
        } else {
            this.$target[0].style.removeProperty(name);
        }
    },

    _persist: function (values) {
        const target = this.$target[0];
        const model = target.dataset.styleModel;
        const resId = parseInt(target.dataset.styleId, 10);
        if (model && resId) {
            return this.orm.write(model, [resId], values);
        }
    },

    /**
     * @override
     */
    _computeWidgetState: function (methodName, params) {
        if (methodName === "selectFontFamily") {
            return this.$target[0].style.getPropertyValue("--atl-dyn-font-family").trim();
        }
        if (methodName === "selectFontSize") {
            return this.$target[0].style.getPropertyValue("--atl-dyn-font-size").trim();
        }
        return this._super(...arguments);
    },
});

export default {
    AtlascoFontStyle: options.registry.AtlascoFontStyle,
};
