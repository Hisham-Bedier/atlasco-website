import logging
import mimetypes
import os

from odoo import api, fields, models
from odoo.modules.module import get_module_path

_logger = logging.getLogger(__name__)

# Media dialog (web_editor's "Images" tab) only lists ir.attachment rows — it
# never scans a module's static/ folder on disk (see web_editor's
# file_selector.js fetchAttachments(), which is a plain ir.attachment
# search_read). Every image under atlasco_website/static/src/img is a bare
# file with no ir.attachment record, so none of them are reachable from the
# picker: an editor who wants to reuse a project photo on a new page has no
# way to find it there. Odoo's own website module works around this the same
# way for its bundled library (see website/data/image_library.xml) — a
# type='url' ir.attachment per file, res_model='ir.ui.view', public=True.
# _seed_static_image_library() below does the equivalent for this module's
# own static images, generated at upgrade time instead of hand-listed, since
# there are ~400 of them across the site.
_MEDIA_LIBRARY_MIMETYPES = {
    '.jpg': 'image/jpeg',
    '.jpeg': 'image/jpeg',
    '.jpe': 'image/jpe',
    '.png': 'image/png',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.webp': 'image/webp',
}

# Client images recovered after the 2026-07-22 COW reset.
#
# Held as real Image fields on the content singleton rather than as Char paths
# or as editor-placed images in the view override. Both of the older approaches
# failed: the Char path fields were orphaned when the templates were hardcoded
# (the fields still hold values that nothing reads), and editor-placed images
# lived in the per-website view override, which is exactly what got deleted.
# An Image field on a model survives both a module upgrade and a COW reset.
#
# (field name, source attachment name, source attachment id)
_RECOVERED = [
    ("home_primegear_bg", "Prime Gear Home page Banner", 2589),
]


class AtlascoContentMedia(models.Model):
    _inherit = "atlasco.content"

    careers_hero_banner_alt = fields.Char(
        "Careers · Hero Banner Alt", translate=True,
        default="Careers at Atlasco",
        help="Alt text for the /careers hero banner. The image widget reads alt "
             "from a field; without this it falls back to the record name.")
    home_primegear_bg = fields.Image(
        "Home · PrimeGear Background",
        help="Background photo behind the PrimeGear Academy section on the "
             "homepage. Replaces the static prime-gear-home.png when set.")

    @api.model
    def _seed_recovered_media(self):
        """Idempotently restore the client's uploads into their slots.

        Skips any field that already holds an image, so a later edit is never
        clobbered on upgrade. Falls back to a name lookup if attachment ids
        shift (restore, migration). Safe to run repeatedly.
        """
        rec = self.sudo().search([], limit=1)
        if not rec:
            return False
        Att = self.env["ir.attachment"].sudo()
        for field_name, att_name, att_id in _RECOVERED:
            if rec[field_name]:
                continue
            att = Att.browse(att_id).exists()
            if not att or att.name != att_name + ".png":
                att = Att.search([("name", "=", att_name + ".png")], limit=1)
            if att and att.datas:
                rec.write({field_name: att.datas})
        return True

    @api.model
    def _seed_static_image_library(self):
        """Register every atlasco_website static image as an ir.attachment.

        Makes them appear in the website editor's media-picker "Images" tab
        (ClickUp 869f082gg — "image path from project folder doesn't appear
        in picker"), the same way Odoo registers its own bundled library in
        website/data/image_library.xml. Idempotent: matches on url, so an
        upgrade never creates duplicates and any attachment an editor later
        renames/removes by hand is left alone.

        Walks the module's static/src/img tree on disk rather than hand-
        listing ~400 files; unsupported extensions (the media dialog's
        IMAGE_MIMETYPES list, e.g. .avif) are skipped, not registered, since
        Odoo would filter them out of the picker anyway. Safe to call on
        every upgrade.
        """
        module = 'atlasco_website'
        module_path = get_module_path(module)
        if not module_path:
            _logger.warning(
                "atlasco_website: could not resolve module path; skipping "
                "static image library seed.")
            return 0

        img_root = os.path.join(module_path, 'static', 'src', 'img')
        if not os.path.isdir(img_root):
            return 0

        Att = self.env['ir.attachment'].sudo()
        existing_urls = set(Att.search([('url', '=like', '/%s/static/src/img/%%' % module)]).mapped('url'))

        to_create = []
        for dirpath, _dirnames, filenames in os.walk(img_root):
            for filename in sorted(filenames):
                ext = os.path.splitext(filename)[1].lower()
                mimetype = _MEDIA_LIBRARY_MIMETYPES.get(ext)
                if not mimetype:
                    continue
                relpath = os.path.relpath(os.path.join(dirpath, filename), img_root)
                relpath = relpath.replace(os.sep, '/')
                url = '/%s/static/src/img/%s' % (module, relpath)
                if url in existing_urls:
                    continue
                to_create.append({
                    'name': relpath,
                    'public': True,
                    'res_model': 'ir.ui.view',
                    'type': 'url',
                    'url': url,
                    'mimetype': mimetype,
                })

        if to_create:
            Att.create(to_create)
        return len(to_create)
