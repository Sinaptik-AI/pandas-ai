import re
from pandasai.exceptions import MaliciousQueryError


class UserQuery:
    def __init__(self, user_query: str):
        self._check_malicious_keywords_in_query(user_query)
        self.value = user_query

    def __str__(self):
        return self.value

    def __repr__(self):
        return f"UserQuery(value={self._value})"

    def _check_malicious_keywords_in_query(self, user_query):
        dangerous_pattern = re.compile(
            r"\b(os|io|chr|b64decode)\b|"
            r"(\.os|\.io|'os'|'io'|\"os\"|\"io\"|chr\(|chr\)|chr |\(chr)"
        )
        if bool(dangerous_pattern.search(user_query)):
            raise MaliciousQueryError(
                "The query contains references to io or os modules or b64decode method which can be used to execute or access system resources in unsafe ways."
            )

    def __dict__(self):
        return self.value

    def to_json(self):
        return self.value
