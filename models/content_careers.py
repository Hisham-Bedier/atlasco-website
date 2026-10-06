from odoo import api, models, fields

from ._seed_utils import backfill_images_from_static

# The 3 "Life Beyond the Workplace" photo tiles never had a real photo
# uploaded, so they always rendered the site's static fallback banner
# (visually identical across all 3, just cropped differently per tile
# width) - see AtlascoCultureLife._backfill_photo_tile_images below, which
# restores that same look but through the real, editable `photo` field
# instead of a hard-coded <img src>.
_CULTURE_LIFE_PHOTO_IMAGES = {
    'seed_culture_life_photo_1': 'static/src/img/banners/careers-culture.jpg',
    'seed_culture_life_photo_2': 'static/src/img/banners/careers-culture.jpg',
    'seed_culture_life_photo_3': 'static/src/img/banners/careers-culture.jpg',
}

# ---------------------------------------------------------------------------
# Long copy defaults (kept as module constants for readability). Every value is
# the EXACT current hard-coded string from views/careers.xml so a fresh install
# renders byte-identical.
# ---------------------------------------------------------------------------

# --- Careers page ---
_CR_HERO_BODY = ("Be part of a 35-year engineering legacy built on excellence, trust, and strong "
                 "values — where people are supported, respected, and empowered to grow within a "
                 "healthy and collaborative environment.")

# --- Culture page ---
_CU_HERO_BODY = ("More than a workplace — an environment where people are respected, developed, and "
                 "trusted to deliver meaningful impact within a culture of strong values and "
                 "collaboration.")
_CU_OVERVIEW_BODY = ("At Atlasco, we offer more than a workplace — we build an environment where "
                     "people are respected, developed, and trusted to deliver meaningful impact, "
                     "while growing within a culture defined by strong values, collaboration, and "
                     "long-term commitment.")


