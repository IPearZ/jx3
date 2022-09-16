import os
import json
from nonebot import get_driver
from pydantic import BaseModel, Field

profession_data_path = os.path.dirname(os.path.abspath(__file__)) + "/data/profession.json"

with open(profession_data_path, "r") as f:
    profession_data = json.load(f)


class Jx3Config(BaseModel):
    # Your Config Here
    server: str = Field("", alias="jx3_server")
    jx3api_host: str = Field("", alias="jx3_jx3api_host")

    class Config:
        extra = "ignore"


class Jx3ProfessionConfig(BaseModel):
    # Your Config Here
    profession = profession_data
    # 将profession_data转换为字典
    profession_dict = {}
    for i in profession:
        for j in profession[i]:
            profession_dict[j] = i

    @staticmethod
    def get_profession(self, alias):
        return self.profession_dict.get(alias)


config = get_driver().config
jx3_config = Jx3Config.parse_obj(config)
jx3_profession_config = Jx3ProfessionConfig.parse_obj(config)
