import unittest
import datetime
from addBirthday import get_date

class Test(unittest.TestCase):
    # @unittest.mock.patch("datetime.datetime.now().year", new=2000)
    def test_get_date(self):
        # Test abbreviated format
        valid_date_strs = ["Jan 20", "jan 20", "jAn 20"]
        year = datetime.datetime.now().year
        expected_date = datetime.datetime(year, 1, 20)
        for date in valid_date_strs:
            print(expected_date)
            self.assertEqual(get_date(date), expected_date)
        
        invalid_date_strs = ["Jane 20", "jane 20", "jAne 20", "Jan"]
        for date in invalid_date_strs:
            self.assertIsNone(get_date(date))
            
        # Test full month format 
        valid_date_strs = ["January 20", "january 20", "jAnuary 20"]
        year = datetime.datetime.now().year
        expected_date = datetime.datetime(year, 1, 20)
        for date in valid_date_strs:
            print(expected_date)
            self.assertEqual(get_date(date), expected_date)
        
        invalid_date_strs = ["Januar 20", "januar 20", "jAnuar 20", "January"]
        for date in invalid_date_strs:
            self.assertIsNone(get_date(date))
        
        # Test month/day format
        valid_date_strs = ["01/20", "1/20"]
        year = datetime.datetime.now().year
        expected_date = datetime.datetime(year, 1, 20)
        for date in valid_date_strs:
            print(expected_date)
            print(get_date(date))
            self.assertEqual(get_date(date), expected_date)

        invalid_date_strs = ["/01/20", "01/$20"]
        for date in invalid_date_strs:
            self.assertIsNone(get_date(date))
        
        # Test invalid date (month too big or doesn't exist, day too big or doesn't exist)
        date_strs = ["abc 20", "March 32", "dec 32"]
        for date in date_strs:
            self.assertIsNone(get_date(date))

        # Test empty string
        date_strs = [""]
        for date in date_strs:
            self.assertIsNone(get_date(date))


if __name__ == "__main__":
    unittest.main()