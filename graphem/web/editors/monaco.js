import * as monaco from "monaco-editor";
import EditorWorker from "monaco-editor/editor/editor.worker?worker";


self.MonacoEnvironment = {
    getWorker() {
        return new EditorWorker();
    }
}

export function createEditor(container, code) {
    const view = monaco.editor.create(container, {
        value: code,
        language: "python",
        theme: "vs-dark",
        automaticLayout: true,
        tabSize: 4,
        insertSpaces: true,
        minimap: { enabled: false }
    });

    return {
        getValue: () => view.getValue(),
        destroy: () => {
            const model = view.getModel();
            view.dispose();
            model?.dispose();
        }
    }
}
