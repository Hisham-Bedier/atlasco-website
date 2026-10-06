# -*- coding: utf-8 -*-
"""Atlasco partners as data, not code.

ClickUp 869eg533x follow-up ("it shouldn't be hardcoded"): the 23 original
partners used to live as inline dicts inside controllers/main.py (a
16,000+-line file), hand-authored HTML cards in views/partners.xml, and a
separate hardcoded JS array for the homepage honeycomb — three copies of
overlapping data, none of it backend-editable. `_seed_legacy_partners()`
below migrates all 23 into real records here (idempotent, only creates a
slug that doesn't already exist), and the three render sites (partner_detail
route, /partners listing, homepage honeycomb) now read this model as their
only source of truth.

Everything a partner page renders is a field here, so the client edits
partners the same way they edit team members or milestones.
"""
from odoo import api, fields, models

from .seo_slug import validate_seo_slug


class AtlascoPartner(models.Model):
    _name = "atlasco.partner"
    _description = "Atlasco Partner"
    _order = "sequence, name"

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    name = fields.Char("Partner Name", required=True)
    slug = fields.Char("URL Slug", required=True, help="Drives /partners/<slug>.")
    category = fields.Char("Category")
    country = fields.Char("Country")

    # shown on the homepage strip
    show_on_home = fields.Boolean("Show on Homepage Strip", default=True)
    home_label = fields.Char("Homepage Caption", help="Short line under the logo on the homepage.")
    # ClickUp 869f081z9 — "Add new Partner (logo + link + details page) not
    # possible from backend". Root cause for the logo half of that ticket:
    # `logo`/`banner` below are plain Char *paths* (e.g.
    # "/atlasco_website/static/src/img/partners/compair.png") pointing at a
    # static file baked into the module — there is no backend control that
    # can put a NEW file at a NEW path, so a real logo/banner for a
    # brand-new partner was never actually settable from the backend, only
    # from a code change. `logo_image`/`banner_image` are real upload
    # widgets (stored as attachments, served via /web/image/...) so a new
    # partner gets a working logo/banner purely through the form. The Char
    # fields stay as a fallback/override for the original 23 partners whose
    # real assets already live in static/ (see logo_url()/banner_url()).
    logo_image = fields.Image("Logo", help="Upload the partner's logo here. Used if set; falls back to Logo Path otherwise.")
    logo = fields.Char("Logo Path", help="Advanced: path to a static image already shipped in the module. Prefer the Logo upload above for new partners.")
    link = fields.Char("Link", help="Where the homepage logo points. Defaults to /partners/<slug>.")

    banner_image = fields.Image("Banner", help="Upload the partner page's hero banner here. Used if set; falls back to Banner Image Path otherwise.")
    banner = fields.Char("Banner Image Path", help="Advanced: path to a static image already shipped in the module. Prefer the Banner upload above for new partners.")
    tagline = fields.Char()
    headline = fields.Char()
    subtitle = fields.Char()
    together = fields.Text("Together Statement")

    body_html = fields.Html("Body", sanitize=False)

    tech_name = fields.Char("Featured Technology")
    tech_description = fields.Text("Featured Technology Description")
    tech_video = fields.Char("Featured Technology Video")

    kpi_ids = fields.One2many("atlasco.partner.kpi", "partner_id", string="KPIs")
    why_ids = fields.One2many("atlasco.partner.why", "partner_id", string="Why Atlasco")
    range_ids = fields.One2many("atlasco.partner.link", "partner_id", string="Product Range",
                                domain=[("kind", "=", "range")])
    quicklink_ids = fields.One2many("atlasco.partner.link", "partner_id", string="Quick Links",
                                    domain=[("kind", "=", "quick")])
    link_ids = fields.One2many("atlasco.partner.link", "partner_id", string="All Links")
    service_program_ids = fields.One2many("atlasco.partner.service_program", "partner_id",
                                          string="Service Programs",
                                          help="Only a couple of partners have these (e.g. CompAir's Assure/iConn) — leave empty otherwise.")
    certification_ids = fields.One2many("atlasco.partner.certification", "partner_id",
                                        string="Certifications")

    _sql_constraints = [("slug_uniq", "unique(slug)", "That partner slug is already used.")]

    @api.constrains("slug")
    def _check_slug_is_seo_convention(self):
        # New partner pages must follow the site's lowercase-hyphenated
        # slug convention — see models/seo_slug.py for the full rule.
        for rec in self:
            validate_seo_slug(rec.slug)

    def write(self, vals):
        # The hero-banner picker (Website > Page Hero Banners) keys its
        # partner rows as 'partner_<slug>' — a plain string, not a real
        # link to this record. Renaming a partner's slug here without this
        # would silently orphan its hero row (still sitting under the OLD
        # key) and leave the new slug with no hero-banner entry at all, so
        # an uploaded banner would just stop applying with no error
        # anywhere. Keep the two in sync automatically instead.
        old_slugs = {rec.id: rec.slug for rec in self} if 'slug' in vals else {}
        res = super().write(vals)
        if old_slugs and vals.get('slug'):
            Hero = self.env['atlasco.page.hero'].sudo()
            for rec in self:
                old_slug = old_slugs.get(rec.id)
                if old_slug and old_slug != rec.slug:
                    hero = Hero.search([('key', '=', 'partner_%s' % old_slug)], limit=1)
                    if hero and not Hero.search_count([('key', '=', 'partner_%s' % rec.slug)]):
                        hero.write({'key': 'partner_%s' % rec.slug, 'label': rec.name})
        return res

    def href(self):
        self.ensure_one()
        return self.link or ("/partners/%s" % (self.slug or ""))

    def logo_url(self):
        self.ensure_one()
        if self.logo_image:
            unique = int(self.write_date.timestamp()) if self.write_date else 0
            return "/web/image/atlasco.partner/%d/logo_image?unique=%s" % (self.id, unique)
        return self.logo or ""

    def banner_url(self):
        self.ensure_one()
        if self.banner_image:
            unique = int(self.write_date.timestamp()) if self.write_date else 0
            return "/web/image/atlasco.partner/%d/banner_image?unique=%s" % (self.id, unique)
        return self.banner or ""

    def to_page_data(self):
        """Build the same dict shape controllers/main.py's partner_detail()
        renders, so a partner created purely from the backend gets a real,
        working /partners/<slug> page instead of the silent "falls back to
        CompAir" bug (ClickUp 869f081z9). product_range is intentionally
        left out here — the controller already fills it in from
        atlasco.partner.product by slug for every partner.
        """
        self.ensure_one()
        return {
            "name": self.name,
            "banner": self.banner_url(),
            "slug": self.slug,
            "category": self.category or "",
            "country": self.country or "",
            "tagline": self.tagline or "",
            "headline": self.headline or "",
            "subtitle": self.subtitle or "",
            "kpis": [{"value": k.value, "label": k.label} for k in self.kpi_ids],
            # 'body' below is t-esc'd (escaped) by partner_detail.xml; kept
            # empty for ORM records since body_html is real admin-authored
            # HTML (widget="html" on the backend form) and goes through the
            # separate 'body_raw' key instead, which the template t-raw's —
            # never mix the two or the markup gets escaped into visible
            # literal tags.
            "body": [],
            "body_raw": self.body_html or "",
            "together": self.together or "",
            # None (falsy) when nothing was actually filled in — a dict with
            # just blank strings would still be truthy, so partner_detail.xml's
            # `t-if="partner.get('featured_technology')"` would render an
            # empty "Featured Technology" section title on every partner
            # that has none (only CompAir has real content here today).
            "featured_technology": ({
                "name": self.tech_name or "",
                "description": self.tech_description or "",
                "links": [],
                "video": self.tech_video or "",
            } if (self.tech_name or self.tech_description or self.tech_video) else None),
            "why_atlasco": [{"title": w.title, "description": w.description or ""} for w in self.why_ids],
            "quick_links": [{"text": l.text, "url": l.url} for l in self.quicklink_ids],
            "service_programs": [
                {
                    "name": sp.name,
                    "subtitle": sp.subtitle or "",
                    "description": sp.description or "",
                    "features": (sp.features or "").splitlines(),
                }
                for sp in self.service_program_ids
            ],
            "certifications": [
                {"name": c.name, "image": c.image_url()} for c in self.certification_ids
            ],
        }

    @api.model
    def _seed_legacy_partners(self):
        """One-time idempotent seed: create a real atlasco.partner record
        for each of the 23 partners that used to live only as a hardcoded
        dict in controllers/main.py (`_LEGACY_PARTNERS_SEED` there) —
        ClickUp 869eg533x follow-up. Only creates a slug that doesn't
        already exist, so this is safe to re-run on every module upgrade
        and never clobbers a manual edit made after the first deploy.

        show_on_home is seeded to match exactly the 15 of these 23 that
        used to appear in the old hardcoded homepage-honeycomb JS array
        (static/src/js/atlasco.js), so the homepage strip looks identical
        before and after this migration.
        """
        import html as html_lib
        # Lazy import: controllers/main.py imports models at module-load
        # time via Odoo's own machinery, so importing controllers back
        # from a model method (call-time, not module top) avoids a
        # load-order/circular-import dependency — same technique already
        # used by partner_product.py's _backfill_images_from_catalog().
        from odoo.addons.atlasco_website.controllers.main import (
            _LEGACY_PARTNERS_SEED, _LEGACY_PARTNER_LOGOS,
        )

        home_strip_slugs = {
            'compair', 'oxymat', 'spm', 'chart-industries', 'ept-clean-oil',
            'spectro-scientific', 'continental-industrie', 'filtertechnik',
            'sdt-systems', 'noria-corporation', 'luneta', 'mobius-institute',
            'harvard-corporation', 'sotras', 'des-case',
        }

        seq = 10
        for slug, d in _LEGACY_PARTNERS_SEED.items():
            if self.search_count([('slug', '=', slug)]):
                continue
            tech = d.get('featured_technology') or {}
            vals = {
                'sequence': seq,
                'name': d.get('name'),
                'slug': slug,
                'category': d.get('category'),
                'country': d.get('country'),
                'show_on_home': slug in home_strip_slugs,
                'home_label': d.get('category'),
                'logo': d.get('logo') or _LEGACY_PARTNER_LOGOS.get(slug, ''),
                'banner': d.get('banner') or '',
                'tagline': d.get('tagline'),
                'headline': d.get('headline'),
                'subtitle': d.get('subtitle'),
                'together': d.get('together'),
                'tech_name': tech.get('name'),
                'tech_description': tech.get('description'),
                'tech_video': tech.get('video'),
                'body_html': ''.join(
                    '<p>%s</p>' % html_lib.escape(p) for p in (d.get('body') or [])
                ),
                'kpi_ids': [
                    (0, 0, {'sequence': i * 10, 'value': k['value'], 'label': k['label']})
                    for i, k in enumerate(d.get('kpis') or [])
                ],
                'why_ids': [
                    (0, 0, {'sequence': i * 10, 'title': w['title'], 'description': w.get('description', '')})
                    for i, w in enumerate(d.get('why_atlasco') or [])
                ],
                'quicklink_ids': [
                    (0, 0, {'sequence': i * 10, 'kind': 'quick', 'text': q['text'], 'url': q.get('url', '')})
                    for i, q in enumerate(d.get('quick_links') or [])
                ],
                'service_program_ids': [
                    (0, 0, {
                        'sequence': i * 10,
                        'name': sp.get('name'),
                        'subtitle': sp.get('subtitle'),
                        'description': sp.get('description'),
                        'features': '\n'.join(sp.get('features') or []),
                    })
                    for i, sp in enumerate(d.get('service_programs') or [])
                ],
                'certification_ids': [
                    (0, 0, {
                        'sequence': i * 10,
                        'name': c.get('name'),
                        # 'image' in the legacy dict is a static path string,
                        # not an upload — image_path is this model's own
                        # Char-fallback field (same logo/banner convention),
                        # so nothing is silently lost.
                        'image_path': c.get('image'),
                    })
                    for i, c in enumerate(d.get('certifications') or [])
                ],
            }
            rec = self.create(vals)
            seq += 10
            # The 'logo'/'banner'/'image_path' Char fields above are enough
            # for the site to render correctly, but the backend form's
            # actual Logo/Banner upload widgets (logo_image/banner_image)
            # stay visibly empty otherwise — same "map what's on to the
            # backend" gap already fixed once this session for Partner
            # Product Range images. Backfill the real image fields from the
            # same static files so the form previews show something instead
            # of looking unlinked/broken.
            self._backfill_static_image(rec, 'logo', 'logo_image')
            self._backfill_static_image(rec, 'banner', 'banner_image')
            for cert in rec.certification_ids:
                self._backfill_static_image(cert, 'image_path', 'image')
        return True

    def _backfill_static_image(self, record, path_field, image_field):
        """Read the static file at record[path_field] (a module-relative
        URL like '/atlasco_website/static/src/img/partners/compair.png')
        and write its bytes into record[image_field] (a real fields.Image).
        No-op if the path field is empty, isn't under this module's static/
        folder, or the file can't be found/read.
        """
        import base64
        import urllib.parse
        from odoo.modules.module import get_module_resource

        path = record[path_field]
        prefix = '/atlasco_website/'
        if not path or not path.startswith(prefix):
            return
        rel = urllib.parse.unquote(path[len(prefix):])
        fs_path = get_module_resource('atlasco_website', *rel.split('/'))
        if not fs_path:
            return
        try:
            with open(fs_path, 'rb') as f:
                record[image_field] = base64.b64encode(f.read())
        except OSError:
            return


