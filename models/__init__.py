from . import seo_slug
from . import atlasco_content
# ClickUp 869f081z9 — "Add new Partner (logo + link + details page) not
# possible from backend". Primary root cause: this file (introduced in
# db1e5c9, "Add atlasco_website Odoo module") never imported
# atlasco_partner.py at all, even though that file, its backend views
# (views/atlasco_partner_views.xml), and its menu under Website > Content >
# Partners have existed on this branch the whole time. An un-imported model
# file is never registered with Odoo, so opening that backend menu didn't
# show an incomplete form — it hard-errored ("Object atlasco.partner
# doesn't exist"). Confirmed via a real install + XML-RPC round trip on a
# fresh local Odoo 17 DB before this line was added.
from . import atlasco_partner
from . import content_home
from . import content_about
from . import content_team
from . import content_history
from . import content_careers
from . import reliability_card
from . import industry_product
from . import partner_product
from . import content_media
from . import atlasco_block_style
from . import page_hero
from . import home_slide
from . import atlasco_service
from . import hr_job_seed
from . import website
