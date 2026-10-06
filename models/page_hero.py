from odoo import api, fields, models

# Every page listed here already has a hardcoded fallback banner baked into
# the CSS/controller data or the page's own template, so an empty row is
# always safe: the site keeps looking exactly as it does today until
# someone uploads a replacement here.

_SITE_PAGES = [
    ('home', 'Homepage (/)'),
    ('about', 'About (/about)'),
    ('team', 'About — Our Team (/about/team)'),
    ('history', 'About — Our History (/about/history)'),
    ('culture', 'Culture (/culture)'),
    ('careers', 'Careers (/careers)'),
    ('industries', 'Industries (/industries)'),
    ('services', 'Services (/services)'),
    ('products', 'Products (/products)'),
    ('partners', 'Partners (/partners)'),
    ('primegear', 'PrimeGear Academy (/primegear)'),
    ('contact', 'Contact Us (/contact)'),
]

# Slugs/labels below are mirrored exactly from controllers/main.py's
# INDUSTRY_HERO_COPY / services / partners_data / PRODUCT_CATEGORIES dicts —
# keep in sync if a slug is ever renamed there.

_INDUSTRIES = [
    ('oil-gas', 'Oil & Gas'),
    ('steel', 'Steel'),
    ('pharmaceutical', 'Pharmaceutical'),
    ('medical', 'Medical'),
    ('food-beverage', 'Food & Beverage'),
    ('textile', 'Textile'),
    ('electronics', 'Electronics'),
    ('construction', 'Construction'),
    ('cement', 'Cement'),
]

_SERVICES = [
    ('condition-monitoring', 'Machine Condition Monitoring Services'),
    ('after-sales-support', 'After-Sales Services'),
    ('oil-analysis-filtration', 'Oil Analysis & Filtration Services'),
    ('piping-installation', 'Piping & Installation Services'),
    ('consultation-audits', 'Consultation Services'),
    ('rental', 'Rental Services'),
    ('training-primegear', 'Training Services (PrimeGear Academy)'),
]

_PARTNERS = [
    ('compair', 'CompAir'),
    ('oxymat', 'OXYMAT'),
    ('spm', 'SPM'),
    ('chart-industries', 'Chart Industries'),
    ('ept-clean-oil', 'EPT Clean Oil'),
    ('des-case', 'Des-Case'),
    ('filtertechnik', 'Filtertechnik'),
    ('continental-industrie', 'Continental Industrie'),
    ('schaeffler-smt', 'Schaeffler SMT / BETEX'),
    ('sotras', 'Sotras'),
    ('sdt-systems', 'SDT Ultrasound Solutions'),
    ('prevost', 'Prevost'),
    ('spectro-scientific', 'Spectro Scientific'),
    ('iriss', 'IRISS'),
    ('luneta', 'Luneta'),
    ('noria-corporation', 'Noria Corporation'),
    ('mobius-institute', 'Mobius Institute'),
    ('harvard-corporation', 'Harvard Corporation'),
    ('rmf-systems', 'RMF Systems'),
    ('stiavelli-irio', 'Stiavelli Irio'),
    ('itc', 'ITC (Infrared Training Center)'),
    ('atmos', 'Atmos'),
    ('bega-special-tools', 'Bega Special Tools'),
]

