from odoo import api, models, fields, _

from ._seed_utils import backfill_images_from_static

# Static-file backfill map for the Industry Cards seeded in
# data/seed_home.xml. Used once by _seed_industry_card_images() below to
# populate the new binary 'image' field from the bundled file each card's
# old Char path field used to point at, so the fix doesn't blank out the
# homepage on upgrade. Safe/idempotent — see _seed_utils.py.
_INDUSTRY_CARD_IMAGES = {
    'seed_home_industry_1': 'static/src/img/industries/cards/card-oil-gas.jpg',
    'seed_home_industry_2': 'static/src/img/industries/cards/card-pharmaceutical.jpg',
    'seed_home_industry_3': 'static/src/img/industries/cards/card-medical.jpg',
    'seed_home_industry_4': 'static/src/img/industries/cards/card-steel.jpg',
    'seed_home_industry_5': 'static/src/img/industries/cards/card-food-beverage.jpg',
    'seed_home_industry_6': 'static/src/img/industries/cards/card-textile.jpg',
    'seed_home_industry_7': 'static/src/img/industries/cards/card-electronics.jpg',
    'seed_home_industry_8': 'static/src/img/industries/cards/card-cement.jpg',
    'seed_home_industry_9': 'static/src/img/industries/cards/card-construction.jpg',
    'seed_home_industry_10': 'static/src/img/industries/cards/card-oil-gas.jpg',
}

# Seed values for card_name/card_desc, keyed by the href slug (last segment
# of the 'href' field, e.g. '/industries/oil-gas' -> 'oil-gas'). Reproduces
# the text the "Related Industries" cards on /industries/<slug> already show
# today (previously hard-coded in controllers/main.py's industry_detail()),
# so switching that section to read these fields is a no-visible-change
# upgrade. See _seed_related_industry_cards() below.
_INDUSTRY_CARD_TEXT = {
    'oil-gas': ('Oil & Gas', 'Atlasco Egypt delivers advanced air and reliability solutions for the '
                'toughest oil & gas environments—ensuring safe and uninterrupted operations.'),
    'pharmaceutical': ('Pharmaceutical', 'ISO-certified Class II clean air solutions for pharmaceutical '
                        'manufacturing excellence.'),
    'medical': ('Medical', 'Medical grade oxygen and vacuum systems for life-critical environments.'),
    'steel': ('Steel', 'High-pressure compressed air systems purpose-built for steel manufacturing.'),
    'food-beverage': ('Food & Beverage', 'Hygienic compressed air for processing lines in food and '
                       'beverage production.'),
    'power-generation': ('Power Generation', 'High-pressure systems for turbine cooling and power '
                          'generation facilities.'),
    'textile': ('Textile', 'Compressed air, blowers, and condition-monitoring solutions for textile mills.'),
    'electronics': ('Electronics', 'Clean, oil-free air and high-purity gas systems for electronics '
                     'manufacturing.'),
    'cement': ('Cement', 'Heavy-duty compressed air, vacuum, and dust-collection systems for cement plants.'),
    'construction': ('Construction', 'Portable compressors, generators, and on-site equipment for '
                      'construction sites.'),
}

# ---------------------------------------------------------------------------
# Long / multi-line copy blocks extracted as constants for readability.
# Each default MUST reproduce the current hard-coded HTML text EXACTLY.
# ---------------------------------------------------------------------------
_HOME_HERO_SUBTITLE = ("Pioneering industrial engineering and sustainable enterprise solutions "
                       "for Egypt's evolving landscape.")

_SOL_CA_BODY = ("Atlasco Egypt provides complete compressed air systems designed to support stable "
                "production, improve energy efficiency, and ensure dependable operation across critical "
                "industrial applications. Through trusted branded equipment, system integration, and "
                "technical support, Atlasco helps plants maintain reliable air supply with lower "
                "operational risk.")
_SOL_GAS_BODY = ("Atlasco Egypt provides reliable gas generation systems designed to help industrial "
                 "facilities produce oxygen or nitrogen directly on site. Through advanced PSA technology, "
                 "integrated equipment packages, and technical support, Atlasco helps customers reduce "
                 "cylinder dependency, improve operational safety, and maintain a stable gas supply for "
                 "critical applications.")
