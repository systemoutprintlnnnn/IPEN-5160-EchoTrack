import asyncio
import json
from pprint import pprint
from pymongo import MongoClient

from bilibili_api.comment import OrderType

from BilibiliScraper import BilibiliScraper
from bilibili_api import Credential, search, topic, sync, comment

SESSIONDATA = "8de4b28e%2C1759379533%2C426c1%2A42CjCOME2savjXqodnd14Arv5y6q9rX2fhKHlbL6fTboeaVMD68P0o0pSXcfkpmEZQi3ISVm15SlEwZS1YQmhFbmJvUlY2RkVMamctNEdBSlQ4ekV2bGIyWFBnZHNLMlp0TzFXZGhWeFVzcjUzNzB2UFdIYWdvdGxJTTJZdE56czF2c0RyWUdXWDZRIIEC"
BILI_JCT = "120bf3765734ab46c7fb24726edef950"
BUVID3 = "A2D4DF5D-8110-2AD2-712E-CB70E86E460D66077infoc"
DEDEUSERID = "35556285"
AC_TIME_VALUE = "88f211501d832c4b8685a028f94063c2"

class Bilibili:

    def __init__(self):
        credential = Credential(SESSIONDATA, BILI_JCT, BUVID3, DEDEUSERID, AC_TIME_VALUE)
        self.credential = credential
        print(sync(credential.check_refresh()))
        if sync(credential.check_refresh()):
            sync(credential.refresh())
        # ac_time_value = "4a478ebc8540615b1bd81d534ca5dda2"
        # credential = Credential(sessionData, bili_jct, buvid3, dedeuserid, ac_time_value)
        pass

    # async def main(self) -> None:
    #     u = user.User(self.__uid, self.credential)
    #     res0 = await u.get_dynamics_new(940233543259258887)
    #
    #     print(res0)
    #     # res = await u.get_all_followings()
    #     # print(res)

    async def main(self) -> None:
        b = BilibiliScraper()
        keyword_list = ["iPhone 15", "小米 15"]



        # test
        # c = await comment.get_comments_lazy(113564136249182, comment.CommentResourceType.VIDEO, '',OrderType.LIKE, self.credential)
        # replies = c['replies']
        # print(replies)

        # 一次20个视频
        for i in range(1, 3):
            for keyword in keyword_list:
                await b.get_video_comments_by_keyword(keyword,i)

        # 获取指定视频
        # await b.get_all_comments_by_video("337044251", self.credential, OrderType.LIKE)




if __name__ == "__main__":
    # 获取视频对应评论区
    bilibili = Bilibili()
    asyncio.run(bilibili.main())
