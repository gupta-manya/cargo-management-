import streamlit as st
import requests

backend_url = "http://localhost:8000"

def fetch_container_count():
    try:
        response = requests.get(f"{backend_url}/summary")
        if response.status_code == 200:
            return response.json().get("total_containers", 0)
    except Exception as e:
        st.error(f"Error checking containers: {e}")
    return 0

def app():
    st.title("Place an Item Manually")

    # Check if any containers exist
    container_count = fetch_container_count()
    # if container_count == 0:
    #     st.warning("No containers available. Please upload container data first via Home.")
    #     return

    with st.form("placement_form"):
        item_id = st.text_input("Item ID")
        name = st.text_input("Item Name")
        width = st.number_input("Width (cm)", min_value=0.0)
        depth = st.number_input("Depth (cm)", min_value=0.0)
        height = st.number_input("Height (cm)", min_value=0.0)
        mass = st.number_input("Mass (kg)", min_value=0.0)
        priority = st.number_input("Priority", min_value=0, step=1)
        expiry_date = st.text_input("Expiry Date (or N/A)")
        usage_limit = st.number_input("Usage Limit", min_value=0, step=1)
        preferred_zone = st.text_input("Preferred Zone")

        submitted = st.form_submit_button("Place Item")
        if submitted:
            item_data = {
                "item_id": item_id,
                "name": name,
                "width_cm": width,
                "depth_cm": depth,
                "height_cm": height,
                "mass_kg": mass,
                "priority": priority,
                "expiry_date": expiry_date,
                "usage_limit": usage_limit,
                "preferred_zone": preferred_zone
            }

            try:
                response = requests.post(f"{backend_url}/place-item", json=item_data)
                if response.status_code == 200:
                    result = response.json()
                    st.success("Item successfully placed.")
                    st.markdown(f"**Zone**: {result['zone']}")
                    st.markdown(f"**Container ID**: {result['container_id']}")
                    st.markdown(f"**Start Coordinates**: {result['start_coordinates']}")
                    st.markdown(f"**End Coordinates**: {result['end_coordinates']}")
                else:
                    st.error(f"Placement failed: {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
