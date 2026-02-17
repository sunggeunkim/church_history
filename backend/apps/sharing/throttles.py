"""Throttle classes for social sharing."""

from rest_framework.throttling import ScopedRateThrottle


class SharingRateThrottle(ScopedRateThrottle):
    scope = "sharing"


class SharingBurstThrottle(ScopedRateThrottle):
    scope = "sharing_burst"
