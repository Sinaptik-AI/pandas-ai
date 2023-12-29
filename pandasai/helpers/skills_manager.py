from typing import List, Optional
from pandasai.skills import Skill


class SkillsManager:
    """
    Manages Custom added Skills and tracks used skills for the query
    """

    _skills: List
    _used_skills: List[str]

    def __init__(self) -> None:
        self._skills = []
        self._used_skills = []

    def add_skills(self, *skills: Skill):
        """
        Add skills to the list of skills. If a skill with the same name
             already exists, raise an error.

        Args:
            *skills: Variable number of skill objects to add.
        """
        for skill in skills:
            if any(
                existing_skill.name == skill.name for existing_skill in self._skills
            ):
                raise ValueError(f"Skill with name '{skill.name}' already exists.")

        self._skills.extend(skills)

    def skill_exists(self, name: str):
        """
        Check if a skill with the given name exists in the list of skills.

        Args:
            name (str): The name of the skill to check.

        Returns:
            bool: True if a skill with the given name exists, False otherwise.
        """
        return any(skill.name == name for skill in self._skills)

    def get_skill_by_func_name(self, name: str):
        """
        Get a skill by its name.

        Args:
            name (str): The name of the skill to retrieve.

        Returns:
            Skill or None: The skill with the given name, or None if not found.
        """
        return next((skill for skill in self._skills if skill.name == name), None)

    def add_used_skill(self, skill: str):
        if self.skill_exists(skill):
            self._used_skills.append(skill)

    def __str__(self) -> str:
        """
        Present all skills
        Returns:
            str: _description_
        """
        return "".join(str(skill) for skill in self._skills)

    def prompt_display(self) -> Optional[str]:
        """
        Displays skills for prompt
        """
        if len(self._skills) == 0:
            return None

        return f"You can call the following functions that have been pre-defined for you:\n{self}"

    @property
    def used_skills(self):
        return self._used_skills

    @used_skills.setter
    def used_skills(self, value):
        self._used_skills = value

    @property
    def skills(self):
        return self._skills
