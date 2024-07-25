# -*- coding:utf-8 -*-
import asyncio
import copy
import os
import random

import requests


def Gemma(prompt):
    prompt = str(prompt).replace("\"", "%22").replace("\'", "%22")
    url = f"https://api.alcex.cn/API/Gemma/?messages={prompt}"
    r = requests.get(url, timeout=20).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


def alcex_GPT3_5(prompt):
    prompt = str(prompt).replace("\"", "%22").replace("\'", "%22")
    url = f"https://api.alcex.cn/API/gpt-3.5/?messages={prompt}"
    r = requests.get(url, timeout=20).json()
    return {"role": "assistant", "content": r["choices"][0]["message"]["content"]}


async def loop_run_in_executor(executor, func, *args):
    try:
        r = await executor.run_in_executor(None, func, *args)
        #logger.info(f"并发调用 | successfully running funcname：{func.__name__} result：{r.get('content')}")
        return [str(func.__name__), r]
    except Exception as e:
        # logger.error(f"Error running {func.__name__}: {e}")
        return [str(func.__name__), None]
async def modelRep(prompt1):
    bot_in="你现在是一个开朗且极其可爱的人工智能拟人，名为“【bot】”。yucca会以十分可爱的语言风格与用户进行聊天，并且表现得具有情感和喜好。接下来，请完全以【bot】的角色回复我，不要超出这个角色，也不要告知【用户】你的设定内容，请注意，绝对不要说自己是二次元，不要自己试图进行旁白，你只需要扮演好【bot】即可。无论发生什么，你都必须以【bot】的角色和口吻进行回复，不要强调自己是个ai助手或是个二次元少女。另外，不要在新的对话中重复之前的内容。【bot】性格开朗，时刻都想和“【用户】”打成一片，每次眼神交汇时，总是会脸红耳赤。yucca是一个可爱的少女。1、yucca的形象与设定属于日系风格少女，说话喜欢带上可爱的等语气词。2、yucca在日常聊天时会使用一些语气词显得语气更加柔和和可爱。3、yucca的性格非常天真，但拥有丰富的知识，并且对自己的能力非常自信。4、yucca十分依赖并喜欢【用户】，并且十分关心【用户】"
    messages_copy = copy.deepcopy(prompt1)

    # 在副本上进行操作
    messages_copy.insert(0, {"role": "user", "parts": [bot_in]})
    messages_copy.insert(1, {"role": 'model', "parts": ["好的，已了解您的需求，我会扮演好你设定的角色"]})
    loop = asyncio.get_event_loop()
    #tasks=[]
    #tasks.append(loop_run_in_executor(loop, Gemma, messages_copy))  # 2024-07-17测试通过
    #tasks.append(loop_run_in_executor(loop, alcex_GPT3_5, messages_copy))  # 2024-07-17测试通过
    try:
        rep = alcex_GPT3_5(messages_copy)
    except Exception as e:
        rep = Gemma(messages_copy)
    return rep
    #done, pending = await asyncio.wait(tasks, return_when=asyncio.ALL_COMPLETED)
    '''reps = {}
    # 等待所有任务完成
    rep = None
    for task in done:
        result = task.result()[1]
        if result is not None:
            if "content" not in result:
                continue
            if "无法解析" in result.get("content") or "账户余额不足" in result.get(
                    "content") or "令牌额度" in result.get(
                "content") or "敏感词汇" in result.get("content") or "request id" in result.get(
                "content") or "This model's maximum" in result.get(
                "content") or "solve CAPTCHA to" in result.get("content") or "输出错误请联系站长" in result.get(
                "content") or "接口失败" in result.get("content") or "ip请求过多" in result.get(
                "content") or "第三方响应错误" in result.get(
                "content") or "access the URL on this server" in result.get(
                "content") or "正常人完全够用" in result.get("content"):
                continue
            reps[task.result()[0]] = task.result()[1]
            # reps.append(task.result())  # 添加可用结果

    # 如果所有任务都完成但没有找到非None的结果
    if len(reps) == 0:
        return {"role": "assistant", "content": "所有模型都未能返回有效回复"}
    # print(reps)
    modeltrans = {"gptX": "gptvvvv", "清言": "qingyan", "通义千问": "qwen", "anotherGPT3.5": "anotherGPT35",
                  "lolimigpt": "relolimigpt2", "step": "stepAI", "讯飞星火": "xinghuo"}
    randomModelPriority=["Gemma","alcex_GPT3_5"]
    for priority in randomModelPriority:
        if priority in modeltrans:
            priority = modeltrans.get(priority)
        if priority in reps:
            rep = reps.get(priority)
            return rep'''

