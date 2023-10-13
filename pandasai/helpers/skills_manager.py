from typing import List

# from pandasai.skills import skill


class SkillsManager:
    _skills: List

    def __init__(self) -> None:
        self._skills = []

    def add_skills(self, *skills):
        self._skills.extend(skills)

    def __str__(self) -> str:
        """
        Present all skills
        Returns:
            str: _description_
        """
        skills_repr = ""
        for skill in self._skills:
            skills_repr = skills_repr + skill.print

        return skills_repr

    def prompt_display(self) -> str:
        """
        Displays skills for prompt
        """
        if len(self._skills) == 0:
            return

        return (
            """
You can also use the following functions, if relevant:

"""
            + self.__str__()
        )
