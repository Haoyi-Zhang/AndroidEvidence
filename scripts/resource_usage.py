"""Optional OS resource measurements; unavailable values are never zero-filled."""
import sys
try:
    import resource
except ImportError:  # Windows has no standard-library getrusage.
    resource = None


def usage(children=False):
    if resource is None:
        return {'cpu_seconds': None, 'peak_rss_kib': None,
                'basis': 'getrusage unavailable on this platform'}
    r = resource.getrusage(resource.RUSAGE_CHILDREN if children else resource.RUSAGE_SELF)
    rss = r.ru_maxrss / 1024 if sys.platform == 'darwin' else r.ru_maxrss
    return {'cpu_seconds': r.ru_utime + r.ru_stime, 'peak_rss_kib': rss,
            'basis': 'RUSAGE_CHILDREN running maximum' if children else 'RUSAGE_SELF'}
