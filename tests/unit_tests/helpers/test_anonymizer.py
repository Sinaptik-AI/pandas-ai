import pandasai.pandas as pd
from pandasai.helpers.anonymizer import Anonymizer


class TestAnonymizeDataFrameHead:
    def test_is_valid_email(self):
        assert Anonymizer._is_valid_email("john.doe@gmail.com") is True
        assert Anonymizer._is_valid_email("john.doe@gmail") is False

    def test_is_valid_phone_number(self):
        assert Anonymizer._is_valid_phone_number("+1 (123) 456-7890") is True
        assert Anonymizer._is_valid_phone_number("123-456-789") is False

    def test_is_valid_credit_card(self):
        assert Anonymizer._is_valid_credit_card("1234-5678-9012-3456") is True
        assert Anonymizer._is_valid_credit_card("1234-5678-9012") is False

    def test_generate_random_email(self):
        email = Anonymizer._generate_random_email()
        assert Anonymizer._is_valid_email(email) is True

    def test_generate_random_phone_number(self):
        original_phone_number = "+1 (123) 456-7890"
        new_phone_number = Anonymizer._generate_random_phone_number(
            original_phone_number
        )
        assert Anonymizer._is_valid_phone_number(new_phone_number) is True

    def test_generate_random_credit_card(self):
        credit_card = Anonymizer._generate_random_credit_card()
        assert Anonymizer._is_valid_credit_card(credit_card) is True

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
        anonymized_df_head = Anonymizer.anonymize_dataframe_head(df)

        assert df.head().values.tolist() != anonymized_df_head.values.tolist()

    def test_anonymize_dataframe_head_with_boolean(self):
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
            "Grade": [True, False, True],
        }
        df = pd.DataFrame(data)
        df["Grade"] = df["Grade"].astype("boolean")
        anonymized_df_head = Anonymizer.anonymize_dataframe_head(df)
        assert anonymized_df_head.dtypes.all() == df.dtypes.all()

    def test_anonymize_dataframe_head_with_Int64(self):
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
            "Grade": [0, 1, None],
        }
        df = pd.DataFrame(data)
        df["Grade"] = df["Grade"].astype("Int64")
        anonymized_df_head = Anonymizer.anonymize_dataframe_head(df)
        assert anonymized_df_head.dtypes.all() == df.dtypes.all()
