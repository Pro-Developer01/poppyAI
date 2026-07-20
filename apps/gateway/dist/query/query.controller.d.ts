import type { Response } from 'express';
export declare class QueryController {
    query(body: {
        question: string;
        documentId?: string;
        topK?: number;
    }): Promise<any>;
    stream(body: {
        question: string;
        documentId?: string;
        topK?: number;
    }, res: Response): Promise<void>;
}
