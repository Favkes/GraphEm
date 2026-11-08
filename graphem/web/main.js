import { loadPyodide } from
    "https://cdn.jsdelivr.net/pyodide/v314.0.7/full/pyodide.mjs";
import { EditorManager } from "./editors/manager.js";


async function main() {
    const pyodide = await loadPyodide();
    console.log("Pyodide initialized.");

    await pyodide.loadPackage("micropip");
    const micropip = pyodide.pyimport("micropip");

    const wheelUrl = new URL(
        `${import.meta.env.BASE_URL}dist/graphem-0.1.2.4-py3-none-any.whl`, 
        window.location.origin
    ).href;
    await micropip.install(wheelUrl);
    console.log("GraphEm installed! ;)");

    const scriptOutput = document.getElementById("console-output");

    function appendOutput(text) {
        scriptOutput.textContent += text + "\n";

        const panel = scriptOutput.parentElement;
        panel.scrollTop = panel.scrollHeight;
    }
    pyodide.setStdout({
        batched: (text) => appendOutput(text)
    });
    pyodide.setStderr({
        batched: (text) => appendOutput(text)
    });
    console.log("Created script output window");


    // load example code into editor and initialize code editor
    const editor = document.getElementById("python-editor");
    const runButton = document.getElementById("run-code");
    const stopButton = document.getElementById("stop-code");

    document.addEventListener("graphem:finished", () => {
        runButton.disabled = false;
        stopButton.disabled = true;

        console.log("Process finished.");
        appendOutput("Process finished.");
    });

    const response = await fetch("./example.py");
    if (!response.ok) {
        throw new Error("Failed to load example.py");
    }

    const editorManager = new EditorManager(
        editor,
        await response.text()
    );
    await editorManager.switchEditor(editorManager.type);

    const selector = document.getElementById("editor-type");
    selector.value = editorManager.type;
    selector.addEventListener("change", async () => {
        selector.disabled = true;

        try {
            console.log("Changing code editor...");
            await editorManager.switchEditor(selector.value);
        } catch (error) {
            console.error(error);
            selector.value = editorManager.type;
        } finally {
            selector.disabled = false;
        }
    });


    document.getElementById("loading").remove();
    runButton.disabled = false;

    // run user code
    runButton.addEventListener("click", async () => {
        runButton.disabled = true;

        try {
            pyodide.globals.set("editor_source", editorManager.getValue());

            scriptOutput.textContent = "";
            runButton.disabled = true;
            stopButton.disabled = true;

            const started = await pyodide.runPythonAsync(`
import asyncio
import traceback
import sys
from js import document, Event


_started = False

try:
    compiled = compile(editor_source, "<editor>", "exec")
except SyntaxError as error:
    print("".join(traceback.format_exception_only(error)), file=sys.stderr, end="")

else:
    # kill previous task if it wasn't finished
    if "_graph_task" in globals() and not _graph_task.done():
        _graph_task.cancel()
        await asyncio.gather(_graph_task, return_exceptions=True)

    _run_scope = {}
    exec(compiled, _run_scope)

    app = _run_scope["app"]
    _graph_task = asyncio.create_task(app.run(exit_after_finish=False))


    await asyncio.sleep(0)
    _started = True

_started
            `);

            if (started) {
                stopButton.disabled = false;
            } else {
                runButton.disabled = false;
            }

        } catch (error) {
            console.error(error);
            appendOutput(String(error));
            runButton.disabled = false;
            stopButton.disabled = true;
        }
    });

    //stop current execution
    stopButton.addEventListener("click", async () => {
        stopButton.disabled = true;

        try {
            await pyodide.runPythonAsync(`
if "_graph_task" in globals() and not _graph_task.done():
    _graph_task.cancel()
    await asyncio.gather(_graph_task, return_exceptions=True)
            `);
        } catch (error) {
            console.error(error);
        } finally {
            runButton.disabled = false;
        }
    });
}

// entry point
main();
