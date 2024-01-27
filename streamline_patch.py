import asyncio
from streamlit import script_runner

# Create and set up an event loop
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Run the Streamlit script with the patched event loop
script_runner.ScriptRunner.scriptThreadEnviron['asyncio.EventLoopPolicy'] = (
    asyncio.WindowsProactorEventLoopPolicy()
)
script_runner.ScriptRunner.scriptThreadEnviron["asyncio.events.new_event_loop"] = (
    asyncio.ProactorEventLoop().new_event_loop
)
script_runner.ScriptRunner.scriptThreadEnviron["asyncio.events.get_event_loop"] = (
    asyncio.ProactorEventLoop().get_event_loop
)

import main  # write the name of main python script here

