"""Java / JVM."""

from rigsmith.backends import Brew
from rigsmith.library._util import ext, tool
from rigsmith.model import Artifact, Snippet

Artifact(
    id="openjdk",
    help="OpenJDK (latest) from Homebrew, with JAVA_HOME and PATH set.",
    sources=[Brew("openjdk")],
    shell=Snippet("openjdk.zsh", 10),
)
tool("maven", "Apache Maven build tool.", bin="mvn", requires=["openjdk"])
tool("gradle", "Gradle build tool.", requires=["openjdk"])
ext("java-ext", "vscjava.vscode-java-pack", "Java in VS Code: language server, debugger, Maven/Gradle, tests.")
