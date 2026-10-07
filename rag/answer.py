# -*- coding: utf-8 -*-
"""端到端问答 CLI（检索增强）。用法（项目根）:
  python -m rag.answer "LM2596 absolute maximum input voltage?"
  python -m rag.answer "..." --model qwen2.5:7b-instruct-q4_K_M --bare
"""
import sys, json, argparse
sys.stdout.reconfigure(encoding="utf-8")

SYSTEM = ("You are an electronics datasheet QA assistant. Answer strictly from "
          "the provided datasheet excerpts; cite the part and section. If the "
          "excerpts do not contain the answer, say INSUFFICIENT_CONTEXT.")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("--model", default=None)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--bare", action="store_true", help="不用检索，裸模型对照")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    from . import llm
    context, hits = "", []
    if not args.bare:
        from .hierarchical import HierarchicalRetriever
        r = HierarchicalRetriever()
        context, hits = r.context_for(args.query, k=args.k)
    prompt = (f"Datasheet excerpts:\n{context}\n\nQuestion: {args.query}\n"
              f"Answer concisely with the exact value/statement and its source."
              ) if context else (f"Question: {args.query}\nAnswer concisely.")
    res = llm.chat(prompt, model=args.model, system=SYSTEM)
    if args.json:
        print(json.dumps({**res, "n_hits": len(hits),
                          "sources": [h["chunk_id"] for h in hits]},
                         ensure_ascii=False))
    else:
        for h in hits:
            print(f"[ctx] {h['part']} §{h['section']} score={h['score']}")
        print(f"\n{res['text']}\n\n(model={res['model']} "
              f"prompt_tokens={res['prompt_tokens']} "
              f"completion_tokens={res['completion_tokens']} "
              f"latency={res['latency_s']}s)")

if __name__ == "__main__":
    main()
