from bilibili_api import Credential
class CredentialManager:
    def __init__(self, credential: Credential):
        self.credential = credential


    def get_cookie(self) -> str:
        # print(self.credentials.sessdata)
        # print(self.credential.bili_jct)
        sessdata = self.credential.sessdata
        bili_jct = self.credential.bili_jct
        buvid3 = self.credential.buvid3
        dedeuserid = self.credential.dedeuserid
        ac_time_value = self.credential.ac_time_value if hasattr(self.credential, 'ac_time_value') else None

        return f"SESSDATA={sessdata}; bili_jct={bili_jct}; buvid3={buvid3}; DedeUserID={dedeuserid}"