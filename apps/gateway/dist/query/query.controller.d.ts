export declare class QueryController {
    query(body: {
        question: string;
        documentId?: string;
        topK?: number;
    }): Promise<any>;
}
