import { Controller, Post, Body, Res } from '@nestjs/common';
import type { Response } from 'express';

@Controller()
export class QueryController {
    @Post('query')
    async query(
        @Body() body: { question: string; documentId?: string; topK?: number },
    ) {
        const res = await fetch(`${process.env.WORKER_URL}/query`, {  // Node 18+ global fetch
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: body.question,
                document_id: body.documentId,
                top_k: body.topK ?? 5,
            }),
        });
        return res.json();
    }

    @Post('query/stream')
    async stream(
        @Body() body: { question: string; documentId?: string; topK?: number },
        @Res() res: Response,
    ) {
        const upstream = await fetch(`${process.env.WORKER_URL}/query/stream`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: body.question,
                document_id: body.documentId,
                top_k: body.topK ?? 5,
            }),
        });

        res.setHeader('Content-Type', 'text/event-stream');
        res.setHeader('Cache-Control', 'no-cache');
        res.setHeader('Connection', 'keep-alive');

        const reader = upstream.body!.getReader();
        const pump = async () => {
            const { done, value } = await reader.read();
            if (done) return res.end();
            res.write(Buffer.from(value));
            return pump();
        };
        await pump().catch(() => res.end());
    }
}