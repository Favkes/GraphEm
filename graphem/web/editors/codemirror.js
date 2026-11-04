import { EditorView, basicSetup } from "codemirror";
import { python } from "@codemirror/lang-python";
import { keymap } from "@codemirror/view";
import { indentWithTab } from "@codemirror/commands";
import { darcula } from "@uiw/codemirror-theme-darcula";


export function createEditor(container, code) {
    const view = new EditorView({
        doc: code,
        parent: container,
        extensions: [
            basicSetup,
            python(),
            darcula,
            keymap.of([indentWithTab])
        ]
    });

    return {
        getValue: () => view.state.doc.toString(),
        destroy: () => view.destroy()
    }
}
