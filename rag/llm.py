# -*- coding: utf-8 -*-
"""Ollama 聊天后端：固定 seed/temperature 保证可复现，记录 token 用量。
RAG_LLM_MODEL 以 'scnet:' 开头时走超算互联网 OpenAI 兼容端点(key从环境变量或 .env)。"""
import os, json, time, urllib.request

HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
SCNET_BASE = os.environ.get("SCNET_BASE", "https://api.scnet.cn/api/llm/v1")


def _load_env():
    if not os.environ.get("SCNET_API_KEY"):
        for p in (os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
                  os.path.join(os.getcwd(), ".env")):
            if os.path.isfile(p):
                for line in open(p, encoding="utf-8"):
                    k, _, v = line.strip().partition("=")
                    if k == "SCNET_API_KEY" and v:
                        os.environ["SCNET_API_KEY"] = v
                        return


def DEFAULT_MODEL():
    return os.environ.get("RAG_LLM_MODEL", "qwen2.5:3b-instruct")


def chat(prompt, model=None, system=None, temperature=0.0, seed=42, timeout=300,
         thinking_off=True, max_tokens=4000):
    model = model or DEFAULT_MODEL()
    if model.startswith("scnet:"):
        return _scnet_chat(prompt, model[6:], system, temperature, timeout,
                           thinking_off, max_tokens)
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    body = json.dumps({
        "model": model, "messages": msgs, "stream": False,
        "options": {"temperature": temperature, "seed": seed}}).encode()
    req = urllib.request.Request(HOST + "/api/chat", data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        d = json.load(r)
    return {
        "text": (d.get("message") or {}).get("content", "").strip(),
        "model": d.get("model", model),
        "prompt_tokens": d.get("prompt_eval_count", 0),
        "completion_tokens": d.get("eval_count", 0),
        "latency_s": round(time.time() - t0, 2)}


def _scnet_chat(prompt, model, system, temperature, timeout, thinking_off, max_tokens):
    _load_env()
    key = os.environ.get("SCNET_API_KEY", "")
    if not key:
        raise RuntimeError("缺少 SCNET_API_KEY(项目根 .env 或环境变量)")
    msgs = ([{"role": "system", "content": system}] if system else []) + \
           [{"role": "user", "content": prompt}]
    body = {"model": model, "messages": msgs, "stream": False,
            "temperature": temperature, "max_tokens": max_tokens}
    if thinking_off:
        body["thinking"] = {"type": "disabled"}
        body["enable_thinking"] = False
    req = urllib.request.Request(
        SCNET_BASE + "/chat/completions", data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
    t0 = time.time()
    d = None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                d = json.load(r)
            break
        except Exception as e:
            if attempt == 2 or "status code" in str(e):  # 4xx 不重试
                raise
            time.sleep(15 * (attempt + 1))
    ch = d["choices"][0]
    finish = ch.get("finish_reason")
    text = (ch.get("message") or {}).get("content", "").strip()
    if finish == "length" and not text:  # 笔记陷阱: 思考吃光预算致空回
        body["max_tokens"] = max(max_tokens * 2, 8000)
        req = urllib.request.Request(
            SCNET_BASE + "/chat/completions", data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + key})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            d = json.load(r)
        ch = d["choices"][0]
        text = (ch.get("message") or {}).get("content", "").strip()
    usage = d.get("usage", {})
    return {
        "text": text, "model": d.get("model", model),
        "prompt_tokens": usage.get("prompt_tokens", 0),
        "completion_tokens": usage.get("completion_tokens", 0),
        "latency_s": round(time.time() - t0, 2), "finish_reason": ch.get("finish_reason")}
