from autogen_runner import run_agent_sync
import streamlit as st



# async def test_fx():
#     agent = Agent()
#     response = await agent.chat("what is the conversion rate of currency from usd to inr.")
#     print(f"\n\nAI: {response.messages[-1].content}\n")


# async def run_agent(prompt: str):
#     agent = Agent()   # ← created INSIDE event loop
#     result = await agent.chat(prompt)
#     return result.messages[-1].content


# def run_agent_sync(prompt: str) -> str:
#     return asyncio.run(run_agent(prompt))



# async def main() -> None:
#     st.set_page_config(page_title="AI Chat Assistant", page_icon="🤖")
#     st.title("AI Chat Assistant 🤖")

#     # adding agent object to session state to persist across sessions
#     # stramlit reruns the script on every user interaction
#     if "agent" not in st.session_state:
#         st.session_state["agent"] = Agent()

#     # initialize chat history
#     if "messages" not in st.session_state:
#         st.session_state["messages"] = []

#     # displying chat history messages
#     for message in st.session_state["messages"]:
#         with st.chat_message(message["role"]):
#             st.markdown(message["content"])

#     prompt = st.chat_input("Type a message...")
#     if prompt:
#         st.session_state["messages"].append({"role": "user", "content": prompt})
#         with st.chat_message("user"):
#             st.markdown(prompt)

#         response = await st.session_state["agent"].chat(prompt)
#         response = response.messages[-1].content
#         st.session_state["messages"].append({"role": "assistant", "content": response})
#         with st.chat_message("assistant"):
#             st.markdown(response)




st.set_page_config(page_title="AI Chat Assistant", page_icon="🤖")
st.title("AI Chat Assistant 🤖")

# Chat history (SAFE to persist)
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# Display history
for msg in st.session_state["messages"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("Type a message...")

if prompt:
    # User message
    st.session_state["messages"].append(
        {"role": "user", "content": prompt}
    )
    with st.chat_message("user"):
        st.markdown(prompt)

    # Agent response
    with st.spinner("Thinking..."):
        response = run_agent_sync(prompt, [])

    st.session_state["messages"].append(
        {"role": "assistant", "content": response}
    )
    with st.chat_message("assistant"):
        st.markdown(response)






if __name__ == "__main__":
    # asyncio.run(main())
    print()