from odoo import api, fields, models

# Verbatim copy of the product_range lists that were hardcoded per-partner in
# controllers/main.py's partners_data dict, keyed by partner slug, so a fresh
# install seeds byte-identical content.
_SEED_PARTNER_PRODUCTS = {
    'compair': [
        {'name': 'Lubricated Rotary Screw Compressors', 'url': '/products/air-compressors/oil-screw-compressors', 'external_url': 'https://www.compair.com'},
        {'name': 'Oil-Free Compressors', 'url': '/products/air-compressors/oil-free-air-compressors', 'external_url': 'https://www.compair.com'},
        {'name': 'Compressed Air Dryers', 'url': '/products/air-treatment/refrigerant-air-dryers', 'external_url': 'https://www.compair.com'},
        {'name': 'Air Treatment & Filtration Systems', 'url': '/products/air-treatment', 'external_url': 'https://www.compair.com'},
        {'name': 'Controllers & Remote Monitoring', 'url': '/products/control-automation', 'external_url': 'https://www.compair.com'},
        {'name': 'Portable Compressors', 'url': '/products/air-compressors/portable-air-compressors', 'external_url': 'https://www.compair.com'},
    ],
    'oxymat': [
        {'name': 'PSA Oxygen Generators', 'url': '/products/gas-generation/psa-oxygen-generation-systems', 'external_url': 'https://www.oxymat.com'},
        {'name': 'PSA Nitrogen Generators', 'url': '/products/gas-generation/psa-nitrogen-generation-systems', 'external_url': 'https://www.oxymat.com'},
        {'name': 'Membrane Nitrogen Generators', 'url': '/products/gas-generation', 'external_url': 'https://www.oxymat.com'},
        {'name': 'Hydrogen Generation Solutions', 'url': '/products/gas-generation', 'external_url': 'https://www.oxymat.com'},
    ],
    'spm': [
        {'name': 'Portable Vibration Analysis Instruments', 'url': '/services/condition-monitoring', 'external_url': 'https://www.spminstrument.com'},
        {'name': 'Shock Pulse Monitoring Systems', 'url': '/services/condition-monitoring', 'external_url': 'https://www.spminstrument.com'},
        {'name': 'Online Condition Monitoring Systems', 'url': '/services/condition-monitoring', 'external_url': 'https://www.spminstrument.com'},
        {'name': 'Condmaster Software & Diagnostics', 'url': '/services/condition-monitoring', 'external_url': 'https://www.spminstrument.com'},
    ],
    'chart-industries': [
        {'name': 'Cryogenic Bulk Storage Tanks', 'url': '/products/gas-storage/cryogenic-storage-tanks', 'external_url': 'https://www.chartindustries.com'},
        {'name': 'Ambient & Heated Vaporizers', 'url': '/products/gas-storage/vaporizers-gas-handling-equipment', 'external_url': 'https://www.chartindustries.com'},
        {'name': 'Liquid Gas Distribution Systems', 'url': '/products/gas-storage/gas-storage-distribution-systems', 'external_url': 'https://www.chartindustries.com'},
        {'name': 'Engineered Cryogenic Solutions', 'url': '/products/gas-storage', 'external_url': 'https://www.chartindustries.com'},
    ],
    'ept-clean-oil': [
        {'name': 'Varnish Removal Systems (SVR Series)', 'url': '/products/lubrication-oil/contamination-control-solutions', 'external_url': 'https://www.eptcleanoil.com'},
        {'name': 'Electrostatic Oil Cleaning Systems', 'url': '/products/lubrication-oil', 'external_url': 'https://www.eptcleanoil.com'},
        {'name': 'Depth Filtration Units', 'url': '/products/lubrication-oil', 'external_url': 'https://www.eptcleanoil.com'},
        {'name': 'On-Site Oil Recovery & Restoration', 'url': '/services/oil-analysis-filtration', 'external_url': 'https://www.eptcleanoil.com'},
    ],
    'des-case': [
        {'name': 'Standard & Extended Series Desiccant Breathers', 'url': '/products/lubrication-oil', 'external_url': 'https://des-case.com'},
        {'name': 'VentGuard™ Check-Valve Breathers', 'url': '/products/lubrication-oil', 'external_url': 'https://des-case.com'},
        {'name': 'Oil Storage & Transfer Systems', 'url': '/products/lubrication-oil', 'external_url': 'https://des-case.com'},
        {'name': 'Offline Filtration Systems', 'url': '/products/industrial-filtration', 'external_url': 'https://des-case.com'},
    ],
    'filtertechnik': [
        {'name': 'Particle Pal Portable Particle Counters', 'url': '/products/fluid-analysis', 'external_url': 'https://www.filtertechnik.co.uk'},
        {'name': 'Particle Pal Pro Digital Imaging Analyzers', 'url': '/products/fluid-analysis', 'external_url': 'https://www.filtertechnik.co.uk'},
        {'name': 'Oil Condition & Water Content Analyzers', 'url': '/products/fluid-analysis', 'external_url': 'https://www.filtertechnik.co.uk'},
        {'name': 'Contamination Monitoring Kits', 'url': '/products/fluid-analysis', 'external_url': 'https://www.filtertechnik.co.uk'},
    ],
    'continental-industrie': [
        {'name': 'Multistage Centrifugal Blowers', 'url': '/products/vacuum-blowers/multi-stage-blowers', 'external_url': 'https://www.continental-industrie.com'},
        {'name': 'Centrifugal Exhausters', 'url': '/products/vacuum-blowers/centrifugal-blowers', 'external_url': 'https://www.continental-industrie.com'},
        {'name': 'Gas Boosters', 'url': '/products/vacuum-blowers', 'external_url': 'https://www.continental-industrie.com'},
        {'name': 'Custom-Engineered Air & Gas Systems', 'url': '/products/vacuum-blowers', 'external_url': 'https://www.continental-industrie.com'},
    ],
    'schaeffler-smt': [
        {'name': 'Bearing Mounting Tool Kits (BETEX®)', 'url': '/products/industrial-tools/bearing-mounting-dismounting-tools', 'external_url': 'https://www.schaeffler.com'},
        {'name': 'Induction Heaters for Bearing Installation', 'url': '/products/industrial-tools/induction-heaters', 'external_url': 'https://www.schaeffler.com'},
        {'name': 'Hydraulic Pullers & Mechanical Extractors', 'url': '/products/industrial-tools/hydraulic-tools-equipment', 'external_url': 'https://www.schaeffler.com'},
        {'name': 'Laser Alignment Tools', 'url': '/products/industrial-tools/alignment-tools', 'external_url': 'https://www.schaeffler.com'},
    ],
    'sotras': [
        {'name': 'Compressor Inlet Air Filters', 'url': '/products/industrial-filtration/air-filtration-systems', 'external_url': 'https://www.sotras.com'},
        {'name': 'Oil Filters & Lube Elements', 'url': '/products/industrial-filtration', 'external_url': 'https://www.sotras.com'},
        {'name': 'Air/Oil Separator Elements', 'url': '/products/industrial-filtration', 'external_url': 'https://www.sotras.com'},
        {'name': 'Vacuum Pump Filtration', 'url': '/products/industrial-filtration/vacuum-compressor-filters', 'external_url': 'https://www.sotras.com'},
    ],
    'sdt-systems': [
        {'name': 'SDT340 Portable Ultrasound Data Collector', 'url': '/services/condition-monitoring', 'external_url': 'https://www.sdtultrasound.com'},
        {'name': 'LUBExpert Acoustic Lubrication Monitor', 'url': '/services/condition-monitoring', 'external_url': 'https://www.sdtultrasound.com'},
        {'name': 'Ultrasound "Checker" Entry-Level Tools', 'url': '/services/condition-monitoring', 'external_url': 'https://www.sdtultrasound.com'},
        {'name': 'Online Ultrasound Monitoring Systems', 'url': '/services/condition-monitoring', 'external_url': 'https://www.sdtultrasound.com'},
    ],
    'prevost': [
        {'name': 'prevoS1 Quick-Safety Couplings & Plugs', 'url': '/products/control-automation', 'external_url': 'https://www.prevost.fr'},
        {'name': 'Industrial Blow Guns (prevoS1 & 27202 Series)', 'url': '/products/control-automation', 'external_url': 'https://www.prevost.fr'},
        {'name': 'Compressed Air Distribution Fittings', 'url': '/products/control-automation', 'external_url': 'https://www.prevost.fr'},
        {'name': 'Ring Main Piping Components', 'url': '/products/control-automation', 'external_url': 'https://www.prevost.fr'},
    ],
    'spectro-scientific': [
        {'name': 'FluidScan Portable IR Oil Analyzer', 'url': '/products/fluid-analysis', 'external_url': 'https://www.spectrosci.com'},
        {'name': 'MiniLab On-Site Fluid Analysis System', 'url': '/products/fluid-analysis', 'external_url': 'https://www.spectrosci.com'},
        {'name': 'SpectroTrack Fleet Management Software', 'url': '/products/fluid-analysis', 'external_url': 'https://www.spectrosci.com'},
        {'name': 'Wear Debris Analysis Instruments', 'url': '/products/fluid-analysis', 'external_url': 'https://www.spectrosci.com'},
    ],
    'iriss': [
        {'name': 'VP Series Infrared Inspection Windows', 'url': '/services/condition-monitoring', 'external_url': 'https://www.iriss.com'},
        {'name': 'CAP Series Large-Format IR Windows', 'url': '/services/condition-monitoring', 'external_url': 'https://www.iriss.com'},
        {'name': 'Flex IR Series Custom Configurations', 'url': '/services/condition-monitoring', 'external_url': 'https://www.iriss.com'},
        {'name': 'Ultrasound & Partial Discharge Solutions', 'url': '/services/condition-monitoring', 'external_url': 'https://www.iriss.com'},
    ],
    'luneta': [
        {'name': 'Bullseye Level & Condition Sight Glasses', 'url': '/products/lubrication-oil', 'external_url': 'https://www.lunetainc.com'},
        {'name': 'Bearing Oil Sight Glass Systems', 'url': '/products/lubrication-oil', 'external_url': 'https://www.lunetainc.com'},
        {'name': 'Oil Drain & Fill Systems', 'url': '/products/lubrication-oil', 'external_url': 'https://www.lunetainc.com'},
        {'name': 'Visual Contamination Indicator Systems', 'url': '/products/lubrication-oil', 'external_url': 'https://www.lunetainc.com'},
    ],
    'noria-corporation': [
        {'name': 'MLT I — Machinery Lubrication Technician Level I', 'url': '/services/training-primegear', 'external_url': 'https://www.noria.com'},
        {'name': 'MLT II — Machinery Lubrication Technician Level II', 'url': '/services/training-primegear', 'external_url': 'https://www.noria.com'},
        {'name': 'MLA I — Machinery Lubrication Analyst Level I', 'url': '/services/training-primegear', 'external_url': 'https://www.noria.com'},
        {'name': 'MLA II — Machinery Lubrication Analyst Level II', 'url': '/services/training-primegear', 'external_url': 'https://www.noria.com'},
    ],
    'mobius-institute': [
        {'name': 'Vibration Analysis CAT I — Foundation Level', 'url': '/services/training-primegear', 'external_url': 'https://www.mobiusinstitute.com'},
        {'name': 'Vibration Analysis CAT II — Practitioner', 'url': '/services/training-primegear', 'external_url': 'https://www.mobiusinstitute.com'},
        {'name': 'Vibration Analysis CAT III — Specialist', 'url': '/services/training-primegear', 'external_url': 'https://www.mobiusinstitute.com'},
        {'name': 'Vibration Analysis CAT IV — Expert', 'url': '/services/training-primegear', 'external_url': 'https://www.mobiusinstitute.com'},
    ],
    'harvard-corporation': [
        {'name': 'Lubrication Management Systems & Equipment', 'url': '/products/lubrication-oil', 'external_url': 'https://www.harvardcorporation.com'},
        {'name': 'Oil Storage & Transfer Solutions', 'url': '/products/lubrication-oil', 'external_url': 'https://www.harvardcorporation.com'},
        {'name': 'Filtration & Contamination Control Products', 'url': '/products/industrial-filtration', 'external_url': 'https://www.harvardcorporation.com'},
        {'name': 'Condition Monitoring Accessories & Supplies', 'url': '/services/condition-monitoring', 'external_url': 'https://www.harvardcorporation.com'},
    ],
    'rmf-systems': [
        {'name': 'Offline Filtration Systems', 'url': '/products/industrial-filtration', 'external_url': None},
        {'name': 'Oil Storage & Transfer Solutions', 'url': '/products/lubrication-oil', 'external_url': None},
        {'name': 'Contamination Monitoring Systems', 'url': '/products/lubrication-oil/contamination-control-solutions', 'external_url': None},
        {'name': 'Fluid Management & Clean Oil Systems', 'url': '/products/lubrication-oil', 'external_url': None},
    ],
    'stiavelli-irio': [
        {'name': 'Centrifugal Fans', 'url': '/products/vacuum-blowers/centrifugal-blowers', 'external_url': None},
        {'name': 'Axial Fans', 'url': '/products/vacuum-blowers/axial-fans', 'external_url': None},
        {'name': 'High-Temperature & ATEX Fans', 'url': '/products/vacuum-blowers', 'external_url': None},
        {'name': 'Heavy-Duty Industrial Blowers', 'url': '/products/vacuum-blowers/multi-stage-blowers', 'external_url': None},
    ],
    'itc': [
        {'name': 'Infrared Thermography Training (Level I–III)', 'url': '/services/training-primegear', 'external_url': None},
        {'name': 'Thermal Inspection & Diagnostics Training', 'url': '/services/training-primegear', 'external_url': None},
        {'name': 'Certification Programs', 'url': '/services/training-primegear', 'external_url': None},
        {'name': 'On-Site & Customized Training Solutions', 'url': '/services/training-primegear', 'external_url': None},
    ],
    'atmos': [
        {'name': 'Portable Air Compressors', 'url': '/products/air-compressors/portable-air-compressors', 'external_url': None},
        {'name': 'Diesel-Driven Compressors', 'url': '/products/air-compressors/portable-air-compressors', 'external_url': None},
        {'name': 'Construction & Drilling Air Systems', 'url': '/products/air-compressors/portable-air-compressors', 'external_url': None},
        {'name': 'Compact & Mobile Air Solutions', 'url': '/products/air-compressors/portable-air-compressors', 'external_url': None},
    ],
    'bega-special-tools': [
        {'name': 'Induction Heaters', 'url': '/products/industrial-tools', 'external_url': None},
        {'name': 'Bearing Handling Tools', 'url': '/products/industrial-tools', 'external_url': None},
        {'name': 'Precision Maintenance Tools', 'url': '/products/industrial-tools', 'external_url': None},
        {'name': 'Coupling & Alignment Tools', 'url': '/products/industrial-tools', 'external_url': None},
    ],
}


