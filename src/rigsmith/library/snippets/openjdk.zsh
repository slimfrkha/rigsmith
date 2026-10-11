# Homebrew openjdk is keg-only: expose it explicitly.
export JAVA_HOME="$(brew --prefix openjdk 2>/dev/null)/libexec/openjdk.jdk/Contents/Home"
[[ -d $JAVA_HOME ]] || export JAVA_HOME="$(brew --prefix openjdk 2>/dev/null)/libexec"
export PATH="$(brew --prefix openjdk 2>/dev/null)/bin:$PATH"
