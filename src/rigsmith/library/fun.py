"""Fun. Focus killers, tagged `fun` (the questionnaire asks)."""

from rigsmith.library._util import ext, snippet, tool

for id, about, bin in [
    ("fastfetch", "System info with a logo, fast (neofetch successor).", None),
    ("cmatrix", "The Matrix in your terminal.", None),
    ("lolcat", "Rainbow-colored output: `ls | lolcat`.", None),
    ("figlet", "ASCII-art banners.", None),
    ("cowsay", "A cow says your text.", None),
    ("pipes-sh", "Animated pipes screensaver.", "pipes.sh"),
    ("sl", "A steam locomotive, punishment for typing sl instead of ls.", None),
]:
    tool(id, about, bin=bin, tags=["fun"])
snippet("fun-aliases", "matrix, rainbow BANNER, shrug/flip/lenny (copied to the clipboard).", 70, tags=["fun"])
ext("power-mode-ext", "hoovercj.vscode-power-mode", "Explosions while you type. Seriously.", tags=["fun"])
ext("pets-ext", "tonybaloney.vscode-pets", "A pet in your editor.", tags=["fun"])
