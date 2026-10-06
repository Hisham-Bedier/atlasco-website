import base64
import logging

from odoo.modules.module import get_module_resource

_logger = logging.getLogger(__name__)


def backfill_images_from_static(env, module, xmlid_to_relpath, field='image'):
    """Idempotently copy bundled static files into a real binary/Image field.

    For each ``xmlid -> relative static path`` pair: if the record referenced
    by the xmlid exists and its ``field`` is still empty, read the bytes of
    the module's bundled static file and write them in as the field's value.

    Records that already have a value in ``field`` are left untouched, so a
    manual re-upload made after this fix ships is never clobbered by a later
    module upgrade. Safe to call on every upgrade.

    Returns the number of records actually filled in (for logging/testing).
    """
    filled = 0
    for xmlid, relpath in xmlid_to_relpath.items():
        rec = env.ref('%s.%s' % (module, xmlid), raise_if_not_found=False)
        if not rec or rec[field]:
            continue
        path = get_module_resource(module, *relpath.split('/'))
        if not path:
            _logger.warning(
                "atlasco_website: static file not found for %s.%s (%s); "
                "skipping image backfill for this record.",
                module, xmlid, relpath)
            continue
        with open(path, 'rb') as f:
            rec[field] = base64.b64encode(f.read())
        filled += 1
    return filled
