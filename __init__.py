from . import models
from . import controllers


def post_init_hook(env):
    """BUG-10 (ClickUp 869f03ux1): the header 'En / Ar' language switcher was
    pure static markup with no language behind it - Arabic was never actually
    activated as an Odoo language, so the control was a dead click.

    This activates Arabic (ar_001) as a real installed language and adds it
    to every website's language_ids, so the switcher can do genuine locale/
    URL switching (via website's native multi-language routing) instead of
    doing nothing. It intentionally leaves the default language as English
    and does NOT attempt to translate any content - see
    views/atlasco_layout.xml for the switcher wiring, and the ClickUp comment
    on 869f03ux1 for the full scope note.
    """
    lang_code = 'ar_001'
    Lang = env['res.lang']
    lang = Lang._activate_lang(lang_code)
    if not lang:
        lang = Lang.with_context(active_test=False).search([('code', '=', lang_code)], limit=1)
    if not lang:
        return
    websites = env['website'].search([])
    for website in websites:
        if lang.id not in website.language_ids.ids:
            website.language_ids = [(4, lang.id)]

    # Recruitment integration ticket: hr/hr_recruitment's own demo hr.job
    # records install already published. Their demo data loads in Odoo's
    # separate, later "demo" pass (after every module's "data" files), so
    # this can't be a <function> call in a data file - it has to run here,
    # after the full load (data + demo) has completed.
    env['hr.job']._unpublish_demo_positions()
