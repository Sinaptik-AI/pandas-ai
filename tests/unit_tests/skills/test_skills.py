import uuid
from typing import Optional
from unittest.mock import MagicMock, Mock, patch

import pandas as pd
import pytest

from pandasai import Agent
from pandasai.helpers.skills_manager import SkillsManager
from pandasai.llm.fake import FakeLLM
from pandasai.pipelines.chat.code_cleaning import CodeExecutionContext
from pandasai.skills import Skill, skill


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

    # @pytest.fixture
    # def code_manager(self, agent: Agent):
    #     return CodeManager(
    #         agent.context.dfs,
    #         config=agent.context.config,
    #         logger=agent.logger,
    #     )

    @pytest.fixture
    def exec_context(self) -> MagicMock:
        return CodeExecutionContext(uuid.uuid4(), SkillsManager())

    @pytest.fixture
    def agent(self, llm, sample_df):
        return Agent(sample_df, config={"llm": llm, "enable_cache": False})

    def test_add_skills(self):
        skills_manager = SkillsManager()

        @skill
        def skill1():
            """SkillA docstring"""
            pass

        skill2 = Skill.from_function(func=lambda _: None, description="Skill B")

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
    def test_skill_decorator(self, _mock_inspect_signature):
        # Define skills using the decorator
        @skill
        def skill_a(*args, **kwargs):
            """
            Test skill A
            Args:
                arg(str)
            """
            return "SkillA Result"

        @skill
        def skill_b(*args, **kwargs):
            """
            Test skill B
            Args:
                arg(str)
            """
            return "SkillB Result"

        # Test the wrapped functions
        assert skill_a() == "SkillA Result"
        assert skill_b() == "SkillB Result"

        # Test the additional attributes added by the decorator
        assert skill_a.name == "skill_a"
        assert skill_b.name == "skill_b"

        # check the function definition
        assert skill_a._signature == "def skill_a(a, b, c):"
        assert skill_b._signature == "def skill_b(a, b, c):"

    @patch("pandasai.skills.inspect.signature", return_value="(a, b, c)")
    def test_skill_decorator_test_code(self, _mock_inspect_signature):
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

        assert function_def in str(plot_salaries)

    def test_add_skills_with_agent(self, agent: Agent):
        @skill
        def skill_a(*args, **kwargs):
            """Skill A"""
            return "SkillA Result"

        skill_b = Skill.from_function(
            func=lambda _: "SkillB Result", description="Skill B"
        )

        agent.add_skills(skill_a)
        assert len(agent.context.skills_manager.skills) == 1

        agent.context.skills_manager.skills = []
        agent.add_skills(skill_a, skill_b)
        assert len(agent.context.skills_manager.skills) == 2

    def test_run_prompt(self, llm):
        df = pd.DataFrame({"country": []})
        df = Agent([df], config={"llm": llm, "enable_cache": False})

        function_def = """
<function>
def plot_salaries(merged_df: pandas.core.frame.DataFrame):
    \"\"\"Plot salaries given a dataframe of employees and their salaries\"\"\"
</function>
"""  # noqa: E501

        @skill
        def plot_salaries(merged_df: pd.DataFrame):
            """Plot salaries given a dataframe of employees and their salaries"""
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
def plot_salaries(merged_df: pandas.core.frame.DataFrame):
    \"\"\"Plot salaries given a dataframe of employees and their salaries\"\"\"
</function>
"""  # noqa: E501

        @skill
        def plot_salaries(merged_df: pd.DataFrame):
            """Plot salaries given a dataframe of employees and their salaries"""
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
        last_prompt = agent.last_prompt

        assert function_def in last_prompt

    def test_run_prompt_without_skills(self, agent):
        agent.chat("How many countries are in the dataframe?")

        last_prompt = agent.last_prompt

        assert "<function>" not in last_prompt
        assert "</function>" not in last_prompt
        assert (
            "You can call the following functions that have been pre-defined for you:"
            not in last_prompt
        )

    @pytest.mark.skip(reason="Removed CodeManager class")
    def test_code_exec_with_skills_no_use(self, code_manager, exec_context):
        code = """result = {'type': 'number', 'value': 1 + 1}"""
        skill1 = MagicMock()
        skill1.name = "SkillA"
        exec_context.skills_manager.skills = [skill1]
        code_manager.execute_code(code, exec_context)
        assert len(exec_context.skills_manager.used_skills) == 0

    @pytest.mark.skip(reason="Removed CodeManager class")
    def test_code_exec_with_skills(self, code_manager):
        code = """plot_salaries()
result = {'type': 'number', 'value': 1 + 1}"""

        @skill
        def plot_salaries() -> str:
            """Plots salaries"""
            return "return {'type': 'number', 'value': 1 + 1}"

        sm = SkillsManager()
        sm.add_skills(plot_salaries)
        exec_context = CodeExecutionContext(uuid.uuid4(), sm)
        result = code_manager.execute_code(code, exec_context)

        assert len(exec_context.skills_manager.used_skills) == 1
        assert exec_context.skills_manager.used_skills[0] == "plot_salaries"
        assert result == {"type": "number", "value": 1 + 1}
