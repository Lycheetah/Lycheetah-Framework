# Truth Pressure Live Source Collector v0.8

This collector finds the exact live Lycheetah app files needed to wire the Truth Pressure shadow bridge into Sovereign Sol.

It searches for:

- `scoreCASCADE(...)` calls and imports;
- `truthPressure`, `reorganisationNeeded`, and related displays;
- `OnionProfile`;
- onion-engine imports and calls;
- reorganisation calls;
- CASCADE judge calls;
- AsyncStorage and likely persistence wrappers;
- likely CASCADE and Library screen paths.

It also includes project configuration such as `package.json`, the active lockfile, TypeScript configuration, and Expo configuration.

## Privacy and safety

The collector deliberately excludes:

- `.env` files;
- credentials and signing keys;
- private keys;
- local databases;
- logs;
- `node_modules`;
- build directories;
- Git internals;
- local app user data.

Every collected source file receives a SHA-256 hash.

## macOS or Linux

Place this collector anywhere, then run:

```bash
bash collect-and-zip.sh /path/to/lycheetah-mobile
```

It creates:

```text
/path/to/lycheetah-mobile/truth-pressure-live-source-extract.zip
```

## Windows PowerShell

```powershell
.\collect-and-zip.ps1 -RepoPath C:\path\to\lycheetah-mobile
```

## Node-only fallback

```bash
node collect-truth-pressure-live-source.mjs /path/to/lycheetah-mobile
```

Then compress the generated directory manually:

```text
_truth-pressure-live-source-extract
```

Upload the resulting ZIP to this conversation. The next pass will produce the verified line-level Sovereign Sol integration patch.
