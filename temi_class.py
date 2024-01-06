class TemiClass:
    id=None
    ip=None
    ws=None
    def __init__(self,id,ip,ws) -> None:
        self.id=id
        self.ip=ip
        self.ws=ws
    def detail(self):
        print(f"Temi id ->\t{self.id}")
        print(f"Temi ip ->\t{self.ip}")
        print(f"Temi ws ->\t{self.ws}")