# (category slug, category label, [(product slug, product label), ...])
_PRODUCT_CATEGORIES = [
    ('air-compressors', 'Compressed Air Systems', [
        ('oil-screw-compressors', 'Oil Screw Compressors'),
        ('oil-free-air-compressors', 'Oil-Free Air Compressors'),
        ('portable-air-compressors', 'Portable Air Compressors'),
        ('high-pressure-compressors', 'High-Pressure Compressors'),
        ('compressed-air-packages', 'Compressed Air Packages'),
    ]),
    ('gas-generation', 'Gas Generation', [
        ('psa-nitrogen-generation-systems', 'PSA Nitrogen Generation Systems'),
        ('psa-oxygen-generation-systems', 'PSA Oxygen Generation Systems'),
        ('oxygen-filling-systems', 'Oxygen Filling Systems'),
        ('marine-specialized-gas-systems', 'Marine & Specialized Gas Systems'),
    ]),
    ('air-treatment', 'Air Treatment', [
        ('refrigerant-air-dryers', 'Refrigerant Air Dryers'),
        ('desiccant-air-dryers', 'Desiccant Air Dryers'),
        ('compressed-air-filters', 'Compressed Air Filters'),
        ('condensate-management-systems', 'Condensate Management Systems'),
    ]),
    ('vacuum-blowers', 'Vacuum & Blowers', [
        ('centrifugal-blowers', 'Centrifugal Blowers'),
        ('multi-stage-blowers', 'Multi-Stage Blowers'),
        ('vacuum-systems', 'Vacuum Systems'),
        ('axial-fans', 'Axial Fans'),
        ('process-heavy-duty-fans', 'Process & Heavy-Duty Fans'),
        ('gas-boosters', 'Gas Boosters'),
    ]),
    ('industrial-filtration', 'Industrial Filtration', [
        ('air-filtration-systems', 'Air Filtration Systems'),
        ('oil-hydraulic-filtration', 'Oil & Hydraulic Filtration'),
        ('fuel-filtration-systems', 'Fuel Filtration Systems'),
        ('dust-collection-filtration', 'Dust Collection & Filtration'),
        ('vacuum-compressor-filters', 'Vacuum & Compressor Filters'),
        ('filtration-units-systems', 'Filtration Units & Systems'),
    ]),
    ('lubrication-oil', 'Lubrication & Oil Systems', [
        ('oil-filtration-purification-systems', 'Oil Filtration & Purification Systems'),
        ('contamination-control-solutions', 'Contamination Control Solutions'),
        ('breathers-desiccant-systems', 'Breathers & Desiccant Systems'),
        ('lubricant-inspection-monitoring', 'Lubricant Inspection & Monitoring Tools'),
    ]),
    ('gas-storage', 'Air & Gas Storage', [
        ('air-receivers', 'Air Receivers'),
        ('pressure-vessels', 'Pressure Vessels'),
        ('cryogenic-storage-tanks', 'Cryogenic Storage Tanks'),
        ('gas-storage-distribution-systems', 'Gas Storage & Distribution Systems'),
        ('vaporizers-gas-handling-equipment', 'Vaporizers & Gas Handling Equipment'),
    ]),
    ('fluid-analysis', 'Fluid Analysis', [
        ('oil-analysis-instruments', 'Oil Analysis Instruments'),
        ('particle-counting-systems', 'Particle Counting Systems'),
        ('wear-debris-analysis-systems', 'Wear Debris Analysis Systems'),
        ('portable-fluid-analysis-devices', 'Portable Fluid Analysis Devices'),
        ('laboratory-analysis-systems', 'Laboratory Analysis Systems'),
        ('fluid-monitoring-software', 'Fluid Monitoring Software'),
    ]),
    ('control-automation', 'Control & Automation', [
        ('compressor-controllers', 'Compressor Controllers'),
        ('system-control-panels', 'System Control Panels'),
        ('sensors-transmitters', 'Sensors & Transmitters'),
        ('remote-monitoring-hardware', 'Remote Monitoring Hardware'),
        ('flow-pressure-control-equipment', 'Flow & Pressure Control Equipment'),
        ('integrated-control-systems', 'Integrated Control Systems'),
    ]),
    ('industrial-tools', 'Industrial Tools', [
        ('bearing-mounting-dismounting-tools', 'Bearing Mounting & Dismounting Tools'),
        ('induction-heaters', 'Induction Heaters'),
        ('hydraulic-tools-equipment', 'Hydraulic Tools & Equipment'),
        ('alignment-tools', 'Alignment Tools'),
        ('pullers-mechanical-tools', 'Pullers & Mechanical Tools'),
        ('maintenance-tool-kits', 'Maintenance Tool Kits'),
    ]),
]