class AtlascoContent(models.Model):
    _inherit = 'atlasco.content'

    # =====================================================================
    # CAREERS  (/careers)
    # =====================================================================
    # Hero
    careers_hero_badge = fields.Char('Careers · Hero Badge', default="WE'RE HIRING · JOIN THE TEAM")
    careers_hero_title = fields.Char('Careers · Hero Title (line 1)', default='Join the Legacy.')
    careers_hero_title_hl = fields.Char('Careers · Hero Title (highlight)', default='Future')
    careers_hero_title_end = fields.Char('Careers · Hero Title (line 3)', default='of Egyptian Industry.')
    careers_hero_body = fields.Text('Careers · Hero Body', default=_CR_HERO_BODY)
    careers_hero_cta1 = fields.Char('Careers · Hero CTA 1', default='Explore Open Roles')
    careers_hero_cta2 = fields.Char('Careers · Hero CTA 2', default='See Our Culture')
    careers_stat1_num = fields.Char('Careers · Stat 1 Number', default='35+')
    careers_stat1_label = fields.Char('Careers · Stat 1 Label', default='Years Legacy')
    careers_stat2_num = fields.Char('Careers · Stat 2 Number', default='6')
    careers_stat2_label = fields.Char('Careers · Stat 2 Label', default='Core Benefits')
    careers_stat3_num = fields.Char('Careers · Stat 3 Number', default='100%')
    careers_stat3_label = fields.Char('Careers · Stat 3 Label', default='Customer-Centered')
    careers_hero_video = fields.Char('Careers · Hero Video',
                                     default='/atlasco_website/static/src/video/careers-team.mp4')
    careers_hero_float_title = fields.Char('Careers · Hero Float Title', default='People-first')
    careers_hero_float_sub = fields.Char('Careers · Hero Float Subtitle', default='culture, every day')

    # Trust pills
    careers_pill1 = fields.Char('Careers · Trust Pill 1', default='35+ Years of Industry Presence')
    careers_pill2 = fields.Char('Careers · Trust Pill 2', default='Cross-Functional Team Culture')
    careers_pill3 = fields.Char('Careers · Trust Pill 3', default='Continuous Learning & Development')
    careers_pill4 = fields.Char('Careers · Trust Pill 4', default='Recognized for Customer-Centered Approach')
    careers_pill5 = fields.Char('Careers · Trust Pill 5', default='Global Industry Partnerships')

    # Why build section
    careers_why_eyebrow = fields.Char('Careers · Why Eyebrow', default='WHY ATLASCO')
    careers_why_title = fields.Char('Careers · Why Title', default='Why Build Your Career at Atlasco?')

    # Benefits section
    careers_ben_eyebrow = fields.Char('Careers · Benefits Eyebrow', default='EMPLOYEE BENEFITS')
    careers_ben_title = fields.Char('Careers · Benefits Title', default='What We Offer Our People')

    # Openings section
    careers_open_eyebrow = fields.Char('Careers · Openings Eyebrow', default='OPPORTUNITIES AT ATLASCO')
    careers_open_title = fields.Char('Careers · Openings Title', default='Current Openings')
    careers_job_desc_label = fields.Char('Careers · Job Description Label', default='Job Description:')
    careers_job_cta = fields.Char('Careers · Job Apply CTA', default='Apply Now')

    # Apply section
    careers_apply_eyebrow = fields.Char('Careers · Apply Eyebrow', default='GET STARTED')
    careers_apply_title = fields.Char('Careers · Apply Title', default='Apply to Join Atlasco')

    # Collections
    careers_why_ids = fields.One2many('atlasco.career.why', 'content_id', string='Careers · Why Cards')
    careers_benefit_ids = fields.One2many('atlasco.career.benefit', 'content_id', string='Careers · Benefits')
    careers_opening_ids = fields.One2many('atlasco.career.opening', 'content_id', string='Careers · Openings')

    # =====================================================================
    # CULTURE  (/culture)
    # =====================================================================
    # Hero
    culture_hero_badge = fields.Char('Culture · Hero Badge', default='LIFE & CULTURE AT ATLASCO')
    culture_hero_title = fields.Char('Culture · Hero Title (line 1)', default='Where People &')
    culture_hero_title_hl = fields.Char('Culture · Hero Title (highlight)', default='Performance')
    culture_hero_title_end = fields.Char('Culture · Hero Title (end)', default=' Grow')
    culture_hero_body = fields.Text('Culture · Hero Body', default=_CU_HERO_BODY)
    culture_hero_cta1 = fields.Char('Culture · Hero CTA 1', default='Explore Our Values')
    culture_hero_cta2 = fields.Char('Culture · Hero CTA 2', default='Join the Team')
    culture_hero_video = fields.Char('Culture · Hero Video',
                                     default='/atlasco_website/static/src/video/careers-team.mp4')
    culture_hero_float_title = fields.Char('Culture · Hero Float Title', default='35 Years')
    culture_hero_float_sub = fields.Char('Culture · Hero Float Subtitle', default='of shared values')

    # Overview
    culture_ov_eyebrow = fields.Char('Culture · Overview Eyebrow', default='WHERE PEOPLE & PERFORMANCE MEET')
    culture_ov_title = fields.Char('Culture · Overview Title',
                                   default='Atlasco is Where People and Performance Grow Together')
    culture_ov_body = fields.Text('Culture · Overview Body', default=_CU_OVERVIEW_BODY)
    culture_ov_tag1 = fields.Char('Culture · Overview Tag 1', default='Respected')
    culture_ov_tag2 = fields.Char('Culture · Overview Tag 2', default='Developed')
    culture_ov_tag3 = fields.Char('Culture · Overview Tag 3', default='Trusted')
    culture_ov_tag4 = fields.Char('Culture · Overview Tag 4', default='Empowered')
    culture_ov_image = fields.Char('Culture · Overview Image',
                                   default='/atlasco_website/static/src/img/banners/careers-culture.jpg')
    culture_ov_image_alt = fields.Char('Culture · Overview Image Alt', default='Atlasco team')
    culture_ov_badge_num = fields.Char('Culture · Overview Badge Number', default='35+')
    culture_ov_badge_text1 = fields.Char('Culture · Overview Badge Text 1', default="Years building Egypt's")
    culture_ov_badge_text2 = fields.Char('Culture · Overview Badge Text 2', default='industrial backbone')

    # Core values
    culture_val_eyebrow = fields.Char('Culture · Values Eyebrow', default='OUR DNA')
    culture_val_title = fields.Char('Culture · Values Title', default='Core Values We Live By')

    # Life section
    culture_life_eyebrow = fields.Char('Culture · Life Eyebrow', default='LIFE AT ATLASCO')
    culture_life_title = fields.Char('Culture · Life Title', default='Life Beyond the Workplace')
    culture_life_body = fields.Char('Culture · Life Body',
                                    default='A glimpse into the moments that make Atlasco more than just a company.')
    # Life gallery — primary local video (GEM Gathering). Editable URL so the
    # Website Editor can change / replace / link the video source in place.
    culture_gem_video = fields.Char('Culture · GEM Gallery Video',
                                    default='/atlasco_website/static/src/video/gem-event.mp4')

    # Awards section
    culture_aw_eyebrow = fields.Char('Culture · Awards Eyebrow', default='AWARDS & RECOGNITION')
    culture_aw_title = fields.Char('Culture · Awards Title', default='Recognized for How We Work')

    # CTA section
    culture_cta_title = fields.Char('Culture · CTA Title', default='Like What You See? Come Build With Us.')
    culture_cta_body = fields.Text('Culture · CTA Body',
                                   default='If our culture feels like home, explore open roles and start your journey with Atlasco.')
    culture_cta_btn1 = fields.Char('Culture · CTA Button 1', default='Explore Careers')
    culture_cta_btn2 = fields.Char('Culture · CTA Button 2', default='Apply Now')

    # Collections
    culture_value_ids = fields.One2many('atlasco.culture.value', 'content_id', string='Culture · Values')
    culture_life_ids = fields.One2many('atlasco.culture.life', 'content_id', string='Culture · Life Tiles')
    culture_award_ids = fields.One2many('atlasco.culture.award', 'content_id', string='Culture · Awards')
    culture_voice_ids = fields.One2many('atlasco.culture.voice', 'content_id', string='Culture · Voices')


