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

### Default Configuration File

By default, the script looks for `CC_Env.yml` in the current directory or the script directory:

```bash
python native_api_simple.py create
python native_api_simple.py delete  
python native_api_simple.py status
```

### Custom Configuration File

You can specify a different configuration file using the `--config` option:

```bash
python native_api_simple.py status --config CC_Env_CX_Lab_CC3.yml
python native_api_simple.py create --config my_lab_config.yml
```

### Fallback to Hardcoded Credentials

If no YAML file is found, the script falls back to hardcoded credentials (for backward compatibility).

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

- ✅ Separate credentials from code
- ✅ Easy to switch between multiple environments
- ✅ Better security (credentials not in source code)
- ✅ Simpler configuration management
- ✅ Still supports hardcoded fallback for simple use cases

