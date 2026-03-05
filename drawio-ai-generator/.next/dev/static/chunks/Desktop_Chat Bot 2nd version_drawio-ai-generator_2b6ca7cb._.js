(globalThis.TURBOPACK || (globalThis.TURBOPACK = [])).push([typeof document === "object" ? document.currentScript : undefined,
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/components/DiagramPreview.tsx [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "default",
    ()=>DiagramPreview
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/node_modules/next/dist/compiled/react/jsx-dev-runtime.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$react$2d$drawio$2f$dist$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/node_modules/react-drawio/dist/index.js [app-client] (ecmascript)");
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$stores$2f$diagram$2d$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/stores/diagram-store.ts [app-client] (ecmascript)");
;
var _s = __turbopack_context__.k.signature();
"use client";
;
;
;
function DiagramPreview() {
    _s();
    const drawioRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const { currentXml } = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$stores$2f$diagram$2d$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useDiagramStore"])();
    const prevXmlRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])("");
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "DiagramPreview.useEffect": ()=>{
            if (currentXml && currentXml !== prevXmlRef.current && drawioRef.current) {
                prevXmlRef.current = currentXml;
                // Load XML into draw.io iframe
                const action = {
                    action: "load",
                    xml: currentXml,
                    autosave: 0
                };
                // Access the iframe and post the message
                const iframe = document.querySelector('iframe[src*="embed.diagrams.net"]');
                if (iframe?.contentWindow) {
                    iframe.contentWindow.postMessage(JSON.stringify(action), "*");
                }
            }
        }
    }["DiagramPreview.useEffect"], [
        currentXml
    ]);
    return /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])("div", {
        className: "h-full w-full",
        children: /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$jsx$2d$dev$2d$runtime$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["jsxDEV"])(__TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$react$2d$drawio$2f$dist$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["DrawIoEmbed"], {
            ref: drawioRef,
            xml: currentXml || undefined,
            configuration: {
                defaultFonts: []
            },
            urlParameters: {
                spin: true,
                libraries: true,
                saveAndExit: false,
                noSaveBtn: true,
                noExitBtn: true
            }
        }, void 0, false, {
            fileName: "[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/components/DiagramPreview.tsx",
            lineNumber: 33,
            columnNumber: 7
        }, this)
    }, void 0, false, {
        fileName: "[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/components/DiagramPreview.tsx",
        lineNumber: 32,
        columnNumber: 5
    }, this);
}
_s(DiagramPreview, "PcSTV0YFIpUNsqMHZKQqywc9JdQ=", false, function() {
    return [
        __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$app$2f$stores$2f$diagram$2d$store$2e$ts__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useDiagramStore"]
    ];
});
_c = DiagramPreview;
var _c;
__turbopack_context__.k.register(_c, "DiagramPreview");
if (typeof globalThis.$RefreshHelpers$ === 'object' && globalThis.$RefreshHelpers !== null) {
    __turbopack_context__.k.registerExports(__turbopack_context__.m, globalThis.$RefreshHelpers$);
}
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/components/DiagramPreview.tsx [app-client] (ecmascript, next/dynamic entry)", ((__turbopack_context__) => {

