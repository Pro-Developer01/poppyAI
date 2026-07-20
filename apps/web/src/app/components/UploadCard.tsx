"use client";

import { useState, useRef, useEffect } from "react";
import { uploadDocument, getJob, type Job } from "../lib/api";

export default function UploadCard({ onReady }: { onReady?: (documentId: string) => void }) {
    const [job, setJob] = useState<Job | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [busy, setBusy] = useState(false);
    const timer = useRef<ReturnType<typeof setInterval> | null>(null);

    // component hate/band ho to polling bhi band ho
    useEffect(() => {
        return () => { if (timer.current) clearInterval(timer.current); };
    }, []);

    async function handleFile(file: File) {
        setBusy(true);
        setError(null);
        try {
            const { jobId, documentId } = await uploadDocument(file);
            setJob({ id: jobId, status: "processing", filename: file.name });

            timer.current = setInterval(async () => {
                const j = await getJob(jobId);
                setJob(j);
                if (j.status !== "processing") {
                    clearInterval(timer.current!);
                    if (j.status === "done") onReady?.(documentId);
                }
            }, 2000);
        } catch (e) {
            setError(e instanceof Error ? e.message : "Upload failed");
        } finally {
            setBusy(false);
        }
    }

    return (
        <div className="rounded-xl border p-6 space-y-4">
            <h2 className="font-semibold text-lg">Upload a document</h2>

            <input
                type="file"
                accept=".pdf,.csv,.xlsx,.txt"
                disabled={busy}
                onChange={(e) => e.target.files?.[0] && handleFile(e.target.files[0])}
                className="block w-full text-sm"
            />

            {job && (
                <div className="text-sm">
                    <span className="font-medium">{job.filename}</span>{" — "}
                    {job.status === "processing" && <span className="text-amber-600">processing… ⏳</span>}
                    {job.status === "done" && <span className="text-green-600">done ✓ (ask away!)</span>}
                    {job.status === "failed" && <span className="text-red-600">failed: {job.error}</span>}
                </div>
            )}

            {error && <p className="text-sm text-red-600">{error}</p>}
        </div>
    );
}