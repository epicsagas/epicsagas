# Java / JVM — One-Line Install

> Key advantage: **GraalVM native-image** produces a JVM-free binary (~10ms startup).

## JDK Install

```bash
# SDKMAN (JVM ecosystem standard)
curl -s "https://get.sdkman.io" | bash
sdk install java 21-graalvm
sdk install kotlin

# mise (unified management)
mise use java@21

# Homebrew
brew install --cask temurin     # Eclipse Temurin JDK

# Windows
winget install EclipseAdoptium.Temurin.21.JDK
```

## Tool Distribution

```bash
# Fat JAR (requires JVM)
java -jar tool.jar

# Homebrew wrapper (wraps JAR)
brew install tool

# GraalVM native-image (JVM-free binary)
native-image -jar tool.jar -o tool
# → binary runs without JVM, ~10ms startup vs ~200ms JVM

# Windows (winget / Scoop)
winget install tool
scoop install tool
```

## GraalVM Native Image (GitHub Actions)

```yaml
- uses: graalvm/setup-graalvm@v1
  with:
    java-version: '21'
    distribution: 'graalvm'
- run: mvn -Pnative package          # Maven
- run: gradle nativeCompile          # Gradle
```

## Kotlin CLI

```bash
sdk install kotlin
kotlinc cli.kt -include-runtime -d tool.jar
java -jar tool.jar
# or native-image for JVM-free binary
```

## OS/Arch Support

| Method | Linux | macOS | Windows | Startup |
|--------|-------|-------|---------|---------|
| Fat JAR | ✅ | ✅ | ✅ | ~200ms |
| native-image | ✅ | ✅ | ✅ | ~10ms |
