from odoo import api, fields, models


class Website(models.Model):
    _inherit = 'website'

    # Root cause of "new pages don't get the Atlasco theme" (see
    # views/atlasco_page_template.xml for the full writeup of how this was
    # diagnosed): core Odoo's new_page() builds a brand new page by copying
    # the RAW arch_db of a base template - by default 'website.default_page'
    # - via `self.env.ref(template).arch`. That `arch` field is each view's
    # own stored XML only; it does NOT include xpath/inherit_id overrides
    # (those only apply when a template is actually rendered via t-call, not
    # when its raw arch is read like this). So an inherit_id view aimed at
    # website.default_page - which was the first fix attempted here and
    # looked correct - can never change what new_page() actually copies.
    #
    # This applies to every page created through the "+New" dialog, blank or
    # from a "Custom" gallery template: get_new_page_templates() only ever
    # extracts the #wrap content from a source page and the client posts
    # that back as `sections_arch` - it never tells new_page() to use a
    # different base template. So `template` is always left at its default,
    # 'website.default_page', regardless of which starter card the user
    # picked.
    #
    # The only way to make new pages pick up the Atlasco chrome is to swap
    # which base template new_page() actually copies from, so intercept
    # calls that would use the stock default and redirect them to our own
    # copy (default_page_atlasco, in atlasco_page_template.xml) which is
    # identical except it calls atlasco_website.atlasco_layout instead of
    # website.layout.
    @api.model
    def new_page(self, name=False, add_menu=False, template='website.default_page',
                 ispage=True, namespace=None, page_values=None, menu_values=None,
                 sections_arch=None):
        if template == 'website.default_page':
            template = 'atlasco_website.default_page_atlasco'
        # add_menu=True creates a real website.menu entry that
        # views/atlasco_layout.xml's navbar reads directly (see WebsiteMenu
        # below) — no extra sync step needed, unlike the old atlasco.nav.item
        # model this replaced.
        return super().new_page(
            name=name, add_menu=add_menu, template=template, ispage=ispage,
            namespace=namespace, page_values=page_values, menu_values=menu_values,
            sections_arch=sections_arch,
        )


