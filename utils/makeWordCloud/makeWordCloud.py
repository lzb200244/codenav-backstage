from pyecharts import options as opts
from pyecharts.charts import WordCloud
from utils.CountWord import CountWord
from utils.Tencent.cos import tencent


# pip install -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
class MakeWord(object):
    def __init__(self, words):
        self.words = words
        self.wordcloud_base()

    def wordcloud_base(self) -> WordCloud:
        wordcloud = (
            WordCloud(init_opts=opts.InitOpts(bg_color='rgb(255,255,255)',
                                              width='500px',
                                              height='330px',
                                              ), )
                .add("", self.words, word_size_range=[20, 70], )
                .set_global_opts())
        return wordcloud

    def make(self):
        g = self.wordcloud_base()
        g.render("index.html")
        file = open("./index.html", "rb")
        tencent.upload_file(file, "index.html", bucket="defaultdata-1311013567")
        return True


if __name__ == '__main__':
    words = []
    for item in CountWord.get().items():
        words.append(item)
    MakeWord(words=sorted(words, reverse=True, key=lambda x: x[1])[:80]).make()
    MakeWord(words).make()
    pass
