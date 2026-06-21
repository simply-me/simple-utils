## v0.3.1 (2026-06-22)

### Fix

- add subprocess to handle seg fault
- **simply-env.cmd**: remove unnecessary output line
- correct simply-env.cmd name
- correct simply-env.cmd name

## v0.3.0 (2026-06-20)

### Feat

- renamed setup_env.cmd to simply_env.cmd
- add update support to setup_env.cmd

### Fix

- changed the simply.cmd to call simply_env.cmd

## v0.2.0 (2026-06-19)

### Feat

- removed redundant error messages
- changed the way arguments are passed through

## v0.1.0 (2026-06-19)

### Feat

- removed --inputs option, pdf optimization that works
- added pdf-compress support
- updated output formatting
- changed launcher to use mode
- moved to a passthrough invocation
- add min arguments check
- create the launcher framework #2
- initial commit

### Fix

- **pdf-optimizer**: fix seg fault
- removed unused files, will reimplement workflow later
- **launcher**: fix execution dir
