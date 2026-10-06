import base64
import os

from odoo import api, fields, models
from odoo.modules.module import get_module_resource


class AtlascoHomeSlide(models.Model):
    """A single slide of the homepage hero carousel.

    Held in a model (rather than as a one-off editor snippet) so slides are
    backend-manageable and reorderable, while staying editable both in the
    backend and inline on the site. The homepage falls back to the original
    single static hero when no slides exist.
    """
    _name = "atlasco.home.slide"
    _description = "Atlasco Homepage Hero Slide"
    _order = "sequence, id"

    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    name = fields.Char("Slide Name", required=True, default="Slide")
    image = fields.Image("Slide Image", help="Full-bleed artwork. 1920x1080 (16:9) recommended.")
    image_alt = fields.Char("Image Alt Text", translate=True)

    # --- optional text overlay -------------------------------------------
    show_overlay = fields.Boolean(
        "Show Text Overlay", default=False,
        help="Draw headline/subtitle/button over this slide. Leave off for artwork "
             "that already contains its own text.")
    text_theme = fields.Selection(
        [("light", "Light text (dark artwork)"), ("dark", "Dark text (light artwork)")],
        string="Text Theme", default="light")
    established = fields.Char("Eyebrow", translate=True)
    line1 = fields.Char("Headline Line 1", translate=True)
    highlight = fields.Char("Headline Highlight", translate=True)
    subtitle = fields.Text("Subtitle", translate=True)
    btn_label = fields.Char("Button Label", translate=True)
    btn_url = fields.Char("Button URL", default="/about")

    @api.model
    def _load_static_image(self, filename):
        """Base64 bytes of a static file bundled under static/src/img/banners,
        or False if it can't be found (never raises — a missing image just
        means an empty slide image, not a broken upgrade)."""
        full = get_module_resource('atlasco_website', 'static', 'src', 'img', 'banners', filename)
        if not full or not os.path.isfile(full):
            return False
        with open(full, 'rb') as f:
            return base64.b64encode(f.read())

    @api.model
    def _seed_default_slides(self):
        """Idempotently seed 3 slides from the existing homepage banner
        artwork so turning on the carousel starts with real photos instead
        of an empty state. Slide 1 matches the site's current static hero
        (same image + text) so nothing changes until slides 2/3 are added.
        Does nothing once any slide exists, so later edits/additions are
        never clobbered on a later module upgrade.
        """
        if self.search_count([]):
            return False

        content = self.env['atlasco.content'].sudo()._get()
        hero = self.env['atlasco.page.hero'].sudo().search([('key', '=', 'home')], limit=1)

        slide1_image = (hero.image if hero and hero.image else False) \
            or self._load_static_image('home-hero-v3-20260629.jpg')

        self.create({
            'sequence': 10,
            'name': 'Slide 1',
            'image': slide1_image,
            'image_alt': 'Atlasco Egypt products and facility',
            'show_overlay': True,
            'text_theme': 'dark',
            'established': content.home_hero_established,
            'line1': content.home_hero_line1,
            'highlight': content.home_hero_highlight,
            'subtitle': content.home_hero_subtitle,
            'btn_label': content.home_hero_btn,
            'btn_url': '/about',
        })
        self.create({
            'sequence': 20,
            'name': 'Slide 2',
            'image': self._load_static_image('home.jpg'),
            'image_alt': 'Atlasco Egypt products and facility',
            'show_overlay': True,
            'text_theme': 'dark',
            'established': content.home_hero_established,
            'line1': content.home_hero_line1,
            'highlight': content.home_hero_highlight,
            'subtitle': content.home_hero_subtitle,
            'btn_label': content.home_hero_btn,
            'btn_url': '/about',
        })
        self.create({
            'sequence': 30,
            'name': 'Slide 3',
            'image': self._load_static_image('home-hero-1280x540-v2.jpg'),
            'image_alt': 'Atlasco Egypt products and facility',
            'show_overlay': False,
        })
        return True
