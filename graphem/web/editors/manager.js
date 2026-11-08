const STORAGE_KEY = "graphem.editor";

export class EditorManager {
    constructor(container, initialCode) {
        this.container = container;
        this.initialCode = initialCode;
        this.editor = null;
        this.type = localStorage.getItem(STORAGE_KEY) ?? "codemirror";
    }

    getValue() {
        return this.editor?.getValue() ?? "";
    }

    async switchEditor(editorType) {
        this.container.setAttribute("aria-busy", "true");
        if  (this.container.contains(document.activeElement)) {
            document.activeElement.blur();
        }

        try {
            const code = this.editor?.getValue() ?? this.initialCode;

            const module = editorType === "monaco"
                ? await import(`./monaco.js`)
                : await import(`./codemirror.js`);

            this.destroyEditor();
            this.container.replaceChildren();

            this.editor = await module.createEditor(this.container, code);;
            this.type = editorType;

            localStorage.setItem(STORAGE_KEY, editorType);
            console.log("Code editor picked: ", editorType);
        } finally {
            this.container.removeAttribute("aria-busy");
        }
    }

    destroyEditor() {
        this.editor?.destroy();
        this.editor = null;
    }
}
