# First authenticate using this command: `google-cloud-sdk/bin/gcloud auth application-default login`
# This will allow you to access the VertexAI API
# To Run: `streamlit run app.py`

import streamlit as st
from code_editor import code_editor  # third party streamlit editable code_block, WIP
import google.auth

credential, project = google.auth.default()
from langchain_google_vertexai import VertexAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

# Set up the LLM Models

code_model = VertexAI(model_name="code-bison")

explain_template = """Explain this code sample: {code}

Answer: Let's think step by step. The code should be written in the following language: {language}"""

title_template = """Create a title for this code sample in under 50 characters: {code}

Answer: Let's make this intuitive and human readable. The code should be written in the following language: {language}"""

code_prompt = PromptTemplate(
    template=explain_template, input_variables=["code", "language"]
)
title_prompt = PromptTemplate(
    template=title_template, input_variables=["code", "language"]
)

code_chain = LLMChain(prompt=code_prompt, llm=code_model)
title_chain = LLMChain(prompt=title_prompt, llm=code_model)


# Load Session State and Define Functions


def generate_metadata():
    input_code = st.session_state["input_code"]
    input_language = st.session_state["selected_language"]

    code_explain_output = code_chain.invoke(
        {"code": input_code, "language": input_language}
    )
    code_title_output = title_chain.invoke(
        {"code": input_code, "language": input_language}
    )

    st.session_state["code_description"] = code_explain_output["text"]
    st.session_state["code_title"] = code_title_output["text"]

    # Reset Generate Button
    st.session_state["generate_metadata_disabled"] = True

    print(code_explain_output["text"])
    print(code_title_output["text"])


if "generate_metadata_disabled" not in st.session_state:
    st.session_state["generate_metadata_disabled"] = True

if "prior_code_editor_id" not in st.session_state:
    st.session_state["prior_code_editor_id"] = ""

# Button Customization options for code-editor
code_editor_btns = [
    {
        "name": "Stage Code for Metadata Generation",
        "hasText": True,
        "alwaysOn": True,
        "style": {"top": "0.46rem", "right": "0.4rem"},
        "commands": ["submit", "test_command"],
    }
]


if "input_code" not in st.session_state:
    st.session_state["input_code"] = ""

if "code_title" not in st.session_state:
    st.session_state["code_title"] = ""

if "code_description" not in st.session_state:
    st.session_state["code_description"] = ""

if "selected_language" not in st.session_state:
    st.session_state["selected_language"] = "javascript"


# Rendering Section
st.title("MVP for Metadata Generation App")

st.selectbox(
    "Select Language",
    options=("javascript", "python", "java", "cpp"),
    key="selected_language",
)


response_dict = code_editor(
    info={"name": "Input your code here:"},
    code="""console.log("hello world");""",
    lang=st.session_state["selected_language"],
    key="response_dict",
    buttons=code_editor_btns,
    allow_reset=True,
)


st.session_state["code_editor_input"] = response_dict
st.session_state["input_code"] = response_dict["text"]


if not (
    st.session_state["code_editor_input"]["id"]
    == st.session_state["prior_code_editor_id"]
):
    st.session_state["prior_code_editor_id"] = st.session_state["code_editor_input"][
        "id"
    ]
    st.session_state["generate_metadata_disabled"] = False


st.button(
    "Generate Metadata",
    type="secondary",
    disabled=st.session_state["generate_metadata_disabled"],
    on_click=generate_metadata,
)

st.text_input("Code Title", value="", key="code_title")
st.text_area("Code Description", value="", key="code_description", height=300)

# Session State for Logging/Debugging
st.session_state
