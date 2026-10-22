
import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="AI Travel Planner",
    page_icon="✈️",
    layout="centered"
)

st.title("✈️ AI Travel Planner")
st.write("Plan your next trip with AI!")

api_key = os.getenv("GROQ_API_KEY")

with st.form("travel_form"):
    st.subheader("Tell us about your trip")

    name = st.text_input("Your Name")
    destination = st.text_input("Destination")

    col1, col2 = st.columns(2)

    with col1:
        days = st.number_input(
            "Number of Days",
            min_value=1,
            max_value=30,
            value=4
        )

    with col2:
        budget = st.number_input(
            "Total Budget",
            min_value=1,
            value=800
        )

    currency = st.selectbox(
        "Budget Currency",
        ["USD", "PKR", "GBP", "EUR", "AED"]
    )

    interests = st.multiselect(
        "Your Interests",
        [
            "Adventure", "Food", "Nature",
            "Shopping", "History", "Beaches",
            "Culture", "Photography"
        ],
        default=["Food", "Nature"]
    )

    travel_style = st.selectbox(
        "Travel Style",
        ["Solo", "Family", "Friends", "Couple"]
    )

    technique = st.selectbox(
        "Choose Prompting Technique",
        [
            "Zero-Shot",
            "Few-Shot",
            "Structured Reasoning"
        ]
    )

    submitted = st.form_submit_button(
        "Generate My Travel Plan"
    )

if submitted:
    if not api_key:
        st.error(
            "API key not found. Please check your .env file."
        )

    elif not name.strip() or not destination.strip():
        st.warning("Please enter your name and destination.")

    elif not interests:
        st.warning("Please select at least one interest.")

    else:
        traveler = f"""
        Traveler name: {name}
        Destination: {destination}
        Number of days: {days}
        Total budget: {budget} {currency}
        Interests: {", ".join(interests)}
        Travel style: {travel_style}
        """

        if technique == "Zero-Shot":
            prompt = f"""
            You are a helpful AI travel planner.

            Create a personalized travel itinerary using the
            traveler's information below. Do not use examples.

            Analyze their preferences, suggest attractions,
            create a day-by-day itinerary, and estimate costs
            within their total budget.

            Include activities, meal suggestions, transport,
            estimated daily spending, and a total cost summary.
            Explain that costs are estimates and may change.

            Traveler information:
            {traveler}
            """

        elif technique == "Few-Shot":
            prompt = f"""
            You are an AI travel planner. Follow these examples
            to create a personalized itinerary.

            Example 1:
            Traveler: Sara, Istanbul, 2 days, $300,
            interests: history and food, style: friends.
            Sample plan:
            Day 1: Visit the historic old city and try local food.
            Day 2: Explore a market and visit a cultural museum.
            Keep estimated expenses within the budget.

            Example 2:
            Traveler: Ali, Islamabad, 2 days, $200,
            interests: nature and photography, style: solo.
            Sample plan:
            Day 1: Visit a scenic viewpoint and a local park.
            Day 2: Explore a nature area and take photographs.
            Include estimated transport and meal costs.

            Example 3:
            Traveler: Maya, Dubai, 3 days, $500,
            interests: shopping and beaches, style: family.
            Sample plan:
            Day 1: Visit a public beach.
            Day 2: Explore a shopping area.
            Day 3: Enjoy a family-friendly attraction.
            Include estimated expenses.

            Now create a NEW plan for this traveler.
            Use the examples as guidance, not as a plan to copy.

            Include daily activities, estimated costs, and a
            total budget summary. Keep costs within budget.

            Traveler information:
            {traveler}
            """

        else:
            prompt = f"""
            You are an AI travel planner.

            Create a personalized itinerary for this traveler.
            Follow these planning steps internally:
            1. Identify the traveler's preferences.
            2. Consider the total budget.
            3. Plan suitable activities for the number of days.
            4. Select attractions matching their interests.
            5. Organize activities into a day-by-day itinerary.
            6. Check that estimated costs fit the budget.

            Present only the final itinerary and brief
            justifications for your recommendations.
            Do not reveal private internal reasoning.

            Include estimated daily costs, transport, meals,
            activities, and a total cost summary.
            Clearly label uncertain prices as estimates.
            Do not claim to have checked live prices.

            Traveler information:
            {traveler}
            """

        try:
            with st.spinner("Creating your travel itinerary..."):
                client = Groq(api_key=api_key)

                response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a helpful travel planner. "
                                "Be practical, clear, and budget-aware."
                            )
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.5,
                    max_completion_tokens=3000
                )

                itinerary = response.choices[0].message.content

            st.success("Your travel plan is ready!")
            st.subheader(f"Travel Plan for {name}")
            st.caption(f"Technique used: {technique}")
            st.markdown(itinerary)

        except Exception as error:
            st.error(
                "Something went wrong while generating the plan. "
                "Check your API key, internet connection, and "
                "Groq model availability, then try again."
            )
            st.caption(f"Error details: {error}")
