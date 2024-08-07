import streamlit as st
import asyncio

def main():
    st.title("Async with Streamlit")

    # Run async code in a separate thread or use background tasks
    if st.button("Run Async Task"):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(async_task())
        st.write(result)

async def async_task():
    await asyncio.sleep(2)  # Simulating an async task
    return "Async Task Completed!"

if __name__ == "__main__":
    main()
