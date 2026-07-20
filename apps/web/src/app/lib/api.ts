
export type Citation = {
    text: string;
    filename?: string;
    chunk_index?: number;
    document_id: string;
    score: number;
};

export type Job = {
    id: string;
    status: "processing" | "done" | "failed";
    filename?: string;
    error?: string | null;
};

export async function uploadDocument(file: File): Promise<{ jobId: string; documentId: string }> {
    const form = new FormData();
    form.append("file", file);
    const res = await fetch("/api/documents", { method: "POST", body: form });
    if (!res.ok) throw new Error(`Upload failed: ${res.status}`);
    return res.json();
}

export async function getJob(jobId: string): Promise<Job> {
    const res = await fetch(`/api/jobs/${jobId}`);
    if (!res.ok) throw new Error(`Status check failed: ${res.status}`);
    return res.json();
}