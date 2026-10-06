import base64
import os

from odoo import api, fields, models
from odoo.modules.module import get_module_resource

from .seo_slug import validate_seo_slug

# Slugs/labels mirrored exactly from models/page_hero.py's _INDUSTRIES (which
# in turn mirrors controllers/main.py's INDUSTRY_HERO_COPY) — keep in sync
# if an industry slug is ever renamed.
_INDUSTRIES = [
    ('oil-gas', 'Oil & Gas'),
    ('steel', 'Steel'),
    ('pharmaceutical', 'Pharmaceutical'),
    ('medical', 'Medical'),
    ('food-beverage', 'Food & Beverage'),
    ('textile', 'Textile'),
    ('electronics', 'Electronics'),
    ('construction', 'Construction'),
    ('cement', 'Cement'),
]


class AtlascoIndustryProduct(models.Model):
    """Product card shown in the "Technologies Behind Reliable Industry"
    section of an industry detail page.

    One explicit row per (industry, product) — every industry gets its own
    editable copy of each card, so replacing an image for one industry never
    affects another. Migrated out of the hardcoded INDUSTRY_PRODUCTS /
    INDUSTRY_PRODUCTS_OG_EXTRA lists in controllers/main.py; group by
    Industry to navigate the full list, same as Page Hero Banners.
    """
    _name = "atlasco.industry.product"
    _description = "Atlasco Industry Product Card"
    _order = "industry_slug, sequence, id"

    industry_slug = fields.Selection(_INDUSTRIES, "Industry", required=True, index=True)
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    slug = fields.Char(
        "URL Slug", required=True,
        help="Used in this card's own detail page address: "
             "/industries/<industry>/<slug>. Renaming it only moves that "
             "page — the card still shows this record's own name/desc/image "
             "there. To send the card somewhere else entirely (another "
             "existing page, or an external URL), use Link Override below.")
    name = fields.Char("Name", required=True, translate=True)
    desc = fields.Text("Description", translate=True)
    image = fields.Image("Image", max_width=1920, max_height=1920)
    link_url = fields.Char(
        "Link Override",
        help="Optional. If set, clicking this card goes here instead of "
             "its own /industries/<industry>/<slug> detail page — e.g. "
             "another product's page, or an external URL. Leave blank to "
             "keep the default behavior.")
    cta_label = fields.Char(
        "Link Label", translate=True, default="Learn More",
        help="Text shown on the card's call-to-action link (revealed on "
             "hover). Previously baked into CSS as unreachable content, "
             "so it could never be edited from the Website editor or the "
             "backend — this field makes it a real, editable value.")

    _sql_constraints = [
        ('industry_slug_slug_uniq', 'unique(industry_slug, slug)',
         'A product with this URL slug already exists for this industry.'),
    ]

    @api.constrains("slug")
    def _check_slug_is_seo_convention(self):
        # New product-detail pages must follow the site's lowercase-hyphenated
        # slug convention — see models/seo_slug.py for the full rule.
        for rec in self:
            validate_seo_slug(rec.slug)

    @api.model
    def _drop_legacy_slug_constraint(self):
        """Drop the original global UNIQUE(slug) constraint from this
        model's first revision (back when a row could be shared across
        every industry via a blank industry_slug).

        _sql_constraints was later changed to unique(industry_slug, slug)
        under a new constraint name, but Odoo does not drop a superseded
        constraint on upgrade — it only adds the new one alongside it. Any
        environment that ever installed that first revision still has the
        old global constraint sitting in the database, which then collides
        with this model's per-industry seeding (the same product slug is
        legitimately reused across multiple industries). Idempotent and
        safe to run on every upgrade, including one that never had the old
        constraint at all.
        """
        self.env.cr.execute(
            "ALTER TABLE atlasco_industry_product "
            "DROP CONSTRAINT IF EXISTS atlasco_industry_product_slug_uniq"
        )

    @api.model
    def _seed_from_controller(self):
        """Idempotently seed one row per (industry, product) from the
        hardcoded controller lists, with their current static images.

        Only creates a row for an (industry, slug) pair that doesn't exist
        yet, so manual edits (or a partially-seeded table) are never
        clobbered on a later module upgrade. Also migrates away any row
        from the earlier "blank industry = shown on every industry" design,
        now superseded by an explicit row per industry.
        """
        self._drop_legacy_slug_constraint()
        try:
            from odoo.addons.atlasco_website.controllers.main import (
                INDUSTRY_PRODUCTS, INDUSTRY_PRODUCTS_OG_EXTRA,
            )
        except Exception:
            return False

        def _load_image(rel_path):
            # rel_path looks like '/atlasco_website/static/src/img/.../x.png'
            parts = (rel_path or '').strip('/').split('/', 1)
            if len(parts) != 2:
                return False
            module, path = parts
            full = get_module_resource(module, *path.split('/'))
            if not full or not os.path.isfile(full):
                return False
            with open(full, 'rb') as f:
                return base64.b64encode(f.read())

        legacy = self.search([('industry_slug', '=', False)])
        legacy.unlink()

        existing = set(self.search([]).mapped(lambda r: (r.industry_slug, r.slug)))
        created = False
        for industry_slug, _label in _INDUSTRIES:
            seq = 10
            for p in (INDUSTRY_PRODUCTS or []):
                # gas-generation is only ever shown on the oil-gas page
                # (mirrors the old _NON_OG_BASELINE filter).
                if p['slug'] == 'gas-generation' and industry_slug != 'oil-gas':
                    continue
                if (industry_slug, p['slug']) not in existing:
                    self.create({
                        'industry_slug': industry_slug,
                        'sequence': seq,
                        'slug': p['slug'],
                        'name': p['name'],
                        'desc': p.get('desc'),
                        'image': _load_image(p.get('image')),
                    })
                    created = True
                seq += 10
            if industry_slug == 'oil-gas':
                for p in (INDUSTRY_PRODUCTS_OG_EXTRA or []):
                    if (industry_slug, p['slug']) not in existing:
                        self.create({
                            'industry_slug': industry_slug,
                            'sequence': seq,
                            'slug': p['slug'],
                            'name': p['name'],
                            'desc': p.get('desc'),
                            'image': _load_image(p.get('image')),
                        })
                        created = True
                    seq += 10
        return created

    @api.model
    def _backfill_cta_label(self):
        """Set cta_label='Learn More' on any pre-existing row created before
        this field existed (field defaults only apply on create, not to
        rows already in the database). Idempotent — only touches rows
        where the label is still empty, so a manual edit is never
        clobbered on a later module upgrade.
        """
        self.search([('cta_label', '=', False)]).write({'cta_label': 'Learn More'})
