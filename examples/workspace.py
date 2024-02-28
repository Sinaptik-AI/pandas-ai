import os

from pandasai.workspace import Workspace


os.environ["PANDASAI_API_KEY"] = "$2a$10$/4x9CVetluLt2Rqns7p7Zut8xL******"


workspace = Workspace("new-orders-space")

workspace.chat("return orders count groupby country")

workspace.chat("Yes")
