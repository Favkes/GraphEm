#!/usr/bin/env bash
set -euo pipefail

wheel=$(ls -t dist/graphem-*.whl | head -n 1)
target="graphem/web/public/dist"

mkdir -p "$target"
rm -f "$target"/graphem-*.whl

cp "$wheel" "$target"

printf '{"filename":"%s"}\n' "${wheel##*/}" > "$target/wheel.json"