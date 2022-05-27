A few examples on how to start and subscribe to a pubsubhubbub with youtube notifcations

You need to download the XML parser: LXML https://lxml.de/
You also need cython to install it.

Problems:
1. Sometimes it can subscribe to fast and the web server won't catch it. There isn't a on_started method, only a on_startup which runs beside the server startup.
2. Unsubscribing takes a long time. It's not necessary but I mainly added it for demonstration.
3. PubSubHubBub will send multiple responses for some reason. I don't know how to tell them we have the response.
If you have a solution please open a Pull Request or issue!

Hope this helps! You can join my discord https://discord.gg/A8MXcQBKpf or open a issue if you have a problem with it.