class AtlascoPartnerProduct(models.Model):
    """Per-partner "Product Range" tile on a partner subpage (/partners/<slug>).

    Migrated out of the hardcoded 'product_range' lists in the partners_data
    dict in controllers/main.py so admins can add/remove/reorder products and
    edit their name, link, and brand-site URL from the backend.
    """
    _name = 'atlasco.partner.product'
    _description = 'Atlasco Partner — Product Range Item'
    _order = 'partner_slug, sequence, id'

    partner_slug = fields.Char(
        'Partner', required=True, index=True,
        help="Partner page slug this product belongs to, e.g. 'compair' (from /partners/compair).")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)
    name = fields.Char('Product Name', required=True, translate=True)
    url = fields.Char('Internal Product URL', help="Relative link into the Products section, e.g. /products/air-compressors.")
    external_url = fields.Char('Brand Site URL', help="Optional external manufacturer link shown as an 'Brand Site' badge.")
    image = fields.Image('Image')

    @staticmethod
    def _normalize_internal_url(value):
        """Guarantee the site-relative leading slash on 'url'.

        ClickUp 869emevtx: "Adding a new item to the Product Range is not
        working for internal product URLs." Root cause — 'url' is a plain
        Char field (no link-picker widget, no validation), and its own help
        text example ("/products/air-compressors") only *shows* the leading
        slash by convention; nothing enforced it. Type/paste the path without
        that leading slash (e.g. 'products/air-compressors/oil-screw-
        compressors', an easy mistake with no on-save error) and the tile's
        <a t-att-href="prod.get('url')"> in partner_detail.xml renders that
        exact string as the href. A leading-slash-less href is *relative to
        the current page path*, not site-root, so the browser resolves it to
        /partners/<slug>/products/... instead of /products/... — a silent
        404 with zero feedback anywhere in the editor. 'external_url' never
        hits this because a real external link always carries an explicit
        scheme (https://...), which is absolute by definition — that is
        exactly why the bug is specific to internal URLs and never shows up
        for external ones.

        Trims whitespace (a copy-paste trailing space is invisible in a
        plain text input and produces the same kind of broken-but-silent
        href) and, for any non-empty value that isn't already absolute
        (leading '/') or a full URL (contains '://'), prepends '/'.
        """
        if not value:
            return value
        value = value.strip()
        if not value:
            return value
        if value.startswith('/') or '://' in value:
            return value
        return '/' + value

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if 'url' in vals:
                vals['url'] = self._normalize_internal_url(vals['url'])
        return super().create(vals_list)

    def write(self, vals):
        if 'url' in vals:
            vals = dict(vals, url=self._normalize_internal_url(vals['url']))
        return super().write(vals)

    @api.model
    def _seed_from_controller(self):
        """Idempotently seed products from the hardcoded controller data.

        Only seeds a slug that has NO products yet, so manual edits are never
        clobbered on a later module upgrade. Safe to run repeatedly.
        """
        for slug, items in _SEED_PARTNER_PRODUCTS.items():
            if self.search_count([('partner_slug', '=', slug)]):
                continue
            seq = 10
            for it in items:
                self.create({
                    'partner_slug': slug,
                    'sequence': seq,
                    'name': it.get('name'),
                    'url': it.get('url'),
                    'external_url': it.get('external_url'),
                })
                seq += 10
        return True

    @api.model
    def _backfill_images_from_catalog(self):
        """ClickUp 869emevtx follow-up: map the backend `image` field to
        whatever's actually rendering on the live page today, so the backend
        list/form stops showing empty for rows that visitors already see a
        photo for (that photo just lives in the catalog-fallback lookup, not
        on the record — see the same-numbered comment in
        controllers/main.py's `partner` route).

        Only touches rows where `image` is empty, so a real upload (backend
        or the Website Editor) is never overwritten by this — safe to run on
        every module upgrade, and a no-op for anything already populated
        manually. Rows whose fallback also resolves to nothing (verified
        2026-09-12: 5 of 94 site-wide, all in categories with no supplied
        client photo at all, e.g. industrial-filtration) are left empty —
        there is no image anywhere to map from.
        """
        import base64
        from odoo.modules.module import get_module_resource
        # Lazy import: controllers/main.py builds these lookups from the
        # same PRODUCT_CATEGORIES data at module-load time; importing here
        # (call-time, not module top) avoids a load-order/circular-import
        # dependency between models and controllers.
        from odoo.addons.atlasco_website.controllers.main import (
            _product_catalog_image, _service_catalog_image,
        )
        rows = self.search([('image', '=', False), ('url', '!=', False)])
        for row in rows:
            rel_url = _product_catalog_image(row.url) or _service_catalog_image(row.url, env=self.env)
            if not rel_url or not rel_url.startswith('/atlasco_website/'):
                continue
            resource_path = rel_url[len('/atlasco_website/'):]
            fs_path = get_module_resource('atlasco_website', *resource_path.split('/'))
            if not fs_path:
                continue
            try:
                with open(fs_path, 'rb') as f:
                    row.image = base64.b64encode(f.read())
            except OSError:
                continue
        return True