# ===========================================================================
# CAREERS collection models
# ===========================================================================
class AtlascoCareerWhy(models.Model):
    _name = 'atlasco.career.why'
    _description = 'Atlasco Careers — Why Build Card'
    _order = 'sequence, id'

    content_id = fields.Many2one('atlasco.content', ondelete='cascade', required=True)
    sequence = fields.Integer(default=10)
    title = fields.Char('Title')
    body = fields.Text('Body')


class AtlascoCareerBenefit(models.Model):
    _name = 'atlasco.career.benefit'
    _description = 'Atlasco Careers — Employee Benefit'
    _order = 'sequence, id'

    content_id = fields.Many2one('atlasco.content', ondelete='cascade', required=True)
    sequence = fields.Integer(default=10)
    title = fields.Char('Title')
    body = fields.Text('Body')


class AtlascoCareerOpening(models.Model):
    _name = 'atlasco.career.opening'
    _description = 'Atlasco Careers — Job Opening'
    _order = 'sequence, id'

    content_id = fields.Many2one('atlasco.content', ondelete='cascade', required=True)
    sequence = fields.Integer(default=10)
    title = fields.Char('Title')
    department = fields.Char('Department', help="Shown as the coloured tag on the job card, e.g. \"Service\", \"Sales\".")
    location = fields.Char('Location')
    job_type = fields.Char('Type')
    blurb = fields.Char('Card Blurb', help="Short 1-2 line summary shown on the job card itself.")
    description = fields.Text('Description', help="Longer description; not currently shown on the live careers page.")
    points = fields.Text('What You\'ll Do (one per line)',
                          help="Bullet points shown when a visitor clicks \"View details\". One point per line.")


# ===========================================================================
# CULTURE collection models
# ===========================================================================
class AtlascoCultureValue(models.Model):
    _name = 'atlasco.culture.value'
    _description = 'Atlasco Culture — Core Value'
    _order = 'sequence, id'

    content_id = fields.Many2one('atlasco.content', ondelete='cascade', required=True)
    sequence = fields.Integer(default=10)
    title = fields.Char('Title')
    body = fields.Text('Body')


