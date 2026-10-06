from odoo import api, models


class HrJob(models.Model):
    _inherit = 'hr.job'

    @api.model
    def _unpublish_demo_positions(self):
        """hr/hr_recruitment ship demo hr.job records (e.g. "Chief Technical
        Officer", "Experienced Developer") that install already published on
        this database. Left alone they'd show up next to Atlasco's real
        postings on the public /careers page and in the backend Recruitment
        app. Unpublish (not delete) them - same "deactivate, don't destroy"
        approach already used for the old atlasco.career.opening records -
        so they stay as harmless sample data for whoever explores the
        Recruitment app, but never reach the live site. Scoped by module
        ('hr'/'hr_recruitment') rather than by name, so it doesn't depend on
        which demo records this particular database happened to load.
        """
        demo_data = self.env['ir.model.data'].sudo().search([
            ('model', '=', 'hr.job'),
            ('module', 'in', ('hr', 'hr_recruitment')),
        ])
        demo_jobs = self.sudo().browse(demo_data.mapped('res_id')).exists()
        demo_jobs.filtered('website_published').write({'website_published': False})
