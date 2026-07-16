export declare class JobsService {
    private pool;
    createJob(documentId: string, filename: string): Promise<string>;
    getJob(id: string): Promise<any>;
}
