import requests
from lxml import etree
from urllib.parse import urljoin





class GetSiteDetail(object):
    """爬取用户上传的网站icon"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36"
    }
    tree = None

    def __init__(self, site_url, name=None, site_introduce=None, isvalid=1, id=0):
        """
        :param site_url: 网站url
        :param name: 网站名称 =>None
        :param site_introduce: 推荐原因=>None
        """
        self.site_url = site_url
        self.name = name
        self.site_introduce = site_introduce
        self.isvalid = isvalid
        self.content = None

        self.get_page()

    @property
    def get_status(self):
        try:
            content = requests.get(self.site_url, headers=self.headers, timeout=2)
            if content.status_code != 200:
                # url错误
                self.isvalid = 0
                return self.isvalid
            else:
                self.content = content
                self.isvalid = 1
                return self.isvalid
        except:
            # 超时或者拒接连接
            self.isvalid = -1
            return self.isvalid

    def get_page(self):
        try:
            if self.get_status == 1:
                self.tree = etree.HTML(self.content.content.decode("utf8"))
            elif self.get_status == 0:
                return "未嗅觉到资源"
            else:
                return "非法url地址"
        except:
            return "非法url地址"

    @property
    def get_site_introduce(self):
        if self.isvalid:
            if self.site_introduce:
                return self.site_introduce
            return "".join(self.tree.xpath("//*[@name='keywords']/@content|"
                                           "//*[@name='description']/@content"))
        self.site_introduce = "404页面"
        return self.site_introduce

    @property
    def get_site_title(self):
        if self.isvalid:
            if self.name:
                return self.name
            self.name = "".join(list("".join(self.tree.xpath("//title/text()")))[0:10])
            return self.name
        self.name = "404页面"
        return self.name

    @property
    def get_site_ico(self):
        if self.isvalid in [0, -1]:
            return self.isvalid
        try:
            href = "".join(self.tree.xpath(
                r'//*[@rel="apple-touch-icon" or(@rel="icon") or(@rel="shortcut icon") or(@type="image/ico")]/@href'))
            if href.rsplit(".")[-1] not in ["svgz", "jpg", "jpeg", "ico", "tiff", "gif", "svg", "jfif", "webp", "png"]:
                return 0
            return urljoin(self.site_url, href)
        except:
            return

# print(GetSiteDetail("https://www.code.com").get_site_ico)