# Migrated off the old custom atlasco.nav.item model: the client's native
# "Edit Menu" dialog (Website > Site > Menu Editor) only ever manages
# website.menu, and atlasco.nav.item was a second, disconnected list that
# dialog never touched — renaming/relinking a navbar item from the backend
# silently did nothing on the live site. website.menu already gives free
# add/remove/reorder/nest through that same native dialog; the two fields
# below are the only things atlasco.nav.item had that website.menu doesn't:
# which mega-menu sidemenu panel a top-nav item opens, and a per-item font
# size override.
class WebsiteMenu(models.Model):
    _inherit = 'website.menu'

    atlasco_sm_target = fields.Char(
        'Mega-Menu Panel',
        help="Internal key of the sidemenu panel (views/atlasco_layout.xml "
             "atl-sm-panel) this top-nav item opens. Leave blank for a plain "
             "link with no dropdown.")
    atlasco_font_size = fields.Integer(
        'Font Size (px)',
        help="Size in pixels for this link only. Leave at 0 for the site default.")
    atlasco_sidemenu_label = fields.Char(
        'Sidemenu Label Override',
        help="Optional. The original design used a shorter top-navbar label "
             "and a fuller burger-menu label for the same link (e.g. "
             "\"About\" up top vs \"About Atlasco\" in the sidemenu). Set "
             "this to restore that; leave blank to show the same Label "
             "everywhere.")

    @api.model
    def _migrate_atlasco_nav_items(self):
        """One-time migration from the retired atlasco.nav.item model.

        Idempotent by url: only creates a menu entry for a url that isn't
        already a child of the website's root menu, so re-running this on
        upgrade never duplicates entries a client has since added/edited
        themselves. Confirmed via direct read of both the local sandbox and
        the real staging DB before writing this that every atlasco.nav.item
        row still held its original seed value (about/industries/products/
        services/partners/careers/contact) — so hardcoding those same 7
        values here IS the migration, not a guess.
        """
        website = self.env['website'].get_current_website()
        root = website.menu_id

        # The stock 2-item starter menu every fresh website install ships
        # with (confirmed via the client's own "Edit Menu" screenshot: just
        # "Home" and "Contact us", nothing else, never touched). Once the
        # header starts reading this tree it would otherwise leak both a
        # redundant plain "Home" link and a dead "/contactus" link (that
        # route doesn't exist here — /contact does) into the real nav.
        stock_defaults = {('Home', '/'), ('Contact us', '/contactus')}
        for menu in root.child_id:
            if (menu.name, menu.url) in stock_defaults:
                menu.unlink()

        existing_urls = set(root.child_id.mapped('url'))
        seed = [
            ('About', '/about', 'about', 10),
            ('Industries', '/industries', 'industries', 20),
            ('Products', '/products', 'products', 30),
            ('Services', '/services', 'services', 40),
            ('Partners', '/partners', False, 50),
            ('Careers & Culture', '/careers', 'careers', 60),
            ('Contact Us', '/contact', False, 70),
        ]
        for name, url, sm_target, sequence in seed:
            if url in existing_urls:
                continue
            self.create({
                'name': name,
                'url': url,
                'sequence': sequence,
                'parent_id': root.id,
                'website_id': website.id,
                'atlasco_sm_target': sm_target,
            })

    @api.model
    def _get_top_nav_action(self):
        """List-view action scoped to exactly the 7 top-nav items.

        A plain domain on the action record can't reach this - the same
        (name, url) values are duplicated elsewhere in website.menu (e.g. a
        "Contact us"/"/contactus" stock leftover, "Company Overview"/"/about"
        in the sidemenu, 10 product-category sidemenu items that all also
        point at /products) and, in a DB with more than one website
        configured, a second site's own top menu can carry the exact same
        urls again under a different parent. The one thing that reliably
        picks out just these 7 is being a direct child of the CURRENT
        website's own root menu (website.menu_id, resolved fresh here rather
        than hardcoded, exactly like _migrate_atlasco_nav_items above) -
        so resolve that dynamically via a server action instead of a static
        act_window domain.
        """
        website = self.env['website'].get_current_website()
        action = self.env['ir.actions.act_window']._for_xml_id('atlasco_website.action_atlasco_nav_menu')
        action['domain'] = [('parent_id', '=', website.menu_id.id)]
        return action

    # L2/L3 seed data for _migrate_atlasco_sidemenu below — copied verbatim
    # from the hand-authored sidemenu panels in views/atlasco_layout.xml
    # (the ones this migration replaces). Products' 10 categories are
    # themselves (name, sm_target, [L3 leaf items]) tuples since each opens
    # its own L3 panel; every other L1 section is a flat leaf list.
    _SIDEMENU_L2 = {
        'about': [
            ('Company Overview', '/about'),
            ('Our History', '/about/history'),
            ('Our Team', '/about/team'),
        ],
        'industries': [
            ('Oil & Gas', '/industries/oil-gas'),
            ('Steel', '/industries/steel'),
            ('Pharmaceutical', '/industries/pharmaceutical'),
            ('Medical', '/industries/medical'),
            ('Food & Beverage', '/industries/food-beverage'),
            ('Textile', '/industries/textile'),
            ('Electronics', '/industries/electronics'),
            ('Cement', '/industries/cement'),
            ('Construction', '/industries/construction'),
        ],
        'services': [
            ('Machine Condition Monitoring', '/services/condition-monitoring'),
            ('After-Sales Support', '/services/after-sales-support'),
            ('Oil Analysis & Filtration', '/services/oil-analysis-filtration'),
            ('Piping & Installation', '/services/piping-installation'),
            ('Consultation Services', '/services/consultation-audits'),
            ('Rental Services', '/services/rental'),
            ('Training (PrimeGear)', '/primegear'),
        ],
        'careers': [
            ('Careers', '/careers'),
            ('Culture', '/culture'),
        ],
    }

    # Products' 10 L2 category items (name, sm_target). Each one's chevron
    # opens an L3 panel of specific product types — but website.menu hard-
    # caps at 2 levels of hierarchy ("Menus cannot have more than two levels
    # of hierarchy", a real Odoo core constraint, confirmed by hitting it
    # directly while building this), so that 3rd level can't move into
    # website.menu at all. It stays exactly as before: hardcoded L3 panels
    # in views/atlasco_layout.xml, opened via the same sm_target string
    # these L2 records carry — only L1 and L2 are native/backend-editable
    # now, L3 remains a code change like it always was.
    _SIDEMENU_PRODUCTS_L2 = [
        ('Air Compressors', 'air-compressors'),
        ('Gas Generation', 'gas-generation'),
        ('Air Treatment', 'air-treatment'),
        ('Vacuum & Blowers', 'vacuum-blowers'),
        ('Industrial Filtration', 'industrial-filtration'),
        ('Lubrication & Oil Systems', 'lubrication-oil'),
        ('Air & Gas Storage', 'gas-storage'),
        ('Fluid Analysis', 'fluid-analysis'),
        ('Control & Automation', 'control-automation'),
        ('Industrial Tools', 'industrial-tools'),
    ]

    @api.model
    def _migrate_atlasco_sidemenu(self):
        """Migrate the hand-authored L2 sidemenu panels (About/Industries/
        Products/Services/Careers submenus) into website.menu children, so
        the burger-menu drill-down is finally driven by the same tree the
        native Menu Editor manages — same gap as the top nav this replaces,
        one level deeper. Products' L3 (specific product types under each
        of its 10 categories) stays hardcoded — see _SIDEMENU_PRODUCTS_L2
        above for why.

        Idempotent by (parent, name): every sibling group in the source
        data has unique names (unlike url — Products' 10 L2 category items
        all share the literal href "/products", so url can't be used as
        the dedupe key there), so matching within each parent's own
        child_id is what's actually safe to re-run on every upgrade.
        """
        website = self.env['website'].get_current_website()
        root = website.menu_id
        l1_by_target = {m.atlasco_sm_target: m for m in root.child_id if m.atlasco_sm_target}

        def _add_children(parent, items):
            existing_names = set(parent.child_id.mapped('name'))
            seq = 10
            for entry in items:
                name, url = entry[0], (entry[1] if len(entry) == 2 else '/products')
                if name not in existing_names:
                    vals = {
                        'name': name,
                        'url': url,
                        'sequence': seq,
                        'parent_id': parent.id,
                        'website_id': website.id,
                    }
                    if len(entry) == 3:
                        vals['atlasco_sm_target'] = entry[2]
                    self.create(vals)
                seq += 10

        for l1_key, items in self._SIDEMENU_L2.items():
            l1 = l1_by_target.get(l1_key)
            if l1:
                _add_children(l1, items)

        products_l1 = l1_by_target.get('products')
        if products_l1:
            _add_children(products_l1, [(n, '/products', t) for n, t in self._SIDEMENU_PRODUCTS_L2])

        # The original design used a fuller label in the sidemenu than in
        # the cramped top navbar for 2 of the 7 sections ("About" up top /
        # "About Atlasco" in the burger menu; "Industries" / "Industries We
        # Serve") — everything else used the same text in both places. Set
        # the override only where it actually differed, so the sidemenu
        # keeps showing what it always did instead of collapsing to the
        # shorter top-nav text now that both surfaces share one record.
        sidemenu_overrides = {'about': 'About Atlasco', 'industries': 'Industries We Serve'}
        for sm_key, fuller_label in sidemenu_overrides.items():
            l1 = l1_by_target.get(sm_key)
            if l1 and not l1.atlasco_sidemenu_label:
                l1.atlasco_sidemenu_label = fuller_label
