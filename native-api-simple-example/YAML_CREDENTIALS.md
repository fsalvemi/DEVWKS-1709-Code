# Catalyst Center Native API - YAML Credentials Feature

## Overview

This branch adds support for loading Catalyst Center credentials from YAML configuration files, making it easier to manage multiple environments and keeping credentials out of the source code.

## Configuration File Format

Create a `CC_Env.yml` file with the following structure:

```yaml
# Catalyst Center Credentials Configuration
CC_IP: 198.18.129.100
CC_USERNAME: admin
CC_PASSWORD: C1sco12345
CC_INSECURE: true  # Set to false to enable SSL certificate verification
```

## Usage

### Configuration File is Required

The `--config` option is **required** for all operations. You must specify a YAML configuration file:

```bash
python native_api_simple.py create --config CC_Env.yml
python native_api_simple.py delete --config CC_Env_CX_Lab_CC1.yml
python native_api_simple.py status --config CC_Env_CX_Lab_CC3.yml
```

### Multiple Environment Support

You can easily switch between different Catalyst Center environments by specifying different configuration files:

```bash
# Production environment
python native_api_simple.py status --config CC_Env_Production.yml

# Lab environment
python native_api_simple.py create --config CC_Env_CX_Lab_CC1.yml

# Development environment
python native_api_simple.py status --config CC_Env_Dev.yml
```

## Security Best Practices

1. **Never commit `CC_Env.yml`** to version control - it's already in `.gitignore`
2. Use the sample files (`CC_Env_Sample.yml`) as templates
3. Keep actual credential files local only
4. For production, consider using environment variables or a secrets management system

## Files

- `CC_Env_Sample.yml` - Template configuration file (safe to commit)
- `CC_Env_CX_Lab_CC3.yml` - Example lab configuration (safe to commit, uses lab credentials)
- `CC_Env.yml` - Your actual configuration (DO NOT COMMIT - in .gitignore)

## Installation

Install the additional dependency:

```bash
pip install PyYAML==6.0.1
```

Or install all dependencies:

```bash
pip install -r requirements.txt
```

## Benefits

- ✅ **Mandatory configuration** - No hardcoded credentials in source code
- ✅ **Enhanced security** - Credentials always in external files
- ✅ **Easy environment switching** - Just change the --config parameter
- ✅ **Clear error messages** - Script fails fast if config is missing
- ✅ **No accidental credential commits** - Config files are gitignored
- ✅ **Multiple environment support** - Lab, Dev, Prod configurations

