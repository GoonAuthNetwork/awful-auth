## Awful Auth

SA profile authentication service used by the Goon Auth Network.

### Quick Start

While this service is designed to be deployed along with an auth database and discord bot it can be used as a standalone application.

### Development

Ensure there is a `.env` file in the project's root directory with the follow variables:

```
SA_COOKIES_SESSION_ID
SA_COOKIES_SESSION_HASH
SA_COOKIES_BB_USER_ID
SA_COOKIES_BB_PASSWORD
```

Use the vscode launch options to start an auto reloading version of the server.