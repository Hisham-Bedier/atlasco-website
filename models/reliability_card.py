from odoo import api, fields, models


class AtlascoReliabilityCard(models.Model):
    """Per-industry "reliability / predictive-maintenance" card.

    Migrated out of the hardcoded INDUSTRY_RELIABILITY dict in
    controllers/main.py so the text AND image of each card are editable —
    inline in the Website editor (t-field) and in the backend.
    """
    _name = "atlasco.reliability.card"
    _description = "Atlasco Industry Reliability Card"
    _order = "industry_slug, sequence, id"

    industry_slug = fields.Char(
        "Industry", required=True, index=True,
        help="Industry page slug this card belongs to, e.g. 'pharmaceutical'.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    problem = fields.Char("Challenge", translate=True)
    solution_title = fields.Char("Solution Title", translate=True)
    solution_body = fields.Text("Solution Body", translate=True)
    image = fields.Image("Image")
    name = fields.Char(compute="_compute_name")

    @api.depends("industry_slug", "problem")
    def _compute_name(self):
        for rec in self:
            rec.name = "%s / %s" % (rec.industry_slug or "-", rec.problem or "")

    @api.model
    def _seed_from_controller(self):
        """Idempotently seed cards from the hardcoded controller dict.

        Only seeds a slug that has NO cards yet, so manual edits are never
        clobbered on a later module upgrade. Safe to run repeatedly.
        """
        try:
            from odoo.addons.atlasco_website.controllers.main import (
                INDUSTRY_RELIABILITY,
            )
        except Exception:
            return False
        for slug, payload in (INDUSTRY_RELIABILITY or {}).items():
            cards = (payload or {}).get("cards") or []
            if not cards or self.search_count([("industry_slug", "=", slug)]):
                continue
            seq = 10
            for c in cards:
                self.create({
                    "industry_slug": slug,
                    "sequence": seq,
                    "problem": c.get("problem"),
                    "solution_title": c.get("solution_title"),
                    "solution_body": c.get("solution_body"),
                })
                seq += 10
        return True