_SOL_OIL_BODY = ("Atlasco Egypt provides advanced oil filtration and lubrication management solutions that "
                 "help industrial facilities protect critical equipment, reduce contamination, and extend "
                 "lubricant and component life. Through oil purification, varnish removal, contamination "
                 "control, and visual inspection tools, Atlasco supports more reliable operation and lower "
                 "maintenance risk across rotating and hydraulic assets.")
_SOL_FLUID_BODY = ("Atlasco Egypt provides advanced fluid and lubrication analysis solutions that help "
                   "industrial facilities evaluate lubricant health, detect contamination, and identify "
                   "early signs of equipment wear. Through portable analysis devices, particle counting "
                   "systems, and laboratory-grade technologies, Atlasco supports data-driven maintenance "
                   "programs that help reduce failure risk, improve maintenance planning, and increase "
                   "asset reliability.")
_SOL_CM_BODY = ("Atlasco Egypt provides condition monitoring and predictive maintenance solutions that "
                "help industrial facilities identify machine abnormalities before they develop into costly "
                "failures. Through advanced vibration analysis, ultrasound inspection, bearing condition "
                "monitoring, and air leak detection technologies, Atlasco supports maintenance teams in "
                "improving asset reliability, optimizing maintenance planning, and keeping operations "
                "running safely and efficiently.")

_PARTNERS_LEAD = ("At Atlasco Egypt, our partners are more than suppliers — they are an extension of our "
                  "commitment to ")  # remainder is <strong> markup, kept literal in template

# Solutions-tab checklists, one entry per bullet. These used to be plain
# hardcoded <li> text in homepage.xml with no data-oe-model/field binding at
# all, so clicking into one in the Website Editor let you type (it sits
# inside an editable region) but Save silently discarded it - there was no
# field for Odoo to persist the change to. A single Text field (first fix
# attempted here) made the text data-driven but still didn't fix the actual
# complaint: a Text field can't be individually inline-edited per bullet
# either, only as one blob via the backend form. Real per-bullet inline
# editing on the live page needs each bullet to be its own record with its
# own t-field, same as every other repeatable list in this codebase
# (atlasco.career.why, atlasco.culture.value, etc.) - see
# AtlascoHomeSolutionCheck below. Seeded from these lists, keyed by tab.
_SOL_CHECKS_SEED = {
    'ca': ["Oil-lubricated air compressors", "Oil-free air compressors", "Compressed air dryers",
           "Air receivers and storage tanks", "Filtration and air treatment units",
           "Piping and complete system packages", "Installation, commissioning, and after-sales support"],
    'gas': ["PSA oxygen generators", "PSA nitrogen generators", "Buffer tanks",
            "Air treatment and filtration units", "Control panels and monitoring systems",
            "Piping and complete system integration", "Installation, commissioning, and after-sales support"],
    'oil': ["Oil filtration systems", "Oil purification units", "Varnish removal solutions",
            "Coalescers and collector elements", "Desiccant breathers", "Contamination control products",
            "Oil sight glasses and inspection tools", "Installation, commissioning, and technical support"],
    'fluid': ["Oil analysis systems", "Lubricant condition monitoring", "Particle counting systems",
              "Fluid contamination analysis", "Wear debris analysis", "Portable fluid analysis devices",
              "Laboratory analysis systems", "On-site analysis support",
              "Technical consultation and reliability reporting"],
    'cm': ["Vibration analysis and machine diagnostics", "Bearing condition monitoring",
           "Ultrasound inspection", "Compressed air leak detection", "Steam trap and valve inspection",
           "Mechanical fault detection", "Electrical inspection support",
           "Predictive maintenance tools and technical services"],
}

_CAREERS_BODY = ("At Atlasco, we don't just supply equipment; we solve complex challenges. We are always "
                 "looking for passionate engineers and specialists to help us power Egypt's industries.")

_PRIMEGEAR_TITLE = "Where Atlasco's Engineering Legacy Shapes Reliability Leaders"
_PRIMEGEAR_BODY = ("As a sister company of Atlasco Egypt, PrimeGear Academy carries forward a legacy built "
                   "on engineering excellence, industrial experience, and long-term commitment to "
                   "reliability. Created to transform technical knowledge into practical capability, "
                   "PrimeGear empowers engineers, maintenance teams, and reliability professionals through "
                   "internationally recognized training programs, global partnerships, and field-driven "
                   "learning experiences. It is where industry knowledge becomes professional growth "
                   "— and where the next generation of reliability leaders is built.")


