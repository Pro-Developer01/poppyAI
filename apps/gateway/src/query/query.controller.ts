import { Controller, Post, Body } from '@nestjs/common';

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
}