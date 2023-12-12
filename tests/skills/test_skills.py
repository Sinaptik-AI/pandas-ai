from typing import Optional
from unittest.mock import MagicMock, Mock, patch
import uuid
import pandas as pd

import pytest
from pandasai.agent import Agent
from pandasai.helpers.code_manager import CodeExecutionContext, CodeManager

from pandasai.helpers.skills_manager import SkillsManager
from pandasai.llm.fake import FakeLLM
from pandasai.skills import skill
from pandasai.smart_dataframe import SmartDataframe


class TestSkills:
    @pytest.fixture
    def llm(self, output: Optional[str] = None):
        return FakeLLM(output=output)

    @pytest.fixture
    def sample_df(self):
        return pd.DataFrame(
            {
                "country": [
                    "United States",
                    "United Kingdom",
                    "France",
                    "Germany",
                    "Italy",
                    "Spain",
                    "Canada",
                    "Australia",
                    "Japan",
                    "China",
                ],
                "gdp": [
                    19294482071552,
                    2891615567872,
                    2411255037952,
                    3435817336832,
                    1745433788416,
                    1181205135360,
                    1607402389504,
                    1490967855104,
                    4380756541440,
                    14631844184064,
                ],
                "happiness_index": [
                    6.94,
                    7.16,
                    6.66,
                    7.07,
                    6.38,
                    6.4,
                    7.23,
                    7.22,
                    5.87,
                    5.12,
                ],
            }
        )

    @pytest.fixture
    def smart_dataframe(self, llm, sample_df):
        return SmartDataframe(sample_df, config={"llm": llm, "enable_cache": False})

    @pytest.fixture
    def code_manager(self, smart_dataframe: SmartDataframe):
        return smart_dataframe.lake.code_manager

    @pytest.fixture
    def exec_context(self) -> MagicMock:
        return CodeExecutionContext(uuid.uuid4(), SkillsManager())

    @pytest.fixture
    def agent(self, llm, sample_df):
        return Agent(sample_df, config={"llm": llm, "enable_cache": False})

    def test_add_skills(self):
        skills_manager = SkillsManager()
        skill1 = Mock(name="SkillA", print="SkillA Print")
        skill2 = Mock(name="SkillB", print="SkillB Print")
        skills_manager.add_skills(skill1, skill2)

        # Ensure that skills are added
        assert skill1 in skills_manager.skills
        assert skill2 in skills_manager.skills

        # Test that adding a skill with the same name raises an error
        try:
            skills_manager.add_skills(skill1)
        except ValueError as e:
            assert str(e) == f"Skill with name '{skill1.name}' already exists."
        else:
            assert False, "Expected ValueError"

    def test_skill_exists(self):
        skills_manager = SkillsManager()
        skill1 = MagicMock()
        skill2 = MagicMock()
        skill1.name = "SkillA"
        skill2.name = "SkillB"
        skills_manager.add_skills(skill1, skill2)

        assert skills_manager.skill_exists("SkillA")
        assert skills_manager.skill_exists("SkillB")

        # Test that a non-existing skill is not found
        assert not skills_manager.skill_exists("SkillC")

    def test_get_skill_by_func_name(self):
        skills_manager = SkillsManager()
        skill1 = Mock()
        skill2 = Mock()
        skill1.name = "SkillA"
        skill2.name = "SkillB"
        skills_manager.add_skills(skill1, skill2)

        # Test that you can retrieve a skill by its function name
        retrieved_skill = skills_manager.get_skill_by_func_name("SkillA")
        assert retrieved_skill == skill1

        # Test that a non-existing skill returns None
        retrieved_skill = skills_manager.get_skill_by_func_name("SkillC")
        assert retrieved_skill is None

    def test_add_used_skill(self):
        skills_manager = SkillsManager()
        skill1 = Mock()
        skill2 = Mock()
        skill1.name = "SkillA"
        skill2.name = "SkillB"
        skills_manager.add_skills(skill1, skill2)

        # Test adding used skills
        skills_manager.add_used_skill("SkillA")
        skills_manager.add_used_skill("SkillB")

        # Ensure used skills are added to the used_skills list
        assert "SkillA" in skills_manager.used_skills
        assert "SkillB" in skills_manager.used_skills

    def test_prompt_display(self):
        skills_manager = SkillsManager()
        skill1 = Mock()
        skill2 = Mock()
        skill1.name = "SkillA"
        skill2.name = "SkillB"
        skill1.print = "SkillA"
        skill2.print = "SkillB"
        skills_manager.add_skills(skill1, skill2)

        # Test prompt_display method when skills exist
        prompt = skills_manager.prompt_display()
        assert (
            "You can call the following functions that have been pre-defined for you:"
            in prompt
        )

        # Test prompt_display method when no skills exist
        skills_manager.skills = []
        prompt = skills_manager.prompt_display()
        assert prompt is None

    @patch("pandasai.skills.inspect.signature", return_value="(a, b, c)")
    def test_skill_decorator(self, mock_inspect_signature):
        # Define skills using the decorator
        @skill
        def skill_a(*args, **kwargs):
            return "SkillA Result"

        @skill
        def skill_b(*args, **kwargs):
            return "SkillB Result"

        # Test the wrapped functions
        assert skill_a() == "SkillA Result"
        assert skill_b() == "SkillB Result"

        # Test the additional attributes added by the decorator
        assert skill_a.name == "skill_a"
        assert skill_b.name == "skill_b"

        assert skill_a.func_def == "def pandasai.skills.skill_a(a, b, c)"
        assert skill_b.func_def == "def pandasai.skills.skill_b(a, b, c)"

        assert (
            skill_a.print
            == """\n<function>\ndef pandasai.skills.skill_a(a, b, c)\n\n</function>\n"""  # noqa: E501
        )
        assert (
            skill_b.print
            == """\n<function>\ndef pandasai.skills.skill_b(a, b, c)\n\n</function>\n"""  # noqa: E501
        )

    @patch("pandasai.skills.inspect.signature", return_value="(a, b, c)")
    def test_skill_decorator_test_codc(self, llm):
        df = pd.DataFrame({"country": []})
        df = SmartDataframe(df, config={"llm": llm, "enable_cache": False})

        # Define skills using the decorator
        @skill
        def plot_salaries(*args, **kwargs):
            """
            Test skill A
            Args:
                arg(str)
            """
            return "SkillA Result"

        function_def = """
            Test skill A
            Args:
                arg(str)
"""  # noqa: E501

        assert function_def in plot_salaries.print

    def test_add_skills_with_agent(self, agent: Agent):
        # Define skills using the decorator
        @skill
        def skill_a(*args, **kwargs):
            return "SkillA Result"

        @skill
        def skill_b(*args, **kwargs):
            return "SkillB Result"

        agent.add_skills(skill_a)
        assert len(agent.lake.skills_manager.skills) == 1

        agent.lake.skills_manager.skills = []
        agent.add_skills(skill_a, skill_b)
        assert len(agent.lake.skills_manager.skills) == 2

    def test_add_skills_with_smartDataframe(self, smart_dataframe: SmartDataframe):
        # Define skills using the decorator
        @skill
        def skill_a(*args, **kwargs):
            return "SkillA Result"

        @skill
        def skill_b(*args, **kwargs):
            return "SkillB Result"

        smart_dataframe.add_skills(skill_a)
        assert len(smart_dataframe.lake.skills_manager.skills) == 1

        smart_dataframe.lake.skills_manager.skills = []
        smart_dataframe.add_skills(skill_a, skill_b)
        assert len(smart_dataframe.lake.skills_manager.skills) == 2

    def test_run_prompt(self, llm):
        df = pd.DataFrame({"country": []})
        df = SmartDataframe(df, config={"llm": llm, "enable_cache": False})

        function_def = """
<function>
def pandasai.skills.plot_salaries(merged_df: pandas.core.frame.DataFrame) -> str

</function>
"""  # noqa: E501

        @skill
        def plot_salaries(merged_df: pd.DataFrame) -> str:
            import matplotlib.pyplot as plt

            plt.bar(merged_df["Name"], merged_df["Salary"])
            plt.xlabel("Employee Name")
            plt.ylabel("Salary")
            plt.title("Employee Salaries")
            plt.xticks(rotation=45)
            plt.savefig("temp_chart.png")
            plt.close()

        df.add_skills(plot_salaries)

        df.chat("How many countries are in the dataframe?")
        last_prompt = df.last_prompt
        assert function_def in last_prompt

    def test_run_prompt_agent(self, agent):
        function_def = """
<function>
def pandasai.skills.plot_salaries(merged_df: pandas.core.frame.DataFrame) -> str

</function>
"""  # noqa: E501

        @skill
        def plot_salaries(merged_df: pd.DataFrame) -> str:
            import matplotlib.pyplot as plt

            plt.bar(merged_df["Name"], merged_df["Salary"])
            plt.xlabel("Employee Name")
            plt.ylabel("Salary")
            plt.title("Employee Salaries")
            plt.xticks(rotation=45)
            plt.savefig("temp_chart.png")
            plt.close()

        agent.add_skills(plot_salaries)

        agent.chat("How many countries are in the dataframe?")
        last_prompt = agent.lake.last_prompt

        assert function_def in last_prompt

    def test_run_prompt_without_skills(self, agent):
        agent.chat("How many countries are in the dataframe?")

        last_prompt = agent.lake.last_prompt

        assert "<function>" not in last_prompt
        assert "</function>" not in last_prompt
        assert (
            "You can call the following functions that have been pre-defined for you:"
            not in last_prompt
        )

    def test_code_exec_with_skills_no_use(
        self, code_manager: CodeManager, exec_context
    ):
        code = """result = {'type': 'number', 'value': 1 + 1}"""
        skill1 = MagicMock()
        skill1.name = "SkillA"
        exec_context._skills_manager._skills = [skill1]
        code_manager.execute_code(code, exec_context)
        assert len(exec_context._skills_manager.used_skills) == 0

    def test_code_exec_with_skills(self, code_manager: CodeManager):
        code = """plot_salaries()
result = {'type': 'number', 'value': 1 + 1}"""

        @skill
        def plot_salaries() -> str:
            return "return {'type': 'number', 'value': 1 + 1}"

        sm = SkillsManager()
        sm.add_skills(plot_salaries)
        exec_context = CodeExecutionContext(uuid.uuid4(), sm)
        result = code_manager.execute_code(code, exec_context)

        assert len(exec_context._skills_manager.used_skills) == 1
        assert exec_context._skills_manager.used_skills[0] == "plot_salaries"
        assert result == {"type": "number", "value": 1 + 1}
