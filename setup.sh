#!/usr/bin/env bash
set -euo pipefail

# ─────────────────────────────────────────────────────────────
# Deep Research — CachyOS / Arch Linux Setup
# ─────────────────────────────────────────────────────────────

APP_NAME="deep-research"
APP_DIR="$(cd "$(dirname "$0")" && pwd)"
VENV_DIR="$APP_DIR/.venv"
BACKEND_DIR="$APP_DIR/backend"

echo "==> Setting up Deep Research for CachyOS..."

# ── 1. System dependencies ───────────────────────────────────
echo "--> Checking system dependencies..."
MISSING=""
for pkg in webkit2gtk-4.1 python nodejs npm rustup; do
    if ! pacman -Q "$pkg" &>/dev/null; then
        MISSING="$MISSING $pkg"
    fi
done

if [ -n "$MISSING" ]; then
    echo "==> Installing missing system packages:$MISSING"
    sudo pacman -S --noconfirm $MISSING
fi

# ── 2. Python virtual environment ────────────────────────────
echo "--> Setting up Python virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
pip install --upgrade pip --quiet
pip install -r "$BACKEND_DIR/requirements.txt" --quiet
deactivate
echo "     Python dependencies installed."

# ── 3. npm dependencies ─────────────────────────────────────
echo "--> Installing Node.js dependencies..."
cd "$APP_DIR"
npm install --silent 2>/dev/null || npm install
echo "     Node.js dependencies installed."

# ── 4. Build Tauri app (release) ─────────────────────────────
echo "--> Building Tauri application (this may take a while)..."
cd "$APP_DIR"
npx tauri build --bundles deb,appimage 2>&1 | tail -5

# ── 5. Desktop entry ─────────────────────────────────────────
echo "--> Creating desktop entry..."
DESKTOP_FILE="$HOME/.local/share/applications/deep-research.desktop"
mkdir -p "$(dirname "$DESKTOP_FILE")"

if [ -f "$APP_DIR/src-tauri/target/release/deep-research" ]; then
    BINARY="$APP_DIR/src-tauri/target/release/deep-research"
elif [ -f "$APP_DIR/src-tauri/target/release/Deep Research" ]; then
    BINARY="$APP_DIR/src-tauri/target/release/Deep Research"
else
    BINARY="$APP_DIR/src-tauri/target/release/deep-research"
fi

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Name=Deep Research
Comment=Autonomous AI-powered web research tool
Exec=$BINARY
Icon=$APP_DIR/src-tauri/icons/128x128.png
Terminal=false
Type=Application
Categories=Utility;Science;AI;
StartupNotify=true
EOF

chmod +x "$DESKTOP_FILE"

# ── 6. Shell aliases ─────────────────────────────────────────
ALIAS_CMD="alias deepresearch='$BINARY'"

for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
    if [ -f "$rc" ]; then
        if ! grep -q "alias deepresearch=" "$rc" 2>/dev/null; then
            echo "$ALIAS_CMD" >> "$rc"
            echo "     Added alias to $rc"
        fi
    fi
done

if command -v fish &>/dev/null; then
    FISH_CONFIG="$HOME/.config/fish/config.fish"
    if [ -f "$FISH_CONFIG" ]; then
        if ! grep -q "alias deepresearch=" "$FISH_CONFIG" 2>/dev/null; then
            mkdir -p "$(dirname "$FISH_CONFIG")"
            echo "alias deepresearch='$BINARY'" >> "$FISH_CONFIG"
            echo "     Added alias to $FISH_CONFIG"
        fi
    fi
fi

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║          Deep Research — Setup Complete                 ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Launch:  deepresearch                                  ║"
echo "║  The app automatically uses .venv/bin/python3 if present  ║"
echo "║                                                         ║"
echo "║  First run:                                             ║"
echo "║  1. Open Settings → LLM Provider                        ║"
echo "║  2. Select OpenRouter / LM Studio / OpenCode Proxy      ║"
echo "║  3. Enter API key (if needed) → Fetch Models → Select   ║"
echo "║  4. Save Settings                                       ║"
echo "║  5. Enter a topic and click Research                    ║"
echo "╚══════════════════════════════════════════════════════════╝"
