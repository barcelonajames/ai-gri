"""
fields.py
Field management page: add / view / delete fields, with
per-field weather shown inline.
"""

import streamlit as st
from datetime import date

from db import add_field, get_fields, delete_field
from weather import get_weather

CROP_TYPES = ["Rice", "Corn", "Coconut", "Banana", "Sugarcane"]
SIZE_UNITS = ["hectares", "sqm", "acres"]


def show_fields(farmer):
    st.title("My Fields")
    st.caption("Manage your farm fields and see local weather per field.")

    with st.expander("+ Add new field"):
        with st.container(border=True):
            c1, c2 = st.columns(2)

            with c1:
                field_number = st.text_input(
                    "Field number", placeholder="e.g. Field 1"
                )
                crop_type = st.selectbox("Crop type", CROP_TYPES)
                date_planted = st.date_input(
                    "Petsa ng pagtatanim", value=date.today()
                )

            with c2:
                field_size = st.number_input(
                    "Field size", min_value=0.1, step=0.1, value=1.0
                )
                size_unit = st.selectbox("Size unit", SIZE_UNITS)
                location = st.text_input("Location/Barangay")
                lat = st.number_input(
                    "Latitude", format="%.6f", value=0.0
                )
                lng = st.number_input(
                    "Longitude", format="%.6f", value=0.0
                )
                st.caption(
                    "Tip: Get coordinates from Google Maps → "
                    "right-click your field"
                )

            if st.button("Save Field", type="primary"):
                if not field_number or not crop_type or not location:
                    st.error("Field number, crop type, and location are required.")
                else:
                    add_field(
                        farmer["id"], field_number, crop_type, date_planted,
                        field_size, size_unit, location, lat, lng,
                    )
                    st.success("Field saved!")
                    st.rerun()

    st.divider()

    fields = get_fields(farmer["id"])

    if not fields:
        st.info("No fields yet. Add your first field above.")
        return

    for f in fields:
        (field_id, user_id, field_number, crop_type, date_planted,
         field_size, size_unit, location, latitude, longitude, created_at) = f

        with st.container(border=True):
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f"**{field_number}**")
                st.caption(crop_type)
            with c2:
                st.caption("Planted")
                st.write(str(date_planted))
            with c3:
                st.caption("Size")
                st.write(f"{field_size} {size_unit}")
            with c4:
                st.caption("Location")
                st.write(location)

            if latitude and longitude and latitude != 0.0:
                weather = get_weather(latitude, longitude)
                if weather:
                    today = weather["days"][0]
                    st.markdown(
                        f"Today: {today['icon']} {today['label']} · "
                        f"{today['temp_max']}°/{today['temp_min']}°C · "
                        f"Rain {today['rain_pct']}%"
                    )
                    if today["rain_pct"] >= 70:
                        st.warning("Heavy rain expected today")
                    elif today["rain_pct"] >= 40:
                        st.info("Possible rain today")

            if st.button("Delete", key=f"delete_{field_id}"):
                delete_field(field_id, farmer["id"])
                st.rerun()
