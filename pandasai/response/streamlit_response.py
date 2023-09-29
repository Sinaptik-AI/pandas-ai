from pandasai.response.response_parser import ResponseParser

try:
    import streamlit as st
except ImportError:
    raise


class StreamLitResponse(ResponseParser):
    def __init__(self, context):
        super().__init__(context)

    def format_plot(self, result):
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg

        # Load the image file
        image = mpimg.imread(result["value"])

        # Display the image
        plt.imshow(image)
        fig = plt.gcf()
        st.pyplot(fig)
