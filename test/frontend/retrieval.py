import streamlit as st
import requests
from datetime import datetime

backend_url = "http://localhost:8000"

def app():
    st.title("Item Search & Retrieval")

    st.subheader("Search for an Item by Item ID")
    item_id = st.text_input("Enter Item ID")

    astronaut_name = st.text_input("Astronaut Name")
    submit = st.button("Retrieve Item")

    if submit:
        if not item_id or not astronaut_name:
            st.warning("Please enter both Item ID and Astronaut Name.")
            return

        try:
            response = requests.get(f"{backend_url}/retrieve/{item_id}")
            if response.status_code == 200:
                result = response.json()

                st.success("Item found and retrieved successfully!")
                st.markdown(f"🔹 Item Name: {result['item']['name']}")
                st.markdown(f"🔹 Container: {result['container_id']}")
                st.markdown(f"🔹 Zone: {result['zone']}")
                st.markdown(f"🔹 Coordinates: {result['coordinates']}")
                st.markdown(f"🔹 Steps Required: {result['steps_required']}")
                st.markdown(f"🔹 Expiry Date: {result['item'].get('expiry_date', 'N/A')}")

                with st.expander("Optional: Place it in a new container"):
                    new_container = st.text_input("New Container ID")
                    confirm_replace = st.button("Place in New Container")

                    if confirm_replace and new_container:
                        update_response = requests.post(
                            f"{backend_url}/relog-placement",
                            json={
                                "item_id": item_id,
                                "new_container": new_container,
                                "astronaut": astronaut_name,
                                "timestamp": datetime.utcnow().isoformat()
                            }
                        )
                        if update_response.status_code == 200:
                            st.success("Item placed in new container and logged.")
                        else:
                            st.error("Re-placement failed.")
            else:
                st.error(f"Item not found or retrieval failed: {response.json().get('detail')}")
        except Exception as e:
            st.error(f"Error contacting backend: {e}")