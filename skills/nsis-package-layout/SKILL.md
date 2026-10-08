---
name: nsis-package-layout
description: Lays out an NSIS plug-in, header or other contrib download (zip, installer, loose files) as a release-package repository, per the NSIS Package Layout Specification. Use when importing, migrating or repackaging an NSIS plug-in or contrib archive.
---

The target is the [spec](https://github.com/nsis-dev/release-package/blob/main/SPEC.md): the repository root laid out like NSISDIR, built and released by the `nsis-dev/release-package` action. Read the spec before step 3. Scripts live in `scripts/` beside this file. Downloads are **untrusted**: extract each into its own new, empty directory, and never run anything that comes out of one.

Whenever a decision rests on a guess (which file is the license, which DLL is the plug-in, which targets build), **ask the user** and wait. A wrong guess ships in a release.

## 1. Unpack

Unpack every archive and installer (zip, 7z, rar, cab, NSIS installer, MSI) with `7zz x -o<new dir> <file>`, recursing into what comes out.

- An NSIS installer unpacks to `$INSTDIR`-style folders plus, often, a decompiled `[NSIS].nsi`. Its `SetOutPath`/`File` lines say where each file was meant to go: use them as the mapping in step 3.
- `$PLUGINSDIR`, the uninstaller and the installer's own stock plug-ins (System, nsDialogs, …) are not the Package: drop them.
- Strip single-folder wrappers.

Done when the tree holds no `.zip`/`.7z`/`.exe` installer left to open, except `.exe` files an example needs.

## 2. Identify

- **Kind**: Plugin Package (sources, or a DLL whose source is lost: prebuilt) or Data Package (headers, graphics, language files).
- **Name**: the DLL basename, matching `[A-Za-z0-9_-]+`, in the author's casing (folder names under `Docs/` or `Contrib/` often carry it better than a lowercase DLL). Ask when there are several plug-in DLLs, when the name collides with a stock NSIS plug-in (`NSISdl`, `System`, `nsDialogs`, `inetc`…), or when the DLL is a fork shipped under another plug-in's name. A rename needs a README note telling scripts the new `Name::Function`.
- **Repo**: `plugin-<name lowercased>` for a plug-in; ask for a Data Package.

Done when kind, name and repo are settled.

## 3. Move into place

| What                                                                                                                                             | Where                                                          |
| ------------------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------- |
| Sources, headers, `.def`, project files (`.dsp`, `.vcxproj`, `.dpr`, `Cargo.toml`)                                                               | `Contrib/<name>/`, keeping their relative layout               |
| `.nsh` headers                                                                                                                                   | `Include/`                                                     |
| `.nsi` scripts and the files they reference                                                                                                      | `Examples/<name>/`                                             |
| Docs and the upstream readme                                                                                                                     | `Docs/<name>/`                                                 |
| The Package's own license                                                                                                                        | top level                                                      |
| Data files (graphics, language files)                                                                                                            | `Contrib/<subfolder>/` as NSIS ships them                      |
| DLL, with source                                                                                                                                 | delete                                                         |
| DLL, source lost                                                                                                                                 | `Plugins/<target>/<name>.dll` (target from its folder, or ask) |
| Build output (`Debug/`, `Release/`, `.obj`, `.pdb`, `.ncb`, `.suo`, `.aps`, `.user`, `.lib`), OS clutter (`.DS_Store`, `Thumbs.db`, `__MACOSX/`) | delete                                                         |

- A license inside a vendored library's folder (zlib, …) stays with that library.
- If a source includes `exdll.h` and no such file is in the tree, copy `assets/exdll.h` beside the sources and point the include at it.
- A third-party runtime DLL (`python23.dll`…) can't stay: ask.

Done when every extracted file has a destination or was deliberately dropped, and nothing outside the table's destinations remains except dot-folders.

## 4. Licenses

The spec only recognises names whose stem is `LICENSE`, `LICENCE`, `COPYING` or `UNLICENSE`. Rename a license with any other name (`GPL.txt`, `MIT.txt`, `copyright.txt`, `Lizenz.txt`) to `LICENSE.txt`, or `LICENSE-<SPDX>.txt` when there are several. Read it first: a readme with a license paragraph is not a license file. Ask before inventing one; with none, the workflow gets `strict: false`.

## 5. Scaffold

From the repository root:

```bash
python3 <skill>/scripts/scaffold.py <name> --sources <glob>... | --project <path> [--targets <list>]
```

It writes `README.md`, `.gitattributes` and `.github/workflows/ci.yml`, reading the license, usage guide, headers and binary types from the tree; `Plugins/` makes it prebuilt, no sources and no project a Data Package.

- **Sources**: the files the MSVC project compiles (`SOURCE=` in `.dsp`, `ClCompile` in `.vcxproj`), else every `.c`/`.cpp`/`.rc` under `Contrib/<name>/` except `pluginapi.c`. **Project**: the `.dpr`/`.lpr` or `Cargo.toml`.
- **Targets**: omit for all three. Code that uses `char*`/`LPSTR` and no `TCHAR` is `x86-ansi` only; code that is Unicode-only is `x86-unicode,amd64-unicode`.
- Then edit the README's About paragraph where the template is wrong: a fork, a rename, a source other than the NSIS wiki, an author who maintains it.

## 6. Validate

```bash
git clone --depth 1 https://github.com/nsis-dev/release-package <tmp>
NAME=<name> TOOLCHAIN=<none|prebuilt, else omit> STRICT=<false without a license> python3 <tmp>/scripts/check_layout.py
```

Done when it reports 0 errors. Hand the user the commands to `git init`, commit, create the repo and push; the first CI run settles the targets: narrow them if one fails.
