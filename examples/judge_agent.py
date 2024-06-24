import os

from pandasai.agent.agent import Agent
from pandasai.ee.agents.judge_agent import JudgeAgent
from pandasai.llm.openai import OpenAI

os.environ["PANDASAI_API_KEY"] = "$2a****************************"

judge = JudgeAgent()
agent = Agent("github-stars.csv", judge=judge)

print(agent.chat("return total stars count"))


# Using Judge standalone
llm = OpenAI("openai_key")
judge_agent = JudgeAgent(config={"llm": llm})
judge_agent.evaluate(
    query="return total github star count for year 2023",
    code="""sql_query = "SELECT COUNT(`users`.`login`) AS user_count, DATE_FORMAT(`users`.`starredAt`, '%Y-%m') AS starred_at_by_month FROM `users` WHERE `users`.`starredAt` BETWEEN '2023-01-01' AND '2023-12-31' GROUP BY starred_at_by_month ORDER BY starred_at_by_month asc"
    data = execute_sql_query(sql_query)
    plt.plot(data['starred_at_by_month'], data['user_count'])
    plt.xlabel('Month')
    plt.ylabel('User Count')
    plt.title('GitHub Star Count Per Month - Year 2023')
    plt.legend(loc='best')
    plt.savefig('/Users/arslan/Documents/SinapTik/pandas-ai/exports/charts/temp_chart.png')
    result = {'type': 'plot', 'value': '/Users/arslan/Documents/SinapTik/pandas-ai/exports/charts/temp_chart.png'}
                        """,
)
