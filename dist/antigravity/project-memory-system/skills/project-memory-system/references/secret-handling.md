# Secret Handling

## Rules

- Never print secret values.
- Never copy secret values into markdown memory.
- Never commit secret files.
- Never include `.env` contents in summaries.
- Show key names only, not values.

## Ignore Defaults

```gitignore
.env
.env.*
!.env.example
secrets/
credentials/
api-keys/
tokens/
*.pem
*.key
*.p12
*.pfx
```

## Safe Behavior

It is safe to say:

- `LEADFEEDER_API_KEY is present`
- `.env.local exists and is ignored`

It is not safe to show:

- Token values
- API key prefixes/suffixes
- Full credential file contents