class AtlascoContentHome(models.Model):
    _inherit = 'atlasco.content'

    # --- HERO ---
    home_hero_established = fields.Char('Home · Hero Established', default='Established 1989')
    home_hero_line1 = fields.Char('Home · Hero Line 1', default='35 YEARS OF')
    home_hero_highlight = fields.Char('Home · Hero Highlight', default='EXCELLENCE')
    home_hero_subtitle = fields.Text('Home · Hero Subtitle', default=_HOME_HERO_SUBTITLE)
    home_hero_btn = fields.Char('Home · Hero Button', default='Discover Atlasco →')

    # --- SOLUTIONS section header ---
    home_solutions_label = fields.Char('Home · Solutions Label', default='Comprehensive Solutions')
    home_solutions_title = fields.Char('Home · Solutions Title',
                                       default='End-to-End Industrial Solutions')

    # Tab button labels (the first tab has an inline arrow span, rendered literally in template)
    home_tab_btn_ca = fields.Char('Home · Tab Button · Compressed Air', default='Compressed Air Systems')
    home_tab_btn_gas = fields.Char('Home · Tab Button · Gas', default='Gas Generation Systems')
    home_tab_btn_oil = fields.Char('Home · Tab Button · Oil',
                                   default='Oil Filtration & Lubrication Management')
    home_tab_btn_fluid = fields.Char('Home · Tab Button · Fluid',
                                     default='Fluid & Lubrication Analysis')
    home_tab_btn_cm = fields.Char('Home · Tab Button · Condition Monitoring',
                                  default='Condition Monitoring & Predictive Maintenance')
    home_solution_check_ids = fields.One2many('atlasco.home.solution.check', 'content_id',
                                              string='Home · Solutions Checklists')

    # Compressed Air tab
    home_sol_ca_title = fields.Char('Home · CA Title', default='Compressed Air Systems')
    home_sol_ca_sub = fields.Text('Home · CA Subtitle',
                                  default='Reliable compressed air solutions for continuous industrial performance')
    home_sol_ca_body = fields.Text('Home · CA Body', default=_SOL_CA_BODY)
    home_sol_ca_link = fields.Char('Home · CA Link', default='View Compressed Air Systems →')
    home_sol_ca_image = fields.Char('Home · CA Image',
                                    default='/atlasco_website/static/src/img/solutions/compressed-air-system.jpg')
    home_sol_ca_image_alt = fields.Char('Home · CA Image Alt', default='Compressed Air Systems')

    # Gas Generation tab
    home_sol_gas_title = fields.Char('Home · Gas Title', default='Gas Generation Systems')
    home_sol_gas_sub = fields.Text('Home · Gas Subtitle',
                                   default='On-site oxygen and nitrogen generation for continuous industrial supply')
    home_sol_gas_body = fields.Text('Home · Gas Body', default=_SOL_GAS_BODY)
    home_sol_gas_link = fields.Char('Home · Gas Link', default='View Gas Generation Systems →')
    home_sol_gas_image = fields.Char('Home · Gas Image',
                                     default='/atlasco_website/static/src/img/solutions/gas-generation-system.jpg')
    home_sol_gas_image_alt = fields.Char('Home · Gas Image Alt', default='Gas Generation Systems')

    # Oil Filtration tab (title & alt contain & entity -> stored as literal ampersand)
    home_sol_oil_title = fields.Char('Home · Oil Title', default='Oil Filtration & Lubrication Management')
    home_sol_oil_sub = fields.Text('Home · Oil Subtitle',
                                   default='Cleaner oil, protected assets, and stronger machine reliability')
    home_sol_oil_body = fields.Text('Home · Oil Body', default=_SOL_OIL_BODY)
    home_sol_oil_link = fields.Char('Home · Oil Link', default='View Lubrication & Oil Systems →')
    home_sol_oil_image = fields.Char('Home · Oil Image',
                                     default='/atlasco_website/static/src/img/solutions/oil-filtration-lubrication.jpg')
    home_sol_oil_image_alt = fields.Char('Home · Oil Image Alt',
                                         default='Oil Filtration & Lubrication Management')

    # Fluid Analysis tab
    home_sol_fluid_title = fields.Char('Home · Fluid Title', default='Fluid & Lubrication Analysis')
    home_sol_fluid_sub = fields.Text('Home · Fluid Subtitle',
                                     default='Turn oil and fluid data into smarter maintenance decisions')
    home_sol_fluid_body = fields.Text('Home · Fluid Body', default=_SOL_FLUID_BODY)
    home_sol_fluid_link = fields.Char('Home · Fluid Link', default='View Fluid Analysis →')
    home_sol_fluid_image = fields.Char('Home · Fluid Image',
                                       default='/atlasco_website/static/src/img/solutions/fluid-lubrication-analysis.jpg')
    home_sol_fluid_image_alt = fields.Char('Home · Fluid Image Alt',
                                           default='Fluid & Lubrication Analysis')

    # Condition Monitoring tab
    home_sol_cm_title = fields.Char('Home · CM Title',
                                    default='Condition Monitoring & Predictive Maintenance')
    home_sol_cm_sub = fields.Text('Home · CM Subtitle',
                                  default='Detect faults early, protect critical assets, and reduce unplanned downtime')
    home_sol_cm_body = fields.Text('Home · CM Body', default=_SOL_CM_BODY)
    home_sol_cm_link = fields.Char('Home · CM Link', default='Learn About A.R.M.S. →')
    home_sol_cm_image = fields.Char('Home · CM Image',
                                    default='/atlasco_website/static/src/img/solutions/condition-monitoring-predictive.jpg')
    home_sol_cm_image_alt = fields.Char('Home · CM Image Alt',
                                        default='Condition Monitoring & Predictive Maintenance')

    # --- INDUSTRIES section header ---
    home_industries_label = fields.Char('Home · Industries Label', default='From Precision to Performance')
    home_industries_title = fields.Char('Home · Industries Title', default='Industries We Serve')
    home_industries_viewall = fields.Char('Home · Industries View-All', default='View all industries →')
    home_industries_viewall_url = fields.Char('Home · Industries View-All URL', default='/industries')

    # --- PARTNERS (editorial) ---
    home_partners_eyebrow = fields.Char('Home · Partners Eyebrow', default='Our Global Partners')
    home_partners_h2_1 = fields.Char('Home · Partners H2 Row 1', default='Strategic')
    home_partners_h2_2 = fields.Char('Home · Partners H2 Row 2', default='Partnerships')
    home_partners_h2_3 = fields.Char('Home · Partners H2 Row 3', default='that drive')
    home_partners_h2_4 = fields.Char('Home · Partners H2 Row 4', default='performance.')
    # lead paragraph: plain lede + bold clause kept as two fields (the <strong> stays literal in template)
    home_partners_lead = fields.Text('Home · Partners Lead (before bold)', default=_PARTNERS_LEAD)
    home_partners_lead_bold = fields.Char('Home · Partners Lead (bold clause)',
                                          default='reliability, performance, and long-term value.')
    home_partners_lead_tail = fields.Text('Home · Partners Lead (after bold)',
                                          default=(' We collaborate with globally recognised manufacturers to '
                                                   'deliver advanced industrial solutions that perform under the '
                                                   'most demanding conditions.'))
    home_partners_cta = fields.Char('Home · Partners CTA', default='Meet our partners →')
    # The honeycomb's own "Show all partners" hexagon tile (built entirely in
    # JS — see initPartnerComb() in atlasco.js) had its href hardcoded to
    # '/partners' directly in the script, completely disconnected from any
    # field or CMS content — nothing in the Website Editor or backend could
    # ever touch it. Passed down to the JS via a data attribute on the
    # honeycomb container (#atlPartnerComb) in the template below.
    home_partners_showall_url = fields.Char('Home · Partners "Show All" Hexagon URL', default='/partners')

    # --- SEPARATOR logo ---
    home_sep_logo_image = fields.Char('Home · Separator Logo',
                                      default='/atlasco_website/static/src/img/logo/ate-monogram.png')
    home_sep_logo_alt = fields.Char('Home · Separator Logo Alt', default='ATLASCO EGYPT')

    # --- CAREERS cine section ---
    home_careers_label = fields.Char('Home · Careers Label', default='Careers & Culture')
    home_careers_h2_1 = fields.Char('Home · Careers Heading Row 1', default='Join a Legacy')
    home_careers_h2_2 = fields.Char('Home · Careers Heading Row 2', default='of Engineering')
    home_careers_h2_3 = fields.Char('Home · Careers Heading Row 3', default='Excellence')
    home_careers_body = fields.Text('Home · Careers Body', default=_CAREERS_BODY)
    home_careers_btn = fields.Char('Home · Careers Button', default='Meet The Team')
    home_careers_bg_image = fields.Char('Home · Careers Background',
                                        default='/atlasco_website/static/src/img/careers-culture-bg-v2.jpg')
    home_careers_bg_alt = fields.Char('Home · Careers Background Alt', default='Atlasco engineering team')

    # --- PRIMEGEAR cine section ---
    home_primegear_label = fields.Char('Home · PrimeGear Label', default='PrimeGear Academy')
    home_primegear_title = fields.Char('Home · PrimeGear Title', default=_PRIMEGEAR_TITLE)
    home_primegear_body = fields.Text('Home · PrimeGear Body', default=_PRIMEGEAR_BODY)
    home_primegear_btn = fields.Char('Home · PrimeGear Button', default='Explore PrimeGear Academy')
    home_primegear_bg_image = fields.Char('Home · PrimeGear Background',
                                          default='/atlasco_website/static/src/img/primegear/prime-gear-home.png')
    home_primegear_bg_alt = fields.Char('Home · PrimeGear Background Alt', default='PrimeGear Academy')

    # --- Separator / "Best Selling" cards section ---
    home_sep_eyebrow = fields.Char('Home · Separator Eyebrow', default='Featured Equipment')
    home_sep_heading = fields.Char('Home · Separator Heading', default='Our Best Selling')

    # --- Collections ---
    home_stat_ids = fields.One2many('atlasco.home.stat', 'content_id', string='Home Stats')
    home_industry_ids = fields.One2many('atlasco.home.industry', 'content_id', string='Home Industries')
    home_sepcard_ids = fields.One2many('atlasco.home.sepcard', 'content_id', string='Home Separator Cards')


