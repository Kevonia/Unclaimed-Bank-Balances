import unittest

from lib.utils.helper import search_jamaican_banks

class TestJamaicanBanksSearch(unittest.TestCase):
    
    def setUp(self):
        """Set up the test environment"""
        self.banks = {
            'NCB': 'National Commercial Bank Jamaica Limited',
            'BNSJ': 'The Bank of Nova Scotia Jamaica Limited',
            'JN': 'JN Bank Limited',
            'Sagicor Bank': 'Sagicor Bank Jamaica Limited',
            'CIBC': 'CIBC FirstCaribbean International Bank',
            'FGB': 'First Global Bank Limited',
            'BOJ': 'Bank of Jamaica (Central Bank)',
            'JMMB': 'JMMB Bank (Jamaica Money Market Brokers)',
            'RBTT': 'RBTT Bank Jamaica Limited (now part of Scotiabank)',
            'NSB': 'National Savings Bank'
        }

    def test_exact_bank_code_match(self):
        """Test exact bank code matching"""
        result = search_jamaican_banks('BNSJ')
        expected = {'BNSJ': self.banks['BNSJ']}
        self.assertEqual(result, expected)
        
        result = search_jamaican_banks('NCB')
        expected = {'NCB': self.banks['NCB']}
        self.assertEqual(result, expected)

    def test_bank_code_with_additional_text(self):
        """Test bank code extraction from text with additional content"""
        result = search_jamaican_banks('BNSJ Unclaimed Bank Balances')
        expected = {'BNSJ': self.banks['BNSJ']}
        self.assertEqual(result, expected)
        
        result = search_jamaican_banks('Please check NCB account status')
        expected = {'NCB': self.banks['NCB']}
        self.assertEqual(result, expected)

    def test_multiple_bank_codes_in_text(self):
        """Test when multiple bank codes appear in search text"""
        result = search_jamaican_banks('BNSJ and NCB both have good rates')
        expected = {
            'BNSJ': self.banks['BNSJ'],
            'NCB': self.banks['NCB']
        }
        self.assertEqual(result, expected)

    def test_case_insensitive_bank_code(self):
        """Test case insensitive bank code matching"""
        result = search_jamaican_banks('bnSj')
        expected = {'BNSJ': self.banks['BNSJ']}
        self.assertEqual(result, expected)
        
        result = search_jamaican_banks('ncB Unclaimed Funds')
        expected = {'NCB': self.banks['NCB']}
        self.assertEqual(result, expected)


    def test_full_bank_name_matching(self):
        """Test full bank name matching"""
        result = search_jamaican_banks('JN Bank Limited')
        expected = {'JN': self.banks['JN']}
        self.assertEqual(result, expected)

    def test_no_matches_found(self):
        """Test when no matches are found"""
        result = search_jamaican_banks('XYZ')
        self.assertEqual(result, {})
        
        result = search_jamaican_banks('Random Text Nothing Related')
        self.assertEqual(result, {})

    def test_empty_search_term(self):
        """Test empty search term"""
        result = search_jamaican_banks('')
        self.assertEqual(result, {})
        
        result = search_jamaican_banks('   ')
        self.assertEqual(result, {})

    def test_sagicor_bank_special_case(self):
        """Test Sagicor Bank which has space in code"""
        result = search_jamaican_banks('Sagicor Bank')
        expected = {'Sagicor Bank': self.banks['Sagicor Bank']}
        self.assertEqual(result, expected)
        
        result = search_jamaican_banks('Sagicor')
        expected = {'Sagicor Bank': self.banks['Sagicor Bank']}
        self.assertEqual(result, expected)

    def test_whitespace_handling(self):
        """Test handling of extra whitespace"""
        result = search_jamaican_banks('   BNSJ   ')
        expected = {'BNSJ': self.banks['BNSJ']}
        self.assertEqual(result, expected)
        
        result = search_jamaican_banks('BNSJ   Unclaimed   ')
        expected = {'BNSJ': self.banks['BNSJ']}
        self.assertEqual(result, expected)

    def test_mixed_case_search(self):
        """Test search with mixed case text"""
        result = search_jamaican_banks('BnSj UnClAiMeD BaLaNcEs')
        expected = {'BNSJ': self.banks['BNSJ']}
        self.assertEqual(result, expected)

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)