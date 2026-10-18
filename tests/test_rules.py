import unittest
from datetime import date, timedelta
from rules import needs_renewal

class RenewalTests(unittest.TestCase):
    def test_60_days_included(self):
        today=date(2026,10,15)
        self.assertTrue(needs_renewal((today+timedelta(days=60)).isoformat(),today))
    def test_61_days_excluded(self):
        today=date(2026,10,15)
        self.assertFalse(needs_renewal((today+timedelta(days=61)).isoformat(),today))
    def test_missing_never_warned(self):
        self.assertFalse(needs_renewal(None,date(2026,10,15)))
    def test_expired_not_upcoming(self):
        self.assertFalse(needs_renewal('2026-10-14',date(2026,10,15)))

if __name__=='__main__': unittest.main()
