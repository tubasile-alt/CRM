#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
BUILD_DIR="$SCRIPT_DIR/.build/release"
APP_DIR="$SCRIPT_DIR/dist/CRM Notch.app"
CONTENTS="$APP_DIR/Contents"

cd "$SCRIPT_DIR"
swift build -c release

mkdir -p "$CONTENTS/MacOS" "$CONTENTS/Resources"
cp "$BUILD_DIR/CRMNotch" "$CONTENTS/MacOS/CRMNotch"
cp "$SCRIPT_DIR/Info.plist" "$CONTENTS/Info.plist"
codesign --force --deep --sign - "$APP_DIR"

print "App criado em: $APP_DIR"
