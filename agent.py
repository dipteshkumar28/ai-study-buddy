"""StudyForge agent graph (LangGraph + LangChain + Groq)."""
import json, os, re
from typing import List, Literal, TypedDict
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

MAX_REVISIONS = 2


def llm(temp: float = 0.3) -> ChatGroq:
    return ChatGroq(model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"), temperature=temp)


def structured(schema, prompt, temp: float = 0.0):
    """Structured output with a JSON-parsing fallback (never crashes on a missed tool call)."""
    try:
        return llm(temp).with_structured_output(schema).invoke(prompt)
    except Exception:
        raw = llm(temp).invoke(
            prompt + "\n\nReply with ONLY valid JSON matching this schema, no prose:\n"
            + json.dumps(schema.model_json_schema())).content
        return schema.model_validate_json(re.search(r"\{.*\}", raw, re.S).group(0))


# ---------- structured outputs ----------
class Route(BaseModel):
    task: Literal["chat", "explain", "summarize", "plan", "quiz"]


class Review(BaseModel):
    ok: bool = Field(description="True if accurate, clear and right for the student's level")
    issues: str = Field(default="", description="Concrete problems to fix, if any")


class QA(BaseModel):
    question: str
    options: List[str] = Field(description="Exactly 4 options")
    answer_index: int = Field(description="0-based index of the correct option")
    concept: str = Field(description="Short name of the concept tested")
    explanation: str


class Quiz(BaseModel):
    questions: List[QA]


class State(TypedDict, total=False):
    task: str
    query: str
    level: str
    context: str
    history: str
    output: str
    ok: bool
    review: str
    revisions: int
    quiz: list
    answers: list
    report: dict
    trace: list


SYS = ("You are StudyForge, an expert, encouraging tutor. Student level: {level}. "
       "Use clear markdown, analogies and concrete examples.")


def _ctx(s):
    c = s.get("context") or ""
    return f"\n\nStudent's notes (prioritise these):\n{c[:12000]}" if c else ""


def _log(s, msg):
    return (s.get("trace") or []) + [msg]


def _ask(s, prompt, temp=0.3):
    return llm(temp).invoke([("system", SYS.format(level=s["level"])), ("human", prompt)]).content


# ---------- nodes ----------
def route(s: State):
    try:
        task = structured(Route,
            "Classify the student's message into ONE task: chat (greeting/small talk/anything not about "
            "studying), explain (concept/question), summarize (summarise notes/text), plan (study plan/"
            "schedule), quiz (wants to be tested).\nMessage: " + s["query"]).task
    except Exception:
        task = "explain"
    return {"task": task, "trace": _log(s, f"🧭 Router → **{task}**")}


def chat(s: State):
    out = _ask(s, f"Reply briefly and warmly to: {s['query']}\nIf it's small talk, invite them to ask a "
                  "study question, upload notes, request a study plan, or take a quiz.")
    return {"output": out, "trace": _log(s, "💬 Tutor agent replied")}


def explain(s: State):
    out = _ask(s, f"Conversation so far:\n{s.get('history', '')}\n\nQuestion: {s['query']}{_ctx(s)}\n\n"
                  "Explain with: 1) intuition, 2) key idea, 3) worked example, 4) a common mistake, "
                  "5) one-line recap.")
    return {"output": out, "revisions": 0, "trace": _log(s, "📘 Tutor agent drafted an explanation")}


def critique(s: State):
    r = structured(Review,
        f"Act as a strict fact-checker. Review this answer for accuracy, clarity and suitability for a "
        f"{s['level']} student.\nQuestion: {s['query']}\n\nAnswer:\n{s['output']}")
    msg = "🔍 Critic agent: approved ✅" if r.ok else f"🔍 Critic agent: found issues → {r.issues[:90]}"
    return {"ok": r.ok, "review": r.issues, "trace": _log(s, msg)}


def revise(s: State):
    out = _ask(s, f"Improve this answer by fixing these issues: {s['review']}\n\nOriginal:\n{s['output']}")
    return {"output": out, "revisions": s.get("revisions", 0) + 1, "trace": _log(s, "✍️ Reviser agent rewrote the answer")}


def after_critique(s: State):
    return "revise" if (not s.get("ok") and s.get("revisions", 0) < MAX_REVISIONS) else END


def summarize(s: State):
    out = _ask(s, f"{s['query']}{_ctx(s)}\n\nGive: TL;DR (2 lines), key points, key terms glossary, "
                  "and 3 self-test questions.")
    return {"output": out, "trace": _log(s, "🗒️ Summarizer agent condensed the material")}


def plan(s: State):
    out = _ask(s, f"Create a realistic, day-by-day study plan for: {s['query']}{_ctx(s)}\n"
                  "Include daily goals, time blocks, active-recall and spaced-repetition checkpoints, "
                  "and a final self-assessment. Use a markdown table.")
    return {"output": out, "trace": _log(s, "📅 Planner agent built a study plan")}


def quiz(s: State):
    n = s.get("num_questions", 5) if isinstance(s.get("num_questions"), int) else 5
    r = structured(Quiz,
        f"Write {n} multiple-choice questions (4 options each, one correct) for a {s['level']} student on: "
        f"{s['query']}.{_ctx(s)}\nMix recall and application; tag each with a short concept name.", 0.5)
    qs = [q.model_dump() for q in r.questions if len(q.options) == 4 and 0 <= q.answer_index < 4]
    return {"quiz": qs, "output": "I built a quiz for you - open the **Adaptive Quiz** tab!",
            "trace": _log(s, f"🧪 Quiz agent generated {len(qs)} questions")}


def diagnose(s: State):
    qs, ans = s["quiz"], s["answers"]
    wrong = [q for q, a in zip(qs, ans) if a != q["answer_index"]]
    weak = sorted({q["concept"] for q in wrong})
    lesson = ""
    if wrong:
        missed = "\n".join(f"- {q['question']} (correct: {q['options'][q['answer_index']]})" for q in wrong)
        lesson = _ask(s, f"The student missed these questions:\n{missed}\n\nWrite a short, kind remediation "
                         "mini-lesson for each weak concept: why they likely erred, the correct idea, a memory trick.")
    rep = {"score": len(qs) - len(wrong), "total": len(qs), "weak": weak, "lesson": lesson}
    return {"report": rep, "trace": _log(s, f"🩺 Diagnostic agent found {len(weak)} weak concept(s)")}


def build_graph():
    g = StateGraph(State)
    for name, fn in [("route", route), ("chat", chat), ("explain", explain), ("critique", critique), ("revise", revise),
                     ("summarize", summarize), ("plan", plan), ("quiz", quiz), ("diagnose", diagnose)]:
        g.add_node(name, fn)
    targets = {k: k for k in ["chat", "explain", "summarize", "plan", "quiz", "diagnose"]}
    g.add_conditional_edges(START, lambda s: "route" if s.get("task", "auto") == "auto" else s["task"],
                            {"route": "route", **targets})
    g.add_conditional_edges("route", lambda s: s["task"], targets)
    g.add_edge("explain", "critique")
    g.add_conditional_edges("critique", after_critique, {"revise": "revise", END: END})
    g.add_edge("revise", "critique")
    for n in ["chat", "summarize", "plan", "quiz", "diagnose"]:
        g.add_edge(n, END)
    return g.compile()