class AtlascoCultureLife(models.Model):
    _name = 'atlasco.culture.life'
    _description = 'Atlasco Culture — Life Gallery Tile'
    _order = 'sequence, id'

    content_id = fields.Many2one('atlasco.content', ondelete='cascade', required=True)
    sequence = fields.Integer(default=10)
    label = fields.Char('Label')
    # 'video' (self-hosted mp4, real "Replace video" upload button on the
    # tile) or 'photo' (real uploaded image, see `photo` below). 'iframe'
    # (external Google Drive embed) used to be a third type, but that left
    # the raw Drive URL as page copy the admin had to paste/edit by hand —
    # no upload, no real click-to-replace. Migrated to 'video' by
    # _migrate_iframe_tiles_to_video() below, same fix already applied to
    # the /careers hero video (see atlasco_careers_page.xml / vsrc below).
    vtype = fields.Char('Tile Type (video/photo)')
    vsrc = fields.Char('Video Source (video tiles only)')
    poster = fields.Char('Inline Poster Video')
    # Real attachment-backed image for 'photo' tiles — editable from the
    # Website Editor (click-to-replace, since it's rendered via a
    # `t-field`/widget="image" converter, same pattern as the homepage
    # hero carousel) and from the backend Culture admin list.
    photo = fields.Image('Photo', max_width=1920, max_height=1920)
    photo_alt = fields.Char('Photo Alt Text')
    # Real upload for 'video' tiles from the backend list itself (previously
    # the only way to add a real video was the Website Editor's own "Replace
    # video" button on the live page - vsrc had to be typed/pasted by hand
    # here, same "no real upload" gap 'iframe' had). attachment=True stores
    # it as a real ir.attachment rather than inline base64, same as `photo`.
    video_file = fields.Binary('Upload Video', attachment=True)
    video_filename = fields.Char('Video Filename')

    def write(self, vals):
        res = super().write(vals)
        if 'video_file' in vals:
            self._sync_vsrc_from_video_file()
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        records.filtered(lambda r: r.video_file)._sync_vsrc_from_video_file()
        return records

    def _sync_vsrc_from_video_file(self):
        for rec in self:
            if rec.video_file:
                rec.vsrc = '/web/content/atlasco.culture.life/%d/video_file/%s?unique=%s' % (
                    rec.id, rec.video_filename or 'video.mp4', int(rec.write_date.timestamp()))
            else:
                rec.vsrc = False

    @api.model
    def _migrate_iframe_tiles_to_video(self):
        """One-time migration: 'iframe' tiles (Google Drive embeds) become
        'video' tiles so they get the same real "Replace video" upload
        button as GEM Gathering, instead of a raw URL left as editable page
        text. Their old Drive preview link can't play as a <video src> (it's
        an embed page, not a direct file), so vsrc is cleared rather than
        left silently broken — the tile shows empty until someone uploads a
        real mp4 via "Replace video". Idempotent: only ever touches rows
        still tagged 'iframe', so re-running (or a record an admin already
        fixed by hand) is a no-op.
        """
        tiles = self.search([('vtype', '=', 'iframe')])
        tiles.write({'vtype': 'video', 'vsrc': False})

    @api.model
    def _backfill_photo_tile_images(self):
        """Idempotently give the 3 photo tiles their old look back (the
        static fallback banner they always rendered before the tile
        started reading the real `photo` field) so they show real content
        immediately instead of an empty "add image" placeholder. Only fills
        rows whose `photo` is still empty, so a real upload is never
        clobbered on a later module upgrade.
        """
        return backfill_images_from_static(
            self.env, 'atlasco_website', _CULTURE_LIFE_PHOTO_IMAGES, field='photo')


class AtlascoCultureAward(models.Model):
    _name = 'atlasco.culture.award'
    _description = 'Atlasco Culture — Award / Recognition'
    _order = 'sequence, id'

    content_id = fields.Many2one('atlasco.content', ondelete='cascade', required=True)
    sequence = fields.Integer(default=10)
    title = fields.Char('Title')
    body = fields.Text('Body')


class AtlascoCultureVoice(models.Model):
    _name = 'atlasco.culture.voice'
    _description = 'Atlasco Culture — Employee Voice / Testimonial'
    _order = 'sequence, id'

    content_id = fields.Many2one('atlasco.content', ondelete='cascade', required=True)
    sequence = fields.Integer(default=10)
    quote = fields.Text('Quote')
    person_role = fields.Char('Role / Title')
    years_label = fields.Char('Years at Company')
    avatar = fields.Image('Avatar')
