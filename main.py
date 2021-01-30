from typing import Iterator, List, Dict, Optional

import jieba
import uvicorn
from fastapi import FastAPI, Query, HTTPException
from pydantic import BaseModel
from starlette import status

dictionary = dict()


def init():
    """
    1 加载字典文件到内存
    2 将所有中文词导入 jieba 字典库

    可以考虑把 words.txt 写入数据库或者 ES 做持久化处理
    可以做一个 jieba 服务来不断添加词汇 (jieba.add_word())
    但是必须要需要维护一个 jieba_dict.txt 记录所有的中文词汇，以便 jieba 服务
    重启后可以重新加载所有的历史数据
    """
    with open("words.txt", "r") as f:
        for x in f:
            if not x:
                continue
            ch, en = x.strip().split(",")
            en = en.strip("_")
            dictionary[ch] = en
    with open("jieba_dict.txt", "w") as w:
        for key in dictionary:
            w.write(f"{key}\n")
    jieba.load_userdict("jieba_dict.txt")


def match(chinese: str) -> Iterator:
    """输出中文词句，使用 jieba 库切分成多个词语
    """
    return jieba.cut(chinese)


app = FastAPI()


@app.router.get("/transfer")
async def transfer(word=Query("", description="要翻译的词")):
    cut = list(match(word))
    mapping = dict()
    for w in cut:
        mapping[w] = dictionary.get(w)
    result = "_".join(filter(lambda x: x is not None, mapping.values()))
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="item not found"
        )
    return dict(
        input_word=word,
        cut=cut,
        mapping=mapping,
        result=result
    )


if __name__ == '__main__':
    init()
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=9999
    )
