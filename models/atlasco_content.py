from odoo import models, fields, api


class AtlascoContent(models.Model):
    """Singleton holding the editable text/image content of the Atlasco website.

    Every field default is the current hard-coded value from the QWeb templates,
    so a fresh install / upgrade renders byte-identical to before. Editing a field
    from the backend form updates the live site with no template change.
    """
    _name = 'atlasco.content'
    _description = 'Atlasco Website Editable Content'

    name = fields.Char(default='Atlasco Website Content')

    @api.model
    def _get(self):
        # Always resolve to the one canonical singleton seeded via xmlid, so
        # every collection and every page render use the same record.
        rec = self.env.ref('atlasco_website.content_singleton', raise_if_not_found=False)
        if not rec:
            rec = self.search([], limit=1) or self.create({})
        return rec
