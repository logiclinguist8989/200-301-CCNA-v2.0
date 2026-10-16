"""Figure registry: chapter modules register figure builders with @figure."""

FIGURES = {}


def figure(number, slug):
    """Register a builder that returns a svgkit.Canvas for figure `number`."""
    def deco(fn):
        FIGURES[number] = (slug, fn)
        return fn
    return deco


def sort_key(number):
    ch, n = number.split(".")
    return int(ch), int(n)


def filename(number, slug):
    ch, n = number.split(".")
    return f"ch{int(ch):02d}/fig-{int(ch):02d}-{int(n):02d}-{slug}.svg"
