from odoo import models, fields

# --- Intro paragraphs (About page) ---
_ABOUT_INTRO_P1 = ("With over 35 years of proven excellence, Atlasco Egypt has been a trusted partner "
                   "in serving the industrial sector, consistently delivering reliable, "
                   "high-performance solutions across diverse industries.")
_ABOUT_INTRO_P2 = ("At the core of our strength lies one of the most effective and dependable "
                   "maintenance systems in the country—built on advanced technologies and certified "
                   "expertise in specialized tools from the Netherlands and Sweden.")
_ABOUT_INTRO_P3 = ("Driven by innovation, Atlasco has expanded into the medical sector, proudly "
                   "supporting governmental and private hospitals with advanced Medical Gas Systems "
                   "that protect and save lives.")

# --- Vision ---
_ABOUT_VISION_P1 = ("Becoming the region's trusted engineering reference for industrial reliability, "
                    "where global technology, regional capability, and practical expertise come "
                    "together in shaping stronger, smarter, and more resilient industries.")
_ABOUT_VISION_P2 = ("Atlasco Egypt continues expanding its capabilities across compressed air, gas "
                    "generation, oil filtration, condition monitoring, training, and reliability "
                    "services, building an engineering ecosystem that supports sustainable industrial "
                    "growth across Egypt and the MENA region.")

# --- Mission ---
_ABOUT_MISSION_P1 = ("Delivering integrated industrial solutions, engineering services, and "
                     "reliability-driven support that strengthen operational performance, protect "
                     "critical assets, and create long-term value for every customer we serve.")
_ABOUT_MISSION_P2 = ("Through premium global partnerships, certified expertise, and responsive "
                     "after-sales capabilities, Atlasco Egypt brings world-class technologies into "
                     "real industrial application — helping industries operate with greater "
                     "confidence, efficiency, and continuity.")


class AtlascoContentAbout(models.Model):
    _inherit = 'atlasco.content'

    # /about — Hero
    about_hero_alt = fields.Char('About · Hero Alt', default='Atlasco Egypt')

    # /about — Intro
    # Two plain Char fields rendered as separate block-level spans (matching
    # the hero-title convention used elsewhere in this module) instead of a
    # single fields.Html with an embedded <br/> — the Website editor's save
    # (save_embedded_field) crashed with KeyError: None on that literal <br/>,
    # silently failing to persist any edit made to this heading.
    about_intro_title_line1 = fields.Char('About · Intro Title Line 1', default='Powering Performance.')
    about_intro_title_line2 = fields.Char('About · Intro Title Line 2', default='Delivering Trust.')
    about_intro_p1 = fields.Text('About · Intro Paragraph 1', default=_ABOUT_INTRO_P1)
    about_intro_p2 = fields.Text('About · Intro Paragraph 2', default=_ABOUT_INTRO_P2)
    about_intro_p3 = fields.Text('About · Intro Paragraph 3', default=_ABOUT_INTRO_P3)
    about_logo_image = fields.Char(
        'About · Logo Image',
        default='/atlasco_website/static/src/img/logo/ate-monogram.png')
    about_logo_alt = fields.Char('About · Logo Alt', default='Atlasco Egypt — ATE Monogram')
    about_logo_name = fields.Char('About · Logo Name', default='ATLASCO EGYPT')
    about_logo_tagline = fields.Char(
        'About · Logo Tagline', default='CERTIFIED SUPPLIERS & CONSULTANTS')

    # /about — Mission / Vision / Video
    about_mv_label = fields.Char('About · MV Section Label', default='The Atlasco Edge')
    about_vision_eyebrow = fields.Char('About · Vision Eyebrow', default='VISION')
    about_vision_title = fields.Char('About · Vision Title', default='Our Vision')
    about_vision_p1 = fields.Text('About · Vision Paragraph 1', default=_ABOUT_VISION_P1)
    about_vision_p2 = fields.Text('About · Vision Paragraph 2', default=_ABOUT_VISION_P2)
    about_mission_eyebrow = fields.Char('About · Mission Eyebrow', default='MISSION')
    about_mission_title = fields.Char('About · Mission Title', default='Our Mission')
    about_mission_p1 = fields.Text('About · Mission Paragraph 1', default=_ABOUT_MISSION_P1)
    about_mission_p2 = fields.Text('About · Mission Paragraph 2', default=_ABOUT_MISSION_P2)
    about_video_src = fields.Char(
        'About · Edge Video',
        default='/atlasco_website/static/src/video/about-atlasco-edge.mp4')
    about_video_aria = fields.Char('About · Edge Video Aria Label', default='Atlasco Edge')

    # /about — What Sets Us Apart
    about_diff_label = fields.Char('About · Differentiators Section Label',
                                   default='The Atlasco Edge')
    about_diff_title = fields.Char('About · Differentiators Title',
                                   default='What Sets Us Apart')
    about_differentiator_ids = fields.One2many(
        'atlasco.about.differentiator', 'content_id', string='About · Differentiators')


class AtlascoAboutDifferentiator(models.Model):
    _name = 'atlasco.about.differentiator'
    _description = 'Atlasco About — What Sets Us Apart Item'
    _order = 'sequence, id'

    content_id = fields.Many2one(
        'atlasco.content', ondelete='cascade', required=True,
        default=lambda self: self.env['atlasco.content']._get().id)
    sequence = fields.Integer(default=10)
    title = fields.Char('Title', required=True)
    body = fields.Text('Body')
