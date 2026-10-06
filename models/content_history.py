from odoo import api, models, fields

from ._seed_utils import backfill_images_from_static

# ---------------------------------------------------------------------------
# /about/history — page scalar copy defaults
# ---------------------------------------------------------------------------
_HIST_HERO_SUB = ("From humble beginnings to industry leader — a journey of growth, "
                  "innovation, and trust.")
_HIST_CTA_SUB = "Join thousands of industrial and medical partners who trust Atlasco Egypt."

# Static-file backfill map for the Timeline Milestones seeded in
# data/seed_history.xml. Used once by _seed_milestone_images() below — see
# the matching comment in content_home.py for why this exists. Milestones
# from 2021 onward were seeded without an image ("Emad to provide") so they
# have no entry here.
_MILESTONE_IMAGES = {
    'history_ms_1990': 'static/src/img/history/1990-founding.png',
    'history_ms_1992': 'static/src/img/history/1992-ecoair.jpg',
    'history_ms_1994': 'static/src/img/history/1994-sotras.jpg',
    'history_ms_1995': 'static/src/img/history/1995-canal.jpg',
    'history_ms_1998': 'static/src/img/history/1998-cement.jpg',
    'history_ms_2007': 'static/src/img/history/2007-oxymat.jpg',
    'history_ms_2008': 'static/src/img/history/1995-canal.jpg',
    'history_ms_2010': 'static/src/img/history/2010-office.jpg',
    'history_ms_2013': 'static/src/img/history/2013-generators.jpg',
    'history_ms_2014': 'static/src/img/history/2014-stiavelli.jpg',
    'history_ms_2015': 'static/src/img/history/2015-25years.jpg',
    'history_ms_2016': 'static/src/img/history/2016-57357.jpg',
    'history_ms_2017': 'static/src/img/history/2017-primegear.png',
    'history_ms_2018': 'static/src/img/history/2018-ue.jpg',
    'history_ms_2019': 'static/src/img/history/2019-mobius.png',
    'history_ms_2020': 'static/src/img/history/2020-compair.png',
}


class AtlascoContentHistory(models.Model):
    _inherit = 'atlasco.content'

    # Hero
    history_hero_label = fields.Char('History · Hero Label', default='Our Story')
    history_hero_title = fields.Char('History · Hero Title', default='35 Years of Excellence')
    history_hero_sub = fields.Text('History · Hero Subtitle', default=_HIST_HERO_SUB)

    # Meta bar
    history_meta_text = fields.Char('History · Meta Bar',
                                    default='Milestones — Descending (Newest First)')

    # Timeline scroll rail
    history_rail_start_year = fields.Char('History · Rail Start Year', default='1990')

    # Milestone image-less placeholder box (two text lines around a <br/>)
    history_photo_placeholder_1 = fields.Char('History · Photo Placeholder Line 1',
                                              default='Photo')
    history_photo_placeholder_2 = fields.Char('History · Photo Placeholder Line 2',
                                              default='[Emad to provide]')

    # Legacy CTA
    history_cta_title = fields.Char('History · CTA Title',
                                    default='A Legacy Built on Trust and Excellence')
    history_cta_sub = fields.Text('History · CTA Subtitle', default=_HIST_CTA_SUB)

    # Collections
    history_milestone_ids = fields.One2many(
        'atlasco.history.milestone', 'content_id', string='History · Milestones')
    history_stat_ids = fields.One2many(
        'atlasco.history.stat', 'content_id', string='History · Stats')


class AtlascoHistoryMilestone(models.Model):
    _name = 'atlasco.history.milestone'
    _description = 'Atlasco History — Timeline Milestone'
    _order = 'sequence, id'

    content_id = fields.Many2one(
        'atlasco.content', ondelete='cascade', required=True,
        default=lambda self: self.env['atlasco.content']._get().id)
    sequence = fields.Integer(default=10)

    # 'standard' = light two-column scene (data-scene="1"); 'parallax' = dark full-bleed scene.
    variant = fields.Selection(
        [('standard', 'Standard'), ('parallax', 'Parallax')],
        string='Variant', default='standard', required=True)
    # Standard scenes alternate flex-direction row / row-reverse.
    reverse = fields.Boolean('Reverse Layout', default=False)

    year = fields.Char('Year', required=True)
    title = fields.Char('Title')
    # Up to five body paragraphs; blank ones render no <p>.
    body_1 = fields.Text('Paragraph 1')
    body_2 = fields.Text('Paragraph 2')
    body_3 = fields.Text('Paragraph 3')
    body_4 = fields.Text('Paragraph 4')
    body_5 = fields.Text('Paragraph 5')

    # Image for standard scenes with a photo, and for parallax scenes.
    # Blank on a standard scene renders the dashed "Emad to provide" placeholder box.
    image = fields.Image('Image')
    image_legacy_path = fields.Char(
        'Image Path (legacy, unused)',
        help="Old static-file path field this milestone used before image "
             "upload/delete was wired up. No longer read by the template; "
             "kept only for reference and safe to remove in a later cleanup.")

    @api.model
    def _seed_milestone_images(self):
        """Idempotently backfill the new 'image' field for the seeded
        Timeline Milestones from the bundled static files the old Char path
        field used to point at. See _seed_utils.backfill_images_from_static.
        """
        return backfill_images_from_static(
            self.env, 'atlasco_website', _MILESTONE_IMAGES)


class AtlascoHistoryStat(models.Model):
    _name = 'atlasco.history.stat'
    _description = 'Atlasco History — Green Stat'
    _order = 'sequence, id'

    content_id = fields.Many2one(
        'atlasco.content', ondelete='cascade', required=True,
        default=lambda self: self.env['atlasco.content']._get().id)
    sequence = fields.Integer(default=10)
    number = fields.Char('Number', required=True)
    label = fields.Char('Label')
