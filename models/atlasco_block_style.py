import re

from odoo import api, fields, models

# label/page for every block currently wired to atl-font-editable, keyed by
# the same string each page's template passes to _get(key). Seeded (not
# created eagerly) so the backend "Block Styles" list is populated with every
# known block up front, without ever overwriting a value someone already set.
_BLOCK_ROWS = [
    ('about_intro', 'About — Intro', 'About'),
    ('industries_hero', 'Industries — Hero', 'Industries'),
    ('products_hero', 'Products — Hero', 'Products'),
    ('services_hero', 'Services — Hero', 'Services'),
    ('careers_hero', 'Careers & Culture — Hero', 'Careers & Culture'),
    ('contact_hero', 'Contact — Hero', 'Contact'),
    ('partners_hero_banner', 'Partners — Hero Banner', 'Partners'),
    ('partners_breadcrumb', 'Partners — Breadcrumb', 'Partners'),
    ('partners_hero', 'Partners — Hero', 'Partners'),
    ('partners_heading', 'Partners — Heading', 'Partners'),
    ('partners_grid', 'Partners — Grid', 'Partners'),
]

# Default cta_url per key, matching each hero's existing hardcoded href
# exactly, so seeding a row never changes the live site until an admin
# actually edits it. Keys with no CTA in their hero (About, Industries,
# Partners' 5 blocks) are simply absent here and get no default.
_BLOCK_CTA_DEFAULTS = {
    'products_hero': '#atl-products-l1-categories',
    'services_hero': '/contact',
    'careers_hero': '#openings',
}


class AtlascoBlockStyle(models.Model):
    """Generic, reusable typography (+ optional CTA link) override for a
    hand-coded static block.

    The site's static pages (Partners, Industries, Products, Services, ...)
    are plain hand-coded HTML with no per-field content binding, so there is
    nowhere for the Website Editor's font controls to persist a change - see
    the "font editing on static blocks" ticket. Rather than adding a pair of
    dedicated Char fields on atlasco.content for every block that might need
    this (which would mean a Python change for every new block), each block
    that opts in just calls _get(key) with its own stable string key and gets
    one record it can read/write font_family/font_size (and, where the block
    has one, its CTA button's cta_url) on.

    Wired up in the QWeb templates as:
        <t t-set="style_x" t-value="request.env['atlasco.block.style'].sudo()._get('x')"/>
        <div class="atl-font-editable o_editable" ...>

    and picked up in the editor by the AtlascoFontStyle snippet option
    (static/src/js/atlasco_font_option.js), which writes back via orm.write()
    exactly like AtlascoVideoReplace does for videos. cta_url has no
    dedicated JS option - it's edited directly from the backend "Block
    Styles" list (views/atlasco_block_style_views.xml) and read by the
    template via `t-att-href="style_x.cta_url or '<original hardcoded href>'"`.
    """
    _name = 'atlasco.block.style'
    _description = 'Atlasco Static Block Typography Override'
    _order = 'page, label'

    key = fields.Char(required=True, index=True, readonly=True)
    label = fields.Char(help="Shown in the backend list; not rendered on the site.")
    page = fields.Char(help="Which site page this block lives on, for grouping in the list.")
    font_family = fields.Char()
    font_size = fields.Char()
    cta_url = fields.Char(help="Leave empty to keep the block's built-in default link.")

    _sql_constraints = [
        ('key_uniq', 'unique(key)', 'A block style with this key already exists.'),
    ]

    @staticmethod
    def _normalize_font_size(value):
        """Append 'px' to a bare number so the value is valid CSS.

        The backend "Block Styles" list lets someone type e.g. "40" straight
        into the Font Size column - but CSS requires a unit, and
        `font-size: var(--atl-dyn-font-size, 38px)` does NOT fall back to
        the 38px default when the variable holds an unitless "40": per the
        CSS custom-properties spec, the fallback only applies when the
        variable is unset, not when it's set to something invalid for the
        property using it. An invalid value there is silently dropped
        (inherited value wins instead) - no error, just a change that
        appears to do nothing. Any value that's already a plain number
        (from here or the JS font-size dropdown, which always sends full
        values like "18px" already, so is unaffected) gets 'px' appended;
        anything else (e.g. "1.5em", "120%") is left exactly as typed.
        """
        if value and re.fullmatch(r'-?\d+(\.\d+)?', value.strip()):
            return value.strip() + 'px'
        return value

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'font_size' in vals:
                vals['font_size'] = self._normalize_font_size(vals['font_size'])
        return super().create(vals_list)

    def write(self, vals):
        if 'font_size' in vals:
            vals = dict(vals, font_size=self._normalize_font_size(vals['font_size']))
        return super().write(vals)

    @api.model
    def _get(self, key):
        record = self.sudo().search([('key', '=', key)], limit=1)
        if not record:
            record = self.sudo().create({'key': key})
        return record

    @api.model
    def _seed_blocks(self):
        """Idempotently create/backfill one row per known block.

        Creates any missing row (key, label, page, and - only on create - its
        default cta_url). For a row that already exists (e.g. one of the 5
        partners_* keys created organically by _get() before this seed ever
        ran), only label/page are backfilled - font_family/font_size/cta_url
        are left completely untouched so nothing already customized (via the
        editor or a previous backend edit) is ever overwritten by an upgrade.
        """
        existing = {r.key: r for r in self.search([])}
        changed = False
        for key, label, page in _BLOCK_ROWS:
            record = existing.get(key)
            if not record:
                self.create({
                    'key': key,
                    'label': label,
                    'page': page,
                    'cta_url': _BLOCK_CTA_DEFAULTS.get(key, False),
                })
                changed = True
            elif not record.label or not record.page:
                record.write({'label': label, 'page': page})
                changed = True
        return changed
