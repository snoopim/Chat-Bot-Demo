module.exports = [
"[externals]/next/dist/compiled/next-server/app-route-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-route-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-route-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/@opentelemetry/api [external] (next/dist/compiled/@opentelemetry/api, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/@opentelemetry/api", () => require("next/dist/compiled/@opentelemetry/api"));

module.exports = mod;
}),
"[externals]/next/dist/compiled/next-server/app-page-turbo.runtime.dev.js [external] (next/dist/compiled/next-server/app-page-turbo.runtime.dev.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js", () => require("next/dist/compiled/next-server/app-page-turbo.runtime.dev.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-unit-async-storage.external.js [external] (next/dist/server/app-render/work-unit-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-unit-async-storage.external.js", () => require("next/dist/server/app-render/work-unit-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/work-async-storage.external.js [external] (next/dist/server/app-render/work-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/work-async-storage.external.js", () => require("next/dist/server/app-render/work-async-storage.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/shared/lib/no-fallback-error.external.js [external] (next/dist/shared/lib/no-fallback-error.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/shared/lib/no-fallback-error.external.js", () => require("next/dist/shared/lib/no-fallback-error.external.js"));

module.exports = mod;
}),
"[externals]/next/dist/server/app-render/after-task-async-storage.external.js [external] (next/dist/server/app-render/after-task-async-storage.external.js, cjs)", ((__turbopack_context__, module, exports) => {

const mod = __turbopack_context__.x("next/dist/server/app-render/after-task-async-storage.external.js", () => require("next/dist/server/app-render/after-task-async-storage.external.js"));

module.exports = mod;
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/openai-client.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "chatCompletion",
    ()=>chatCompletion,
    "createOpenAIClient",
    ()=>createOpenAIClient,
    "listModels",
    ()=>listModels
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$openai$2f$index$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$locals$3e$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/node_modules/openai/index.mjs [app-route] (ecmascript) <locals>");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$openai$2f$client$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$export__OpenAI__as__default$3e$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/node_modules/openai/client.mjs [app-route] (ecmascript) <export OpenAI as default>");
;
function createOpenAIClient(apiKey) {
    return new __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$openai$2f$client$2e$mjs__$5b$app$2d$route$5d$__$28$ecmascript$29$__$3c$export__OpenAI__as__default$3e$__["default"]({
        apiKey
    });
}
async function chatCompletion(client, model, systemPrompt, userPrompt, jsonMode = true) {
    // o-series reasoning models don't support temperature or system role
    const isReasoningModel = /^o[0-9]/.test(model);
    const messages = isReasoningModel ? [
        {
            role: "user",
            content: `${systemPrompt}\n\n${userPrompt}`
        }
    ] : [
        {
            role: "system",
            content: systemPrompt
        },
        {
            role: "user",
            content: userPrompt
        }
    ];
    const response = await client.chat.completions.create({
        model,
        messages,
        ...jsonMode && !isReasoningModel && {
            response_format: {
                type: "json_object"
            }
        },
        ...!isReasoningModel && {
            temperature: 0.3
        }
    });
    return response.choices[0]?.message?.content ?? "";
}
async function listModels(apiKey) {
    const client = createOpenAIClient(apiKey);
    const list = await client.models.list();
    const models = [];
    for await (const model of list){
        models.push(model.id);
    }
    // Filter to chat-capable models and sort
    const chatModels = models.filter((id)=>id.startsWith("gpt-") || id.startsWith("o1") || id.startsWith("o3") || id.startsWith("o4")).sort();
    return chatModels;
}
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/api/models/route.ts [app-route] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "POST",
    ()=>POST
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/node_modules/next/server.js [app-route] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$openai$2d$client$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/lib/openai-client.ts [app-route] (ecmascript)");
;
;
async function POST(req) {
    try {
        const { apiKey } = await req.json();
        if (!apiKey) {
            return __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
                error: "API key is required"
            }, {
                status: 400
            });
        }
        const models = await (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$lib$2f$openai$2d$client$2e$ts__$5b$app$2d$route$5d$__$28$ecmascript$29$__["listModels"])(apiKey);
        return __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
            models
        });
    } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to fetch models";
        return __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$server$2e$js__$5b$app$2d$route$5d$__$28$ecmascript$29$__["NextResponse"].json({
            error: message
        }, {
            status: 500
        });
    }
}
}),
];

//# sourceMappingURL=%5Broot-of-the-server%5D__1e99ac01._.js.map