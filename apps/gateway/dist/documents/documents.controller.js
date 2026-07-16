"use strict";
var __decorate = (this && this.__decorate) || function (decorators, target, key, desc) {
    var c = arguments.length, r = c < 3 ? target : desc === null ? desc = Object.getOwnPropertyDescriptor(target, key) : desc, d;
    if (typeof Reflect === "object" && typeof Reflect.decorate === "function") r = Reflect.decorate(decorators, target, key, desc);
    else for (var i = decorators.length - 1; i >= 0; i--) if (d = decorators[i]) r = (c < 3 ? d(r) : c > 3 ? d(target, key, r) : d(target, key)) || r;
    return c > 3 && r && Object.defineProperty(target, key, r), r;
};
var __metadata = (this && this.__metadata) || function (k, v) {
    if (typeof Reflect === "object" && typeof Reflect.metadata === "function") return Reflect.metadata(k, v);
};
var __param = (this && this.__param) || function (paramIndex, decorator) {
    return function (target, key) { decorator(target, key, paramIndex); }
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.DocumentsController = void 0;
const common_1 = require("@nestjs/common");
const platform_express_1 = require("@nestjs/platform-express");
const multer_1 = require("multer");
const crypto_1 = require("crypto");
const path_1 = require("path");
const queue_service_1 = require("../queue/queue.service");
const jobs_service_1 = require("../jobs/jobs.service");
let DocumentsController = class DocumentsController {
    queue;
    jobs;
    constructor(queue, jobs) {
        this.queue = queue;
        this.jobs = jobs;
    }
    async upload(file) {
        const documentId = (0, crypto_1.randomUUID)();
        const jobId = await this.jobs.createJob(documentId, file.originalname);
        await this.queue.publishIngestion({
            jobId,
            documentId,
            filePath: file.path,
            filename: file.originalname,
        });
        return { jobId, documentId, status: 'processing' };
    }
    async status(id) {
        return this.jobs.getJob(id);
    }
};
exports.DocumentsController = DocumentsController;
__decorate([
    (0, common_1.Post)('documents'),
    (0, common_1.UseInterceptors)((0, platform_express_1.FileInterceptor)('file', {
        storage: (0, multer_1.diskStorage)({
            destination: process.env.UPLOAD_DIR || '/data/uploads',
            filename: (_req, file, cb) => cb(null, `${(0, crypto_1.randomUUID)()}${(0, path_1.extname)(file.originalname)}`),
        }),
    })),
    __param(0, (0, common_1.UploadedFile)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", Promise)
], DocumentsController.prototype, "upload", null);
__decorate([
    (0, common_1.Get)('jobs/:id'),
    __param(0, (0, common_1.Param)('id')),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [String]),
    __metadata("design:returntype", Promise)
], DocumentsController.prototype, "status", null);
exports.DocumentsController = DocumentsController = __decorate([
    (0, common_1.Controller)(),
    __metadata("design:paramtypes", [queue_service_1.QueueService,
        jobs_service_1.JobsService])
], DocumentsController);
//# sourceMappingURL=documents.controller.js.map