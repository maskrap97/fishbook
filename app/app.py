import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta


# -------------------------
# Load data
# -------------------------

locations_df = pd.read_csv("data/locations.csv")
species_df = pd.read_csv("data/species.csv")
sessions_df = pd.read_csv("data/session.csv")
session_targets_df = pd.read_csv(
    "data/session_target_species.csv"
)
catches_df = pd.read_csv("data/catch.csv")


# -------------------------
# Initialize session state
# -------------------------

if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None

if "current_location_name" not in st.session_state:
    st.session_state.current_location_name = None

if "current_start_datetime" not in st.session_state:
    st.session_state.current_start_datetime = None

if "current_end_datetime" not in st.session_state:
    st.session_state.current_end_datetime = None

if "current_target_species" not in st.session_state:
    st.session_state.current_target_species = []

if "catch_form_version" not in st.session_state:
    st.session_state.catch_form_version = 0

if "last_catch_id" not in st.session_state:
    st.session_state.last_catch_id = None


# -------------------------
# Page setup
# -------------------------

st.title("Fish Book")


# ==========================================
# SESSION ENTRY
# ==========================================

if st.session_state.current_session_id is None:

    st.subheader("Add Fishing Session")

    with st.form("session_form"):

        session_date = st.date_input(
            "Session Date",
            value=date.today()
        )

        st.write("Session Start Time")

        time_col1, time_col2, time_col3 = st.columns(3)

        with time_col1:
            start_hour = st.selectbox(
                "Hour",
                options=list(range(1, 13)),
                index=6
            )

        with time_col2:
            start_minute = st.selectbox(
                "Minute",
                options=[
                    "00",
                    "15",
                    "30",
                    "45"
                ]
            )

        with time_col3:
            start_ampm = st.selectbox(
                "AM / PM",
                options=["AM", "PM"]
            )

        session_hours = st.number_input(
            "Session Duration (hours)",
            min_value=0.25,
            max_value=24.0,
            value=3.0,
            step=0.25
        )

        location_name = st.selectbox(
            "Fishing Location",
            options=locations_df["LocationName"].tolist()
        )

        target_species_names = st.multiselect(
            "Target Species",
            options=species_df["Common Name"].tolist()
        )

        offering_type = st.radio(
            "Offering Type",
            options=["Bait", "Lure", "Both"],
            horizontal=True
        )

        session_notes = st.text_area(
            "Session Notes"
        )

        submitted = st.form_submit_button(
            "Submit Session"
        )


    # -------------------------
    # Process session submission
    # -------------------------

    if submitted:

        if not target_species_names:
            st.error(
                "Please select at least one target species."
            )

        else:

            location_id = locations_df.loc[
                locations_df["LocationName"] == location_name,
                "LocationID"
            ].iloc[0]

            target_species_ids = species_df.loc[
                species_df["Common Name"].isin(
                    target_species_names
                ),
                "SpeciesID"
            ].tolist()


            # Convert 12-hour time to 24-hour time
            hour_24 = start_hour

            if start_ampm == "AM":
                if start_hour == 12:
                    hour_24 = 0
            else:
                if start_hour != 12:
                    hour_24 = start_hour + 12


            start_datetime = datetime(
                session_date.year,
                session_date.month,
                session_date.day,
                hour_24,
                int(start_minute)
            )

            end_datetime = (
                start_datetime
                + timedelta(hours=session_hours)
            )


            # Generate next SessionID
            existing_numbers = (
                sessions_df["SessionID"]
                .str.replace("S", "", regex=False)
                .astype(int)
            )

            next_number = existing_numbers.max() + 1
            session_id = f"S{next_number:03d}"


            # Create Session row
            new_session = pd.DataFrame([{
                "SessionID": session_id,
                "AnglerID": "A001",
                "StartDateTime": start_datetime,
                "EndDateTime": end_datetime,
                "LocationID": location_id,
                "OfferingType": offering_type,
                "SessionNotes": session_notes
            }])


            # Create target-species bridge rows
            new_targets = pd.DataFrame([
                {
                    "SessionID": session_id,
                    "SpeciesID": species_id
                }
                for species_id in target_species_ids
            ])


            # Append to existing tables
            updated_sessions = pd.concat(
                [sessions_df, new_session],
                ignore_index=True
            )

            updated_targets = pd.concat(
                [session_targets_df, new_targets],
                ignore_index=True
            )


            # Save
            updated_sessions.to_csv(
                "data/session.csv",
                index=False
            )

            updated_targets.to_csv(
                "data/session_target_species.csv",
                index=False
            )


            # Remember the active session
            st.session_state.current_session_id = session_id
            st.session_state.current_location_name = location_name
            st.session_state.current_start_datetime = start_datetime
            st.session_state.current_end_datetime = end_datetime
            st.session_state.current_target_species = (
                target_species_names
            )

            st.rerun()


