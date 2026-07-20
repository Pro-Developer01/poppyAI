// apps/web/src/hooks/useAgentStream.ts
"use client";

import { useState, useCallback } from "react";
import type { Citation } from "../lib/api";

export type StreamStatus = "idle" | "streaming" | "done" | "error";

export function useAgentStream() {
    const [answer, setAnswer] = useState("");
    const [stages, setStages] = useState<string[]>([]);
    const [citations, setCitations] = useState<Citation[]>([]);
    const [status, setStatus] = useState<StreamStatus>("idle");

    const ask = useCallback(async (question: string, documentId?: string) => {
        // purana result saaf karo
        setAnswer(""); setStages([]); setCitations([]); setStatus("streaming");

        try {
            const res = await fetch("/api/query/stream", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ question, documentId }),
            });
            if (!res.ok || !res.body) throw new Error(`Stream failed: ${res.status}`);

            const reader = res.body.getReader();
            const decoder = new TextDecoder();
            let buffer = "";

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });

                // SSE messages "\n\n" (khaali line) se alag hote hain
                const messages = buffer.split("\n\n");
                buffer = messages.pop() ?? "";   // aakhri (shayad adhoora) wapas buffer mein

                for (const msg of messages) {
                    let event = "message";
                    let data = "";
                    for (const line of msg.split("\n")) {
                        if (line.startsWith("event: ")) event = line.slice(7).trim();
                        if (line.startsWith("data: ")) data = line.slice(6);
                    }
                    if (!data) continue;
                    const payload = JSON.parse(data);

                    if (event === "stage") setStages((s) => [...s, payload.node]);
                    if (event === "citations") setCitations(payload);
                    if (event === "token") setAnswer((a) => a + payload.t);
                    if (event === "done") setStatus("done");
                }
            }
            setStatus((s) => (s === "streaming" ? "done" : s));
        } catch {
            setStatus("error");
        }
    }, []);

    return { ask, answer, stages, citations, status };
}