// apps/web/src/app/page.tsx
"use client";

import { useState } from "react";
import UploadCard from "./components/UploadCard";
import ChatBox from "./components/ChatBox";

export default function Home() {
  const [documentId, setDocumentId] = useState<string | undefined>();

  return (
    <main className="mx-auto max-w-2xl p-6 space-y-6">
      <h1 className="text-2xl font-bold">📄 Document Intelligence</h1>
      <UploadCard onReady={setDocumentId} />
      <ChatBox documentId={documentId} />
    </main>
  );
}
