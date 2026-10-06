# Atlasco Egypt Website

Custom Odoo website module for Atlasco Egypt. Implements the full corporate
website (homepage, industries, services, business arms, partners, products,
about/team/history, careers, and contact) as a single installable Odoo module.

- **Module name:** `atlasco_website`
- **Manifest version:** 17.0.1.0.0
- **Odoo version:** 17.0
- **Depends on:** `website`, `web`, `crm`, `hr_recruitment`, `website_hr_recruitment`
- **License:** LGPL-3

## Repository layout

```
atlasco_website/
├── __manifest__.py        # module manifest (data files, assets, deps)
├── controllers/           # HTTP controllers (contact form, etc.)
├── models/                # backend models
├── views/                 # QWeb page templates (one file per page/section)
├── data/                  # seed data loaded on install
├── security/              # access rights
├── migrations/            # version-upgrade scripts
└── static/src/            # frontend CSS/JS
```

## Deploying

1. Place the module in your Odoo addons path, e.g.:
   ```
   /opt/odoo17/custom_addons/atlasco_website
   ```
2. Ensure the addons directory is listed in the Odoo config (`addons_path`).
3. Install or update the module:
   ```
   ./odoo-bin -c /etc/odoo.conf -d <database> -i atlasco_website --stop-after-init
   # or, to apply changes to an already-installed module:
   ./odoo-bin -c /etc/odoo.conf -d <database> -u atlasco_website --stop-after-init
   ```
4. Restart the Odoo service so the changes are served:
   ```
   systemctl restart <odoo-service>
   ```

After installation the website pages are available under the site root via the
standard Odoo `website` routing.
