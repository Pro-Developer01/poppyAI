// apps/web/src/components/ChatBox.tsx
"use client";

import { useState } from "react";
import { useAgentStream } from "../hooks/useAgentStream";

const STAGE_LABELS: Record<string, string> = {
    route: "Routing", retrieve: "Retrieving", grade: "Grading",
    rewrite: "Rewriting query", web_search: "Searching web",
    plan: "Planning", execute_sub: "Looking up", combine: "Combining",
    generate: "Writing answer", direct_answer: "Answering", cache_hit: "From cache ⚡",
};

export default function ChatBox({ documentId }: { documentId?: string }) {
    const [question, setQuestion] = useState("");
    const { ask, answer, stages, citations, status } = useAgentStream();

    function submit() {
        if (question.trim() && status !== "streaming") ask(question, documentId);
    }

    return (
        <div className="rounded-xl border p-6 space-y-4">
            {/* input */}
            <div className="flex gap-2">
                <input
                    value={question}
                    onChange={(e) => setQuestion(e.target.value)}
                    onKeyDown={(e) => e.key === "Enter" && submit()}
                    placeholder="Ask about your documents…"
                    className="flex-1 rounded-lg border px-3 py-2"
                />
                <button
                    onClick={submit}
                    disabled={status === "streaming"}
                    className="rounded-lg bg-black text-white px-4 py-2 disabled:opacity-50"
                >
                    {status === "streaming" ? "Thinking…" : "Ask"}
                </button>
            </div>

            {/* stage pills — agent ki live soch */}
            {stages.length > 0 && (
                <div className="flex flex-wrap gap-2">
                    {stages.map((s, i) => (
                        <span key={i}
                            className={`text-xs rounded-full border px-2 py-1 ${i === stages.length - 1 && status === "streaming"
                                ? "border-amber-500 text-amber-600 animate-pulse"
                                : "border-green-500 text-green-600"
                                }`}>
                            {STAGE_LABELS[s] ?? s} {i < stages.length - 1 || status !== "streaming" ? "✓" : "…"}
                        </span>
                    ))}
                </div>
            )}

            {/* streaming answer */}
            {answer && (
                <div className="whitespace-pre-wrap rounded-lg bg-gray-50 p-4 text-black text-sm leading-relaxed">
                    {answer}
                    {status === "streaming" && <span className="animate-pulse">▍</span>}
                </div>
            )}

            {status === "error" && (
                <p className="text-sm text-red-600">Kuch galat ho gaya — dobara try karo.</p>
            )}

            {/* citations */}
            {status === "done" && citations.length > 0 && (
                <div className="space-y-2">
                    <h3 className="text-sm font-semibold">Sources</h3>
                    {citations.map((c, i) => (
                        <div key={i} className="rounded-lg border p-3 text-xs">
                            <div className="font-medium">
                                [{i + 1}] {c.filename ?? "unknown"}
                                {c.chunk_index != null && ` · chunk ${c.chunk_index}`}
                                {" · "}score {c.score.toFixed(2)}
                            </div>
                            <p className="mt-1 text-gray-600 line-clamp-3">{c.text}</p>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
