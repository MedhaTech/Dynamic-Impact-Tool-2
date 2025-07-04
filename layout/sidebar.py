import streamlit as st

def render_sidebar():
    st.sidebar.title("Dynamic Impact Tool")

    # Mode Selection
    mode = st.sidebar.radio("Select Mode", ["Single Dataset", "Compare Datasets"], index=0 if st.session_state["mode"] == "single" else 1)

    # Update mode in session
    if mode == "Single Dataset":
        if st.session_state["mode"] != "single":
            st.session_state["mode"] = "single"
            st.session_state["current_compare"] = None  # Clear compare context
            st.rerun()

    else:
        if st.session_state["mode"] != "comparison":
            st.session_state["mode"] = "comparison"
            st.session_state["current_session"] = None  # Clear single dataset context
            st.rerun()

    st.sidebar.markdown("---")

    # Dataset History (List View like ChatGPT)
    if st.session_state["mode"] == "single":
        st.sidebar.markdown("## 🗂️ Dataset History")
        if st.session_state["dataset_sessions"]:
            for dataset in st.session_state["dataset_sessions"].keys():
                if st.sidebar.button(dataset, key=f"dataset_{dataset}"):
                    st.session_state["current_session"] = dataset
                    st.rerun()
        else:
            st.sidebar.info("No datasets uploaded yet.")

    # Comparison History
    elif st.session_state["mode"] == "comparison":
        st.sidebar.markdown("## 🗂️ Comparison History")
        if st.session_state["compare_sessions"]:
            for comparison in st.session_state["compare_sessions"].keys():
                if st.sidebar.button(comparison, key=f"compare_{comparison}"):
                    st.session_state["current_compare"] = comparison
                    st.rerun()
        else:
            st.sidebar.info("No comparisons uploaded yet.")

    st.sidebar.markdown("---")

    # Clear Sessions Button
    if st.sidebar.button("🧹 Clear All Sessions"):
        st.session_state["dataset_sessions"] = {}
        st.session_state["compare_sessions"] = {}
        st.session_state["current_session"] = None
        st.session_state["current_compare"] = None
        st.rerun()
