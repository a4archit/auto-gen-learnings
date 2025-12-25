from autogen_runner import run_agent_sync
import streamlit as st




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
        response = run_agent_sync(prompt, st.session_state['messages'])

    st.session_state["messages"].append(
        {"role": "assistant", "content": response}
    )
    with st.chat_message("assistant"):
        st.markdown(response)






if __name__ == "__main__":
    # asyncio.run(main())
    print()