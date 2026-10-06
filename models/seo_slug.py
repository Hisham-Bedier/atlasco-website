# -*- coding: utf-8 -*-
"""SEO-slug convention, enforced in one place.

Client requirement (2026-09-11 meeting, ClickUp 869f0826p): every new page's
URL path must follow the same lowercase-hyphenated convention already used
across this site (e.g. /partners/compair, /industries/oil-gas/gas-generation)
— never mixed case, spaces, underscores, or a leading/trailing/double hyphen.

This is a naming-convention guardrail, not a URL-routing framework: it only
validates the `slug` field on the two models whose slug actually becomes a
public page path (atlasco.partner -> /partners/<slug>, and
atlasco.industry.product -> /industries/<industry>/<slug>). Models that just
reference an existing page's slug as a foreign key (e.g. industry_slug on
atlasco.reliability.card, partner_slug on atlasco.partner.product) don't
create a page path themselves and are intentionally left alone.

Any new model that introduces its own page-path slug field should call
`validate_seo_slug(value)` from an `@api.constrains` on that field the same
way the two models below do — see atlasco_partner.py / industry_product.py.
"""
import re

from odoo.exceptions import ValidationError

# lowercase letters/digits, hyphen-separated, no leading/trailing/double
# hyphen: "oil-gas", "compair", "gas-generation-2" all pass; "Oil_Gas",
# "-steel", "steel-", "steel--pipe" all fail.
SEO_SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def validate_seo_slug(slug):
    """Raise ValidationError if `slug` isn't lowercase-hyphenated.

    Returns None (nothing to do) for a falsy slug — required=True on the
    field already handles the empty case with its own message.
    """
    if slug and not SEO_SLUG_RE.match(slug):
        raise ValidationError(
            "URL slug %r is not allowed. Page paths must be lowercase and "
            "hyphen-separated (letters, numbers, single hyphens only) — "
            "e.g. 'oil-gas', 'compair', 'gas-generation-2'. No spaces, "
            "capitals, underscores, or leading/trailing/double hyphens." % slug
        )