class AtlascoHomeStat(models.Model):
    _name = 'atlasco.home.stat'
    _description = 'Atlasco Home Stat Counter'
    _order = 'sequence, id'

    sequence = fields.Integer('Sequence', default=10)
    content_id = fields.Many2one('atlasco.content', ondelete='cascade')
    target = fields.Char('Data Target')   # numeric string, kept as Char to preserve exact text
    suffix = fields.Char('Data Suffix', default='+')
    label = fields.Char('Label')


class AtlascoHomeIndustry(models.Model):
    _name = 'atlasco.home.industry'
    _description = 'Atlasco Home Industry Card'
    _order = 'sequence, id'

    @api.depends('card_name', 'href')
    def _compute_display_name(self):
        # No `name` field on this model, so without this every picker
        # (e.g. the "Related Industries Shown On This Industry's Page" tags
        # widget) falls back to Odoo's generic "atlasco.home.industry,4"
        # label instead of something a human can actually pick from.
        for rec in self:
            label = rec.card_name or (
                rec.href.rsplit('/', 1)[-1].replace('-', ' ').title() if rec.href else False)
            rec.display_name = label or _("Unnamed industry card")

    sequence = fields.Integer('Sequence', default=10)
    content_id = fields.Many2one('atlasco.content', ondelete='cascade')
    href = fields.Char('Link URL')
    image = fields.Image('Image')
    image_legacy_path = fields.Char(
        'Image Path (legacy, unused)',
        help="Old static-file path field this card used before image "
             "upload/delete was wired up. No longer read by the template; "
             "kept only for reference and safe to remove in a later cleanup.")
    image_alt = fields.Char('Image Alt')
    fx_delay = fields.Char('FX Delay')          # data-fx-delay value ('' for first card)
    title = fields.Char('Title (may contain <br/>)')   # rendered via t-out to keep <br/> markup
    desc = fields.Text('Description')
    # Separate from title/desc above (those are homepage-grid-formatted:
    # all-caps, may contain <br/>, and desc is shared boilerplate) - these
    # back the "Related Industries" cards on /industries/<slug>, which need
    # their own differently-cased name and industry-specific blurb.
    card_name = fields.Char('Related-Card Name')
    card_desc = fields.Text('Related-Card Description')
    # Curates which industries show in THIS industry's own "Related
    # Industries" section on /industries/<slug> - e.g. Oil & Gas could list
    # just 3 specific ones instead of the site-wide default. Left empty,
    # industry_detail() falls back to its old behaviour (first 5 other
    # industries) - see controllers/main.py - so uncurated industries don't
    # change.
    related_industry_ids = fields.Many2many(
        'atlasco.home.industry', 'atlasco_home_industry_related_rel',
        'industry_id', 'related_id', string='Related Industries',
        help="Which industries appear in the \"Related Industries\" section "
             "on this industry's own page. Leave empty to keep the site "
             "default (first 5 other industries).")

    @api.model
    def _seed_industry_card_images(self):
        """Idempotently backfill the new 'image' field for the seeded
        Industry Cards from the bundled static files the old Char path
        field used to point at. See _seed_utils.backfill_images_from_static.
        """
        return backfill_images_from_static(
            self.env, 'atlasco_website', _INDUSTRY_CARD_IMAGES)

    @api.model
    def _seed_related_industry_cards(self):
        """Idempotently fill card_name/card_desc from the text the
        "Related Industries" cards already show today (moved out of
        controllers/main.py's hard-coded dict). Only touches records whose
        card_name is still empty, so a later edit made through the Website
        Editor is never overwritten.
        """
        for rec in self.search([('card_name', '=', False)]):
            if not rec.href:
                continue
            slug = rec.href.rsplit('/', 1)[-1]
            text = _INDUSTRY_CARD_TEXT.get(slug)
            if text:
                rec.write({'card_name': text[0], 'card_desc': text[1]})

    @api.model
    def _seed_default_related_industries(self):
        """Idempotently pre-fill related_industry_ids with what each
        industry's "Related Industries" section already shows today (first
        5 others, in _INDUSTRY_CARD_TEXT's slug order - the same order/logic
        controllers/main.py's industry_detail() used before this field
        existed), so the backend list always starts matching the live site,
        and removing a tag actually removes that industry from the page
        instead of silently falling back to the old default.

        Only touches a record whose related_industry_ids is still empty, so
        it never overwrites picks an admin already made (including a
        previous run of this same seed).
        """
        order = list(_INDUSTRY_CARD_TEXT.keys())
        by_slug = {
            rec.href.rsplit('/', 1)[-1]: rec
            for rec in self.search([]) if rec.href
        }
        for slug, rec in by_slug.items():
            if rec.related_industry_ids or slug not in order:
                continue
            others = [s for s in order if s != slug][:5]
            rec.related_industry_ids = [(6, 0, [by_slug[s].id for s in others if s in by_slug])]


