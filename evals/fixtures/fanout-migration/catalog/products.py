"""Product records for the storefront catalog."""

from catalog.dates import parse_when


class ProductError(ValueError):
    """Raised when raw product fields cannot be turned into a Product."""


class Product(object):
    def __init__(self, sku, title, added_at, discontinued_at=None):
        self.sku = sku
        self.title = title
        self.added_at = added_at
        self.discontinued_at = discontinued_at

    def is_active(self, at):
        """Whether the product is sellable at the given datetime."""
        if at < self.added_at:
            return False
        if self.discontinued_at is not None and at >= self.discontinued_at:
            return False
        return True


def load_product(fields):
    """Build a Product from a raw field mapping (one feed row).

    ``added_at`` is required. ``discontinued_at`` is optional — an empty or
    missing value means the product is still active.
    """
    sku = (fields.get("sku") or "").strip()
    if not sku:
        raise ProductError("sku is required")

    added_at = parse_when(fields.get("added_at"))
    if added_at is None:
        raise ProductError("product %s: unreadable added_at" % sku)

    discontinued_at = parse_when(fields.get("discontinued_at"))

    return Product(sku, fields.get("title", ""), added_at, discontinued_at)