def _build_page_hero_rows():
    """Flatten every section list above into (key, label, section) rows.

    Dynamic-page keys are prefixed by section ("industry_", "service_", ...)
    so they can never collide with each other or with a site-page key, and
    so a row's key alone tells you which controller dict/route it overrides.
    """
    rows = [(key, label, 'site_page') for key, label in _SITE_PAGES]
    rows += [('industry_%s' % slug, label, 'industry') for slug, label in _INDUSTRIES]
    rows += [('service_%s' % slug, label, 'service') for slug, label in _SERVICES]
    rows += [('partner_%s' % slug, label, 'partner') for slug, label in _PARTNERS]
    for cat_slug, cat_label, items in _PRODUCT_CATEGORIES:
        rows.append(('product_category_%s' % cat_slug, cat_label, 'product_category'))
        rows += [
            ('product_%s_%s' % (cat_slug, slug), '%s — %s' % (cat_label, label), 'product')
            for slug, label in items
        ]
    return rows


_PAGE_HERO_ROWS = _build_page_hero_rows()


class AtlascoPageHero(models.Model):
    """Background banner image for one page's hero section.

    One row per page on the site (site pages, industries, services,
    partners, product categories and individual products) — the single
    place to replace any hero banner photo. Group by Section to navigate
    the full list.
    """
    _name = 'atlasco.page.hero'
    _description = 'Atlasco Page Hero Banner'
    _order = 'sequence, id'

    key = fields.Char(required=True, index=True, readonly=True,
                       help="Stable internal identifier, not shown on the site.")
    sequence = fields.Integer(default=10)
    label = fields.Char('Page', required=True, readonly=True)
    section = fields.Selection([
        ('site_page', 'Site Pages'),
        ('industry', 'Industries'),
        ('service', 'Services'),
        ('partner', 'Partners'),
        ('product_category', 'Product Categories'),
        ('product', 'Products'),
    ], required=True, readonly=True, index=True, default='site_page')
    image = fields.Image('Background Image', help="Leave empty to keep the site's current default photo for this page.")

    _sql_constraints = [
        ('key_uniq', 'unique(key)', 'A page hero with this key already exists.'),
    ]

    @api.model
    def _image_url(self, key):
        """Image URL for `key`'s hero, or '' if no override was uploaded.

        Includes a `unique=` cache-buster derived from write_date. The bare
        `/web/image/<model>/<id>/<field>` URL never changes when the image
        is replaced, so a browser (or an intermediate proxy/CDN cache) that
        already fetched the old bytes for that exact URL keeps serving them
        indefinitely — from a client's point of view, re-uploading a banner
        silently "does nothing". Standard Odoo `t-field` image rendering
        appends this automatically; this hand-built URL didn't, so every
        page that reads its hero through this helper was exposed to it.
        """
        record = self.search([('key', '=', key)], limit=1)
        if not record.image:
            return ''
        unique = int(record.write_date.timestamp()) if record.write_date else 0
        return '/web/image/atlasco.page.hero/%d/image?unique=%s' % (record.id, unique)

    @api.model
    def _seed_pages(self):
        """Idempotently create one row per page in _PAGE_HERO_ROWS.

        Only creates rows for keys that don't exist yet, so re-running this
        after adding new pages to the list (or on a later module upgrade)
        never touches/duplicates existing rows or their uploaded images.
        """
        existing_keys = set(self.search([]).mapped('key'))
        seq = (max(self.search([]).mapped('sequence'), default=0) // 10) * 10 + 10
        created = False
        for key, label, section in _PAGE_HERO_ROWS:
            if key in existing_keys:
                continue
            self.create({'key': key, 'label': label, 'section': section, 'sequence': seq})
            seq += 10
            created = True
        return created
