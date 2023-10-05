from pandasai.responses.response_parser import ResponseParser


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
        try:
            image = mpimg.imread(result["value"])
        except FileNotFoundError:
            raise FileNotFoundError(f"The file {result['value']} does not exist.")
        except OSError:
            raise ValueError(f"The file {result['value']} is not a valid image file.")

        try:
            import streamlit as st
        except ImportError:
            raise ImportError(
                "The 'streamlit' module is required to use StreamLit Response. "
                "Please install it using pip: pip install streamlit"
            )

        # Display the image
        plt.imshow(image)
        fig = plt.gcf()
        st.pyplot(fig)