__turbopack_context__.n(__turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/app/components/DiagramPreview.tsx [app-client] (ecmascript)"));
}),
"[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/node_modules/react-drawio/dist/index.js [app-client] (ecmascript)", ((__turbopack_context__) => {
"use strict";

__turbopack_context__.s([
    "DrawIoEmbed",
    ()=>DrawIoEmbed
]);
var __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__ = __turbopack_context__.i("[project]/Desktop/Chat Bot 2nd version/drawio-ai-generator/node_modules/next/dist/compiled/react/index.js [app-client] (ecmascript)");
;
const getEmbedUrl = (baseUrl, urlParameters, addConfiguration)=>{
    const url = new URL(baseUrl ?? 'https://embed.diagrams.net');
    const urlSearchParams = new URLSearchParams();
    urlSearchParams.append('embed', '1');
    urlSearchParams.append('proto', 'json');
    if (addConfiguration) {
        urlSearchParams.append('configure', '1');
    }
    if (urlParameters) {
        Object.keys(urlParameters).forEach((key)=>{
            const value = urlParameters[key];
            if (value !== undefined) {
                if (typeof value === 'boolean') {
                    urlSearchParams.append(key, value ? '1' : '0');
                } else {
                    urlSearchParams.append(key, value.toString());
                }
            }
        });
    }
    url.search = urlSearchParams.toString();
    return url.toString();
};
function handleEvent(event, handlers, baseUrl) {
    if (!event.origin.includes('embed.diagrams.net') && baseUrl && !baseUrl.includes(event.origin) && !event.origin.includes(baseUrl)) {
        return;
    }
    try {
        const data = JSON.parse(event.data);
        if (data.event in handlers) {
            const handler = handlers[data.event];
            if (handler) {
                // @ts-ignore Not sure how to fix for now
                handler(data);
            }
        }
    } catch  {
    //
    }
}
const useActions = (iframeRef)=>{
    const sendAction = (action, data)=>{
        iframeRef.current?.contentWindow?.postMessage(JSON.stringify({
            action,
            ...data
        }), '*');
    };
    /**
   * Load the contents of a diagram
   */ const load = (data)=>{
        sendAction('load', data);
    };
    const configure = (data)=>{
        sendAction('configure', data);
    };
    /**
   * Merge the contents of the given XML into the current file
   */ const merge = (data)=>{
        sendAction('merge', data);
    };
    /**
   * Display a dialog in the editor window
   */ const dialog = (data)=>{
        sendAction('dialog', data);
    };
    /**
   * Display a prompt in the editor window
   */ const prompt = (data)=>{
        sendAction('prompt', data);
    };
    /**
   * Show the template dialog
   */ const template = (data)=>{
        sendAction('template', data);
    };
    /**
   * Runs an array of layouts using the same format as Arrange > Layout > Apply.
   */ const layout = (data)=>{
        sendAction('layout', data);
    };
    /**
   * Show a draft dialog
   */ const draft = (data)=>{
        sendAction('draft', data);
    };
    /**
   * Display a message in the status bar
   */ const status = (data)=>{
        sendAction('status', data);
    };
    /**
   * Display a spinner with a message or hide the current spinner if show is set to false
   */ const spinner = (data)=>{
        sendAction('spinner', data);
    };
    const exportDiagram = (data)=>{
        sendAction('export', data);
    };
    return {
        load,
        configure,
        merge,
        dialog,
        prompt,
        template,
        layout,
        draft,
        status,
        spinner,
        exportDiagram
    };
};
const DrawIoEmbed = /*#__PURE__*/ (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["forwardRef"])((props, ref)=>{
    const { autosave = false, baseUrl, urlParameters, configuration, xml, csv, exportFormat, onAutoSave, onSave, onClose, onLoad, onConfigure, onDraft, onExport, onMerge, onPrompt, onTemplate } = props;
    const iframeRef = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useRef"])(null);
    const action = useActions(iframeRef);
    const iframeUrl = getEmbedUrl(baseUrl, urlParameters, !!configuration);
    const [isInitialized, setIsInitialized] = (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useState"])(false);
    const messageHandler = (evt)=>{
        handleEvent(evt, {
            init: ()=>{
                setIsInitialized(true);
            },
            load: (data)=>{
                if (onLoad) {
                    onLoad(data);
                }
            },
            configure: (data)=>{
                if (configuration) {
                    action.configure({
                        config: configuration
                    });
                }
                if (onConfigure) {
                    onConfigure(data);
                }
            },
            autosave: (data)=>{
                if (onAutoSave) {
                    onAutoSave(data);
                }
            },
            save: (data)=>{
                action.exportDiagram({
                    format: exportFormat || 'xmlsvg',
                    // @ts-ignore not allowed normally, but only for internal use
                    exit: data.exit,
                    parentEvent: 'save'
                });
            },
            exit: (data)=>{
                if (onClose) {
                    onClose(data);
                }
            },
            draft: (data)=>{
                if (onDraft) {
                    onDraft(data);
                }
            },
            export: (data)=>{
                if (onSave) {
                    onSave({
                        event: 'save',
                        xml: data.data,
                        parentEvent: data.message.parentEvent || 'export'
                    });
                }
                if (onExport) {
                    onExport(data);
                }
                // @ts-ignore not allowed normally, but only for internal use
                if (data.message.exit && onClose) {
                    onClose({
                        event: 'exit',
                        modified: true,
                        parentEvent: data.message.parentEvent || 'export'
                    });
                }
            },
            merge: (data)=>{
                if (onMerge) {
                    onMerge(data);
                }
            },
            prompt: (data)=>{
                if (onPrompt) {
                    onPrompt(data);
                }
            },
            template: (data)=>{
                if (onTemplate) {
                    onTemplate(data);
                }
            }
        }, baseUrl);
    };
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useImperativeHandle"])(ref, {
        "DrawIoEmbed.useImperativeHandle": ()=>({
                ...action
            })
    }["DrawIoEmbed.useImperativeHandle"], []);
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "DrawIoEmbed.useEffect": ()=>{
            let loadObject = {};
            if (isInitialized) {
                if (xml) {
                    if (exportFormat === 'xmlpng') {
                        loadObject = {
                            xmlpng: xml
                        };
                    } else {
                        loadObject = {
                            xml
                        };
                    }
                } else if (csv) {
                    loadObject = {
                        descriptor: {
                            format: 'csv',
                            data: csv
                        }
                    };
                } else {
                    loadObject = {
                        xml: ''
                    };
                }
                loadObject = {
                    ...loadObject,
                    autosave: autosave
                };
                action.load(loadObject);
            }
        }
    }["DrawIoEmbed.useEffect"], [
        isInitialized,
        xml,
        csv,
        autosave
    ]);
    // Initial load
    (0, __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["useEffect"])({
        "DrawIoEmbed.useEffect": ()=>{
            window.addEventListener('message', messageHandler);
            return ({
                "DrawIoEmbed.useEffect": ()=>{
                    window.removeEventListener('message', messageHandler);
                }
            })["DrawIoEmbed.useEffect"];
        }
    }["DrawIoEmbed.useEffect"], []);
    return /*#__PURE__*/ __TURBOPACK__imported__module__$5b$project$5d2f$Desktop$2f$Chat__Bot__2nd__version$2f$drawio$2d$ai$2d$generator$2f$node_modules$2f$next$2f$dist$2f$compiled$2f$react$2f$index$2e$js__$5b$app$2d$client$5d$__$28$ecmascript$29$__["default"].createElement("iframe", {
        className: "diagrams-iframe",
        src: iframeUrl,
        ref: iframeRef,
        allow: "clipboard-read; clipboard-write",
        title: "Diagrams.net",
        style: {
            width: '100%',
            height: '100%',
            minWidth: '400px',
            minHeight: '400px',
            border: 'none'
        }
    });
});
;
 //# sourceMappingURL=index.js.map
}),
]);

//# sourceMappingURL=Desktop_Chat%20Bot%202nd%20version_drawio-ai-generator_2b6ca7cb._.js.map