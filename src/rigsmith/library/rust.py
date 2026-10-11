"""Rust."""

from rigsmith.backends import Script
from rigsmith.library._util import ext, tool
from rigsmith.model import Artifact, Snippet

Artifact(
    id="rustup",
    help="rustup: the official Rust toolchain installer (rustc, cargo, clippy, rustfmt) into ~/.cargo.",
    sources=[
        Script(
            "rustup",
            install_cmd="curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --no-modify-path",
            check_cmd='test -x "$HOME/.cargo/bin/rustup"',
            remove_cmd='"$HOME/.cargo/bin/rustup" self uninstall -y',
        )
    ],
    shell=Snippet("rustup.zsh", 10),
)
tool("bacon", "Background Rust checker: re-runs check/clippy/test as you save.")
tool("cargo-nextest", "Faster, nicer test runner for cargo: `cargo nextest run`.")
tool("sccache", "Compiler cache for Rust (and C/C++) builds.")
ext("rust-analyzer-ext", "rust-lang.rust-analyzer", "Rust in VS Code: completion, inlay hints, refactors.")
