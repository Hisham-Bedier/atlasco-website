from odoo import api, models, fields

from ._seed_utils import backfill_images_from_static

# Static-file backfill map for the team members seeded in data/seed_team.xml.
# Used once by _backfill_photo_from_static() below to populate the new
# binary 'photo' field from the bundled file each member's old Char path
# field used to point at, so the fix doesn't blank out the team page on
# upgrade. Safe/idempotent — see _seed_utils.py.
_TEAM_MEMBER_PHOTOS = {
    'team_member_nabil_soliman': 'static/src/img/team/nabil-soliman.png',
    'team_member_george_soliman': 'static/src/img/team/george-soliman.png',
    'team_member_naguib_maher': 'static/src/img/team/naguib-maher.png',
    'team_member_raafat_henry': 'static/src/img/team/raafat-henry.png',
    'team_member_reham_dorry': 'static/src/img/team/reham-dorry-20260615.jpg',
    'team_member_saied_elgamal': 'static/src/img/team/saied-elgamal.png',
    'team_member_mina_ibrahim': 'static/src/img/team/mina-ibrahim.png',
    'team_member_emad_guindy': 'static/src/img/team/emad-guindy.png',
    'team_member_ahmed_tawhid': 'static/src/img/team/ahmed-tawhid.png',
    'team_member_mina_samir': 'static/src/img/team/mina-samir.jpg',
}

_TEAM_LEAD = ("Guided by visionaries with decades of collective experience in the "
              "global engineering landscape.")

# /about/team — Chairman-message card current strings (exact reproduction of team.xml)
_TEAM_CMSG_P1 = ("It is with great pride that we witness the outcome of years of dedication, "
                 "perseverance, and commitment—Atlasco Egypt evolving into a trusted name "
                 "synonymous with integrity and reliability.")
_TEAM_CMSG_P2 = ("Our journey has been shaped by a team driven by passion, expertise, and a shared "
                 "vision for excellence. Together, we have built strong, long-standing partnerships "
                 "with leading international brands in mechanical engineering, enabling us to deliver "
                 "world-class solutions to the industries we serve.")
_TEAM_CMSG_P3 = ("Over the years, we have successfully expanded our presence, entering new markets "
                 "and industries while maintaining a reputation for efficiency, effectiveness, and "
                 "technical excellence.")
_TEAM_CMSG_P4 = ("To our valued customers, your trust has always been the foundation of our success. "
                 "It is both our responsibility and our privilege to continue serving you with "
                 "reliable solutions, superior products, and consistent results that support your "
                 "operational success.")
_TEAM_CMSG_P5 = ("On behalf of everyone at Atlasco Egypt, I extend our sincere gratitude for your "
                 "continued confidence and partnership. We remain committed to growing together and "
                 "delivering even greater value in the years ahead.")


class AtlascoContentTeam(models.Model):
    _inherit = 'atlasco.content'

    # /about/team — page-level scalar copy
    team_hero_label = fields.Char('Team · Hero Label', default='Our Team')
    team_hero_title = fields.Char('Team · Hero Title', default='People Behind Atlasco Egypt')
    team_board_eyebrow = fields.Char('Team · Board Eyebrow', default='Leadership')
    team_board_title = fields.Char('Team · Board Title', default='Board of Directors')
    team_team_eyebrow = fields.Char('Team · Team Eyebrow', default='The Team')
    team_team_title = fields.Char('Team · Team Title', default='Leadership Excellence')
    team_team_lead = fields.Text('Team · Team Lead', default=_TEAM_LEAD)

    # /about/team — Chairman-message card (own surface; do NOT reuse ceo_* fields)
    team_cmsg_portrait = fields.Char(
        'Team · Chairman Portrait',
        default='/atlasco_website/static/src/img/chairman-nabil-handoff.jpg')
    team_cmsg_portrait_alt = fields.Char(
        'Team · Chairman Portrait Alt',
        default='Eng. Nabil Soliman, Chairman of Atlasco Egypt')
    team_cmsg_name = fields.Char('Team · Chairman Name', default='Eng. Nabil Soliman')
    team_cmsg_role = fields.Char('Team · Chairman Role', default='CHAIRMAN, ATLASCO EGYPT')
    team_cmsg_kicker = fields.Char('Team · Chairman Kicker', default='Chairman Message')
    team_cmsg_p1 = fields.Text('Team · Chairman Paragraph 1', default=_TEAM_CMSG_P1)
    team_cmsg_p2 = fields.Text('Team · Chairman Paragraph 2', default=_TEAM_CMSG_P2)
    team_cmsg_p3 = fields.Text('Team · Chairman Paragraph 3', default=_TEAM_CMSG_P3)
    team_cmsg_p4 = fields.Text('Team · Chairman Paragraph 4', default=_TEAM_CMSG_P4)
    team_cmsg_p5 = fields.Text('Team · Chairman Paragraph 5', default=_TEAM_CMSG_P5)

    team_member_ids = fields.One2many('atlasco.team.member', 'content_id',
                                      string='Team Members')


class AtlascoTeamMember(models.Model):
    _name = 'atlasco.team.member'
    _description = 'Atlasco Team Member'
    _order = 'sequence, id'

    content_id = fields.Many2one('atlasco.content', string='Content',
                                 ondelete='cascade', required=True)
    sequence = fields.Integer('Sequence', default=10)
    section = fields.Selection(
        [('board', 'Board of Directors'), ('team', 'Leadership Team')],
        string='Section', default='team', required=True)
    name = fields.Char('Name', required=True)
    role = fields.Char('Role')
    photo = fields.Image('Photo', max_width=1200, max_height=1200)
    photo_legacy_path = fields.Char(
        'Photo Path (legacy, unused)',
        help="Old static-file path field this record used before image "
             "upload/delete was wired up. No longer read by the template; "
             "kept only for reference and safe to remove in a later cleanup.")
    fx_delay = fields.Char('FX Delay', default='0')
    bio = fields.Text('Bio')
    social_linkedin = fields.Char('LinkedIn')
    social_twitter = fields.Char('Twitter / X')
    social_email = fields.Char('Email')

    @api.model
    def _backfill_photo_from_static(self):
        """Idempotently backfill the new 'photo' field for the seeded team
        members from the bundled static files the old Char path field used
        to point at. See _seed_utils.backfill_images_from_static.
        """
        return backfill_images_from_static(
            self.env, 'atlasco_website', _TEAM_MEMBER_PHOTOS, field='photo')
