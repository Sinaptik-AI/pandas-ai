import unittest
import pandas as pd
from pandasai.helpers.anonymizer import *

class TestAnonymizeDataFrameHead(unittest.TestCase):

    def test_is_valid_email(self):
        self.assertTrue(is_valid_email('john.doe@gmail.com'))
        self.assertFalse(is_valid_email('john.doe@gmail'))

    def test_is_valid_phone_number(self):
        self.assertTrue(is_valid_phone_number('+1 (123) 456-7890'))
        self.assertFalse(is_valid_phone_number('123-456-789'))

    def test_is_valid_credit_card(self):
        self.assertTrue(is_valid_credit_card('1234-5678-9012-3456'))
        self.assertFalse(is_valid_credit_card('1234-5678-9012'))

    def test_generate_random_email(self):
        email = generate_random_email()
        self.assertTrue(is_valid_email(email))

    def test_generate_random_phone_number(self):
        original_phone_number = '+1 (123) 456-7890'
        new_phone_number = generate_random_phone_number(original_phone_number)
        self.assertTrue(is_valid_phone_number(new_phone_number))

    def test_generate_random_credit_card(self):
        credit_card = generate_random_credit_card()
        self.assertTrue(is_valid_credit_card(credit_card))

    def test_copy_head(self):
        data = {'A': [1, 2, 3], 'B': [4, 5, 6]}
        df = pd.DataFrame(data)
        df_head = copy_head(df)
        self.assertEqual(df.head().equals(df_head), True)

    def test_anonymize_dataframe_head(self):
        data = {
            'Email': ['john.doe@gmail.com', 'jane.doe@yahoo.com', 'jake.doe@hotmail.com'],
            'Phone': ['+1 (123) 456-7890', '+1 (234) 567-8901', '+1 (345) 678-9012'],
            'Credit Card': ['1234-5678-9012-3456', '2345-6789-0123-4567', '3456-7890-1234-5678']
        }
        df = pd.DataFrame(data)
        anonymized_df_head = anonymize_dataframe_head(df)

        self.assertNotEqual(df.head().values.tolist(), anonymized_df_head.values.tolist())