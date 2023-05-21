import numpy as np
import pandas as pd
import pytest

from pandasai.helpers.anonymizer import *


class TestAnonymizeDataFrameHead:
    def test_is_valid_email(self):
        assert is_valid_email("john.doe@gmail.com") is True
        assert is_valid_email("john.doe@gmail") is False

    def test_is_valid_phone_number(self):
        assert is_valid_phone_number("+1 (123) 456-7890") is True
        assert is_valid_phone_number("123-456-789") is False

    def test_is_valid_credit_card(self):
        assert is_valid_credit_card("1234-5678-9012-3456") is True
        assert is_valid_credit_card("1234-5678-9012") is False

    def test_generate_random_email(self):
        email = generate_random_email()
        assert is_valid_email(email) is True

    def test_generate_random_phone_number(self):
        original_phone_number = "+1 (123) 456-7890"
        new_phone_number = generate_random_phone_number(original_phone_number)
        assert is_valid_phone_number(new_phone_number) is True

    def test_generate_random_credit_card(self):
        credit_card = generate_random_credit_card()
        assert is_valid_credit_card(credit_card) is True

    def test_copy_head(self):
        data = {"A": [1, 2, 3], "B": [4, 5, 6]}
        df = pd.DataFrame(data)
        df_head = copy_head(df)
        assert df.head().equals(df_head) is True

    def test_anonymize_dataframe_head(self):
        data = {
            "Email": [
                "john.doe@gmail.com",
                "jane.doe@yahoo.com",
                "jake.doe@hotmail.com",
            ],
            "Phone": ["+1 (123) 456-7890", "+1 (234) 567-8901", "+1 (345) 678-9012"],
            "Credit Card": [
                "1234-5678-9012-3456",
                "2345-6789-0123-4567",
                "3456-7890-1234-5678",
            ],
        }
        df = pd.DataFrame(data)
        anonymized_df_head = anonymize_dataframe_head(df)

        assert df.head().values.tolist() != anonymized_df_head.values.tolist()

    def test_anonymize_categorical_column_with_nan(self):
        data = {
            "Email": [
                "john.doe@gmail.com",
                "jane.doe@yahoo.com",
                "jake.doe@hotmail.com",
            ],
            "Phone": ["+1 (123) 456-7890", "+1 (234) 567-8901", "+1 (345) 678-9012"],
            "Credit Card": [
                "1234-5678-9012-3456",
                "2345-6789-0123-4567",
                "3456-7890-1234-5678",
            ],
            "Grade": ["A", "B", np.nan],
        }

        df = pd.DataFrame(data)
        df["Grade"] = df["Grade"].astype("category")

        anonymized_df_head = anonymize_dataframe_head(df)
        assert anonymized_df_head.dtypes.all() == df.dtypes.all()

        with pytest.raises(TypeError):
            anonymized_df_head = anonymize_dataframe_head(df, force_conversion=False)
            assert anonymized_df_head.dtypes.all() == df.dtypes.all()