class AtlascoPartnerKpi(models.Model):
    _name = "atlasco.partner.kpi"
    _description = "Atlasco Partner KPI"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    partner_id = fields.Many2one("atlasco.partner", required=True, ondelete="cascade")
    value = fields.Char(required=True)
    label = fields.Char(required=True)


class AtlascoPartnerWhy(models.Model):
    _name = "atlasco.partner.why"
    _description = "Atlasco Partner — Why Atlasco item"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    partner_id = fields.Many2one("atlasco.partner", required=True, ondelete="cascade")
    title = fields.Char(required=True)
    description = fields.Text()


class AtlascoPartnerLink(models.Model):
    _name = "atlasco.partner.link"
    _description = "Atlasco Partner Link"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    partner_id = fields.Many2one("atlasco.partner", required=True, ondelete="cascade")
    kind = fields.Selection([("range", "Product Range"), ("quick", "Quick Link")],
                            default="range", required=True)
    text = fields.Char(required=True)
    url = fields.Char()
    external_url = fields.Char()


class AtlascoPartnerServiceProgram(models.Model):
    _name = "atlasco.partner.service_program"
    _description = "Atlasco Partner — Service Program"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    partner_id = fields.Many2one("atlasco.partner", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    subtitle = fields.Char()
    description = fields.Text()
    features = fields.Text(help="One bullet point per line.")


class AtlascoPartnerCertification(models.Model):
    _name = "atlasco.partner.certification"
    _description = "Atlasco Partner — Certification"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    partner_id = fields.Many2one("atlasco.partner", required=True, ondelete="cascade")
    name = fields.Char(required=True)
    image = fields.Image("Badge Image", help="Upload the certification badge here. Used if set; falls back to Image Path otherwise.")
    image_path = fields.Char("Image Path", help="Advanced: path to a static image already shipped in the module. Prefer the upload above for new certifications.")

    def image_url(self):
        self.ensure_one()
        if self.image:
            unique = int(self.write_date.timestamp()) if self.write_date else 0
            return "/web/image/atlasco.partner.certification/%d/image?unique=%s" % (self.id, unique)
        return self.image_path or ""
