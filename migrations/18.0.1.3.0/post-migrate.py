# -*- coding: utf-8 -*-
"""UI-01: fix the "From Percision to Performance" typo on homepage content.

The homepage industries section label ('atlasco.content'.home_industries_label)
was created with a misspelled Python `default=` ("Percision" instead of
"Precision"). The field default only applies at record-creation time, so any
`atlasco.content` row created before this fix keeps the typo permanently even
after the model default is corrected. This migration finds and corrects any
row still holding the old value.
"""

TYPO = 'From Percision to Performance'
FIXED = 'From Precision to Performance'


def migrate(cr, version):
    cr.execute(
        "UPDATE atlasco_content SET home_industries_label = %s "
        "WHERE home_industries_label = %s",
        (FIXED, TYPO),
    )
