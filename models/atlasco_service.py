# -*- coding: utf-8 -*-
"""Atlasco services as data, not code.

ClickUp 869f082c8: "Services pages: cannot add more service items (e.g.
Condition Monitoring)." Until now the 7 services (Condition Monitoring,
After-Sales Support, Oil Analysis & Filtration, Piping & Installation,
Consultation Services, Rental Services, Training/PrimeGear) lived as an
inline dict inside controllers/main.py's service_detail() action, and the
/services listing page was 7 hand-written HTML rows in views/services.xml —
so there was no backend list to add an 8th service to, and no way to give a
new service a hero image without direct server/filesystem access.

Everything a service card + detail page renders is now a field here, edited
the same way partners/reliability-cards are: Website > Content > Services.
"""
from odoo import api, fields, models

from ._seed_utils import backfill_images_from_static
from .seo_slug import validate_seo_slug

# xmlid -> module-relative static path, for the one-time backfill of the new
# binary hero_image field from the bundled hero.jpg each service used to
# reference by a hardcoded /atlasco_website/static/... path in code.
_SERVICE_HERO_IMAGES = {
    'service_condition_monitoring': 'static/src/img/services/condition-monitoring/hero.jpg',
    'service_after_sales_support': 'static/src/img/services/after-sales-support/hero.jpg',
    'service_oil_analysis_filtration': 'static/src/img/services/oil-analysis-filtration/hero.jpg',
    'service_piping_installation': 'static/src/img/services/piping-installation/hero.jpg',
    'service_consultation_audits': 'static/src/img/services/consultation-audits/hero.jpg',
    'service_rental': 'static/src/img/services/rental/hero.jpg',
    'service_training_primegear': 'static/src/img/services/training-primegear/hero.jpg',
}

# slug -> the mobile side-menu's current short label for each of the 7
# original services (previously hand-authored website.menu records kept
# separately from this model, so a newly-added atlasco.service never showed
# up there — see AtlascoService._seed_sidemenu_labels / the sidemenu now
# reading straight from this model in atlasco_layout.xml). Seeded once so
# switching to the dynamic sidemenu is a no-visible-change upgrade for the
# 7 existing services; any new one just uses its full Name until someone
# optionally sets a shorter sidemenu_label.
_SERVICE_SIDEMENU_LABELS = {
    'condition-monitoring': 'Machine Condition Monitoring',
    'after-sales-support': 'After-Sales Support',
    'oil-analysis-filtration': 'Oil Analysis & Filtration',
    'piping-installation': 'Piping & Installation',
    'consultation-audits': 'Consultation Services',
    'rental': 'Rental Services',
    'training-primegear': 'Training (PrimeGear)',
}


class AtlascoService(models.Model):
    _name = "atlasco.service"
    _description = "Atlasco Service"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    name = fields.Char("Service Name", required=True)
    slug = fields.Char("URL Slug", required=True, help="Drives /services/<slug>.")
    subtitle = fields.Char("Subtitle")
    intro = fields.Text("Intro (Detail Page)")

    # /services listing card copy — shorter than the detail-page intro.
    card_description = fields.Text("Card Description (Listing Page)")

    hero_image = fields.Image("Hero Image")

    # PrimeGear Training links out to /primegear instead of its own detail
    # page on the listing card; kept generic so any future service can do
    # the same without a code change.
    link_override = fields.Char(
        "Listing Card Link Override",
        help="Optional. If set, the /services listing card's 'Learn More' "
             "link points here instead of /services/<slug>.")

    is_dark_panel = fields.Boolean(
        "Show as Featured Dark Panel",
        default=False,
        help="Renders this service's listing row as the dark, full-width "
             "closing panel (used today for Training / PrimeGear Academy) "
             "instead of a normal alternating row.")

    sidemenu_label = fields.Char(
        "Sidemenu Label (optional, shorter)",
        help="Optional shorter label for the mobile side-menu's Services "
             "panel, which has limited width. Falls back to the full "
             "Service Name if left blank.")

    offering_ids = fields.One2many(
        "atlasco.service.offering", "service_id", string="Sub-Offerings")

    _sql_constraints = [
        ("slug_uniq", "unique(slug)", "That service slug is already used."),
    ]

    # ClickUp 869f0826p: this model creates its own public page path
    # (/services/<slug>, same as atlasco.partner and
    # atlasco.industry.product) but was missing the shared SEO-slug
    # convention check those two already enforce — a gap in this ticket's
    # own "for ALL future pages, not just Partners" scope, found while
    # verifying it (a slug like "Bad_Slug With Spaces" saved with zero
    # error before this).
    @api.constrains("slug")
    def _check_slug_is_seo_convention(self):
        for rec in self:
            validate_seo_slug(rec.slug)

    def href(self):
        self.ensure_one()
        return self.link_override or ("/services/%s" % (self.slug or ""))

    @api.model
    def _seed_hero_images(self):
        """Idempotently backfill hero_image for the seeded services from the
        bundled static hero.jpg each one used to reference by hardcoded path.
        See _seed_utils.backfill_images_from_static.
        """
        return backfill_images_from_static(
            self.env, 'atlasco_website', _SERVICE_HERO_IMAGES, field='hero_image')

    @api.model
    def _seed_sidemenu_labels(self):
        """Idempotently backfill sidemenu_label for the 7 original services
        from the labels their (now-superseded) website.menu sidemenu
        records used. Only fills rows whose sidemenu_label is still empty,
        so a manual edit is never clobbered on a later module upgrade.
        """
        for slug, label in _SERVICE_SIDEMENU_LABELS.items():
            rec = self.search([('slug', '=', slug), ('sidemenu_label', '=', False)], limit=1)
            if rec:
                rec.sidemenu_label = label


class AtlascoServiceOffering(models.Model):
    _name = "atlasco.service.offering"
    _description = "Atlasco Service Sub-Offering"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    service_id = fields.Many2one("atlasco.service", required=True, ondelete="cascade")
    name = fields.Char("Name", required=True)
    desc = fields.Text("Description")
