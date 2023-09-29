from pandasai.responses.response_parser import ResponseParser

try:
    import streamlit as st
except ImportError:
    raise ImportError(
        "The 'streamlit' module is required but not installed. "
        "Please install it using pip: pip install streamlit"
    )


class StreamlitResponse(ResponseParser):
    def __init__(self, context):
        super().__init__(context)

    def format_plot(self, result) -> None:
        """
        Display plot against a user query in Streamlit
        Args:
            result (dict): result contains type and value
        """
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg

        # Load the image file
        image = mpimg.imread(result["value"])

        # Display the image
        plt.imshow(image)
        fig = plt.gcf()
        st.pyplot(fig)
