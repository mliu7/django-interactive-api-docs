# Interactive API Docs

This is a reusable application for creating beautiful REST API documentation for your app that clients can easily interact with and explore.

To see this app in action, visit the [Leaguevine Interactive API Documentation](https://api.leaguevine.com)

## Getting Started

### Download the Repo

### Copy the Static Files

Under the /media directory you will see css, js, and img files. Copy these to where your own static files live. The default templates use the {{ STATIC\_URL }} template variable and expect these files to live next to all of your other static files.

### Configure your settings

Add this to your installed apps:

    INSTALLED_APPS = (
        ...
        'interactive_api_docs',
    )

#### IAD\_BASE\_API\_URL

This is a string denoting the absolute URL of the root of your REST API with no trailing slash appended. Example: 

    IAD_BASE_API_URL = 'https://api.leaguevine.com/v1'

#### IAD\_ACCESS\_TOKEN\_CALLBACK

This is a string denoting the path to the method that creates an access token for a logged in user. This path contains the modules along the path, with the final element in the string being the method name. Example:

    IAD_ACCESS_TOKEN_CALLBACK = 'oauth2.utils.access_token_callback'

### Override the base templates

### Write your API Spec

This module relies on you writing your API specification in a dictionary format within a file called spec.py. I did not automatically create the spec based off of REST API Resources and Models because I feel that these two should be decoupled. This specification should be able to exist without having written a single line of backend code. Ideally, developers will write out the full API specification and finalize how it will look to the users before any backend code is written. This allows the API contract with the users to remain stable and unchanging even when the backend code gets refactored. By building the API documentation first, the API docs would result in 500 errors for all of the resources until each of the resources is coded up.

We've include sample\_spec.py as an example for how to begin writing your specification document. So copy it over to spec.py and configure it to your app appropriately.

    cp sample_spec.py spec.py