# ==========================================
# CATCH ENTRY
# ==========================================

else:

    st.subheader("Add Catches")

    # -------------------------
    # Current session summary
    # -------------------------

    st.write("### Current Session")

    st.write(
        f"**Location:** {st.session_state.current_location_name}"
    )

    st.write(
        "**Start:** "
        + st.session_state.current_start_datetime.strftime(
            "%b %d, %Y at %#I:%M %p"
        )
    )

    st.write(
        "**End:** "
        + st.session_state.current_end_datetime.strftime(
            "%b %d, %Y at %#I:%M %p"
        )
    )

    st.write(
        "**Target Species:** "
        + ", ".join(st.session_state.current_target_species)
    )

    st.success(
        f"Session {st.session_state.current_session_id} created successfully."
    )


    # -------------------------
    # Controlled vocabularies
    # -------------------------

    rig_options = [
        "Carolina",
        "Drop Shot",
        "Fish Finder",
        "High-Low",
        "Jig Head",
        "Texas",
        "Freeline",
        "Sabiki",
        "Direct Tie",
        "Other"
    ]

    lure_color_options = [
        "Natural",
        "White",
        "Silver",
        "Pink",
        "Chartreuse",
        "Black",
        "Red",
        "Blue",
        "Purple",
        "Motor Oil",
        "Green Pumpkin",
        "Watermelon",
        "Perch",
        "Anchovy",
        "Custom"
    ]

    brand_model_options = [
        "Battlestar 115",
        "Battlestar 155",
        "Battlestar Rib Bait",
        "Keitech Swing Impact",
        "Keitech Easy Shiner",
        "Big Hammer Swimbait",
        "Zoom Fluke",
        "Lucky Craft Flash Minnow 110",
        "Lucky Craft Flash Minnow 130MRS",
        "Big Hammer Grub",
        "Gulp Sand Crab",
        "Gulp Camo Worm",
        "Custom"
    ]

    bait_options = [
        "Sand Crab",
        "Live Anchovy",
        "Live Sardine",
        "Squid",
        "Market Shrimp",
        "Ghost Shrimp",
        "Mussel",
        "Clam",
        "Lug Worm",
        "Blood Worm",
        "Cut Bait",
        "Live Bait Other",
        "Custom"
    ]

    lure_type_options = [
        "Jerkbait",
        "Swimbait",
        "Grub",
        "Fluke",
        "Jig",
        "Spoon",
        "Topwater",
        "Worm",
        "Custom"
    ]


    # -------------------------
    # Dynamic offering fields
    # -------------------------

    if st.session_state.last_catch_id is not None:

        st.success(
            f"Catch {st.session_state.last_catch_id} saved successfully."
        )

        st.session_state.last_catch_id = None

    catch_offering_type = st.radio(
        "Caught On",
        options=["Bait", "Lure"],
        horizontal=True
    )

    bait = None
    lure_type = None
    lure_size = None
    lure_color = None
    brand_model = None

    if catch_offering_type == "Bait":

        bait_option = st.selectbox(
            "Bait",
            options=bait_options
        )

        if bait_option == "Custom":
            bait = st.text_input(
                "Enter Bait"
            )
        else:
            bait = bait_option

    else:

        lure_type_option = st.selectbox(
            "Lure Type",
            options=lure_type_options
        )

        if lure_type_option == "Custom":
            lure_type = st.text_input(
                "Enter Lure Type"
            )
        else:
            lure_type = lure_type_option

        lure_color_option = st.selectbox(
            "Lure Color",
            options=lure_color_options
        )

        if lure_color_option == "Custom":
            lure_color = st.text_input(
                "Enter Lure Color"
            )
        else:
            lure_color = lure_color_option

        brand_model_option = st.selectbox(
            "Brand / Model",
            options=brand_model_options
        )

        if brand_model_option == "Custom":
            brand_model = st.text_input(
                "Enter Brand / Model"
            )
        else:
            brand_model = brand_model_option


    # -------------------------
    # Catch form
    # -------------------------

    with st.form(
    f"catch_form_{st.session_state.catch_form_version}"
    ):

        st.write("### Catch Details")

        species_name = st.selectbox(
            "Species",
            options=species_df["Common Name"].tolist()
        )

        st.write("Catch Time")

        time_col1, time_col2, time_col3 = st.columns(3)

        with time_col1:
            catch_hour = st.selectbox(
                "Hour",
                options=list(range(1, 13))
            )

        with time_col2:
            catch_minute = st.selectbox(
                "Minute",
                options=["00", "15", "30", "45"]
            )

        with time_col3:
            catch_ampm = st.selectbox(
                "AM / PM",
                options=["AM", "PM"]
            )

        col1, col2 = st.columns(2)

        with col1:
            length_in = st.number_input(
                "Length (inches)",
                min_value=0.0,
                step=0.25
            )

        with col2:
            weight_lb = st.number_input(
                "Weight (lb)",
                min_value=0.0,
                step=0.1
            )

        rig = st.selectbox(
            "Rig",
            options=rig_options
        )

        if catch_offering_type == "Lure":
            lure_size = st.number_input(
                "Lure Size (inches)",
                min_value=0.0,
                step=0.25
            )

        released = st.radio(
            "Released?",
            options=["Yes", "No"],
            horizontal=True
        )

        catch_notes = st.text_area(
            "Catch Notes"
        )

        catch_submitted = st.form_submit_button(
            "Add Catch"
        )


    # -------------------------
    # Validate + preview
    # -------------------------

    if catch_submitted:

        species_id = species_df.loc[
            species_df["Common Name"] == species_name,
            "SpeciesID"
        ].iloc[0]

        catch_hour_24 = catch_hour

        if catch_ampm == "AM":
            if catch_hour == 12:
                catch_hour_24 = 0
        else:
            if catch_hour != 12:
                catch_hour_24 = catch_hour + 12

        session_start = st.session_state.current_start_datetime
        session_end = st.session_state.current_end_datetime

        catch_time_value = datetime.strptime(
            f"{catch_hour_24}:{catch_minute}",
            "%H:%M"
        ).time()

        candidate_same_day = datetime.combine(
            session_start.date(),
            catch_time_value
        )

        candidate_next_day = datetime.combine(
            session_start.date() + timedelta(days=1),
            catch_time_value
        )

        if session_start <= candidate_same_day <= session_end:
            catch_datetime = candidate_same_day

        elif session_start <= candidate_next_day <= session_end:
            catch_datetime = candidate_next_day

        else:
            catch_datetime = None


        if catch_datetime is None:

            st.error(
                "Catch time must fall within the current session."
            )

        else:

            current_catches_df = pd.read_csv(
                "data/catch.csv"
            )

            # Generate next CatchID
            existing_numbers = (
                current_catches_df["CatchID"]
                .str.replace("C", "", regex=False)
                .astype(int)
            )

            next_number = existing_numbers.max() + 1
            catch_id = f"C{next_number:03d}"


            # Create new catch row
            new_catch = pd.DataFrame([{
                "CatchID": catch_id,
                "SessionID":
                    st.session_state.current_session_id,
                "CatchDateTime": catch_datetime,
                "SpeciesID": species_id,
                "LengthIn": length_in,
                "WeightLb": weight_lb,
                "OfferingType": catch_offering_type,
                "Bait": bait,
                "LureType": lure_type,
                "LureSizeIn": lure_size,
                "LureColor": lure_color,
                "Rig": rig,
                "BrandModel": brand_model,
                "Released": released,
                "CatchNotes": catch_notes
            }])


            # Reload catches before writing
            # so repeated catches in the same Streamlit session
            # don't overwrite each other.
            

            updated_catches = pd.concat(
                [current_catches_df, new_catch],
                ignore_index=True
            )

            updated_catches.to_csv(
                "data/catch.csv",
                index=False
            )


            st.session_state.catch_form_version += 1

            st.session_state.last_catch_id = catch_id

            st.rerun()

    if st.button("Finish Session"):

        st.session_state.current_session_id = None
        st.session_state.current_location_name = None
        st.session_state.current_start_datetime = None
        st.session_state.current_end_datetime = None
        st.session_state.current_target_species = []

        st.rerun()