class AtlascoHomeSepcard(models.Model):
    _name = 'atlasco.home.sepcard'
    _description = 'Atlasco Home Separator Card'
    _order = 'sequence, id'

    sequence = fields.Integer('Sequence', default=10)
    content_id = fields.Many2one('atlasco.content', ondelete='cascade')
    column = fields.Selection([('left', 'Left'), ('right', 'Right')],
                              string='Column', default='left')
    number = fields.Char('Number')       # '01' .. '06', kept exact
    category = fields.Char('Category')   # may contain & entity -> literal ampersand
    name = fields.Char('Product Name')


class AtlascoHomeSolutionCheck(models.Model):
    _name = 'atlasco.home.solution.check'
    _description = 'Atlasco Home — Solutions Tab Checklist Item'
    _order = 'tab, sequence, id'

    content_id = fields.Many2one('atlasco.content', ondelete='cascade', required=True)
    tab = fields.Selection([
        ('ca', 'Compressed Air'),
        ('gas', 'Gas Generation'),
        ('oil', 'Oil Filtration'),
        ('fluid', 'Fluid Analysis'),
        ('cm', 'Condition Monitoring'),
    ], required=True)
    sequence = fields.Integer(default=10)
    text = fields.Char('Bullet Text', required=True)

    @api.model
    def _seed_solution_checks(self):
        """Idempotent per tab: only seeds a tab that has zero rows yet, so
        re-running this on a later upgrade never touches a tab an admin has
        already edited/reordered/added to.
        """
        content = self.env['atlasco.content'].sudo()._get()
        existing_tabs = set(self.search([]).mapped('tab'))
        for tab, bullets in _SOL_CHECKS_SEED.items():
            if tab in existing_tabs:
                continue
            seq = 10
            for text in bullets:
                self.create({'content_id': content.id, 'tab': tab, 'sequence': seq, 'text': text})
                seq += 10
