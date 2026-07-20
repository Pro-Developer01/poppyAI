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
exports.QueryController = void 0;
const common_1 = require("@nestjs/common");
let QueryController = class QueryController {
    async query(body) {
        const res = await fetch(`${process.env.WORKER_URL}/query`, {
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
    async stream(body, res) {
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
        const reader = upstream.body.getReader();
        const pump = async () => {
            const { done, value } = await reader.read();
            if (done)
                return res.end();
            res.write(Buffer.from(value));
            return pump();
        };
        await pump().catch(() => res.end());
    }
};
exports.QueryController = QueryController;
__decorate([
    (0, common_1.Post)('query'),
    __param(0, (0, common_1.Body)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object]),
    __metadata("design:returntype", Promise)
], QueryController.prototype, "query", null);
__decorate([
    (0, common_1.Post)('query/stream'),
    __param(0, (0, common_1.Body)()),
    __param(1, (0, common_1.Res)()),
    __metadata("design:type", Function),
    __metadata("design:paramtypes", [Object, Object]),
    __metadata("design:returntype", Promise)
], QueryController.prototype, "stream", null);
exports.QueryController = QueryController = __decorate([
    (0, common_1.Controller)()
], QueryController);
//# sourceMappingURL=query.controller.js.map