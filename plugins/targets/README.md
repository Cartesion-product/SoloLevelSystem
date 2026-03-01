# Target Company Plugins

This directory contains company-specific interview customizations.

## Directory Structure

Create a subdirectory for each target company:

```
targets/
  google/
    system_prompt.md   # Company-specific interview style overrides
    values.md          # Company values and culture notes
  amazon/
    system_prompt.md
    leadership_principles.md
```

## How It Works

When a user specifies a `target_company`, the PromptPluginLoader will:
1. Load base prompts
2. Apply mode-specific overrides
3. Apply company-specific overrides (this layer)

Company prompts are **appended** to mode prompts, allowing company-specific context without losing the interview mode structure.

## Creating a New Company Plugin

1. Create a directory: `targets/{company_name}/`
2. Add `system_prompt.md` with company-specific interview guidance
3. Optionally add other files referenced by the system_prompt
