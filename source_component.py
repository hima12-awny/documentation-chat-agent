import streamlit as st
from typing import Dict, Any, Optional


class SourceCard:
    """
    A reusable component for displaying compact source code files as clickable cards in Streamlit.
    """

    def __init__(self):
        # Programming language icons
        self.icons = {
            "Java": "https://img.icons8.com/color/35/000000/java-coffee-cup-logo.png",
            "Python": "https://img.icons8.com/color/35/000000/python.png",
            "C": "https://img.icons8.com/color/35/000000/c-programming.png",
            "C++": "https://img.icons8.com/color/35/000000/c-plus-plus-logo.png",
            "C#": "https://img.icons8.com/color/35/000000/c-sharp-logo.png",
            "JavaScript": "https://img.icons8.com/color/40/000000/javascript.png",
            "TypeScript": "https://img.icons8.com/color/40/000000/typescript.png",
            "Ruby": "https://img.icons8.com/office/35/000000/ruby-programming-language.png",
            "PHP": "https://img.icons8.com/officel/40/000000/php-logo.png",
            "Swift": "https://img.icons8.com/fluent/40/000000/swift.png",
            "Markdown": "https://res.cloudinary.com/dcu6hrqeq/image/upload/v1741824368/file_qikjrq.png",
        }
        # Inject CSS once
        self._inject_css()

    def _inject_css(self):
        """Inject the required CSS for the component."""
        st.markdown("""
        <style>
        .clickable-container {
            display: inline-block;
            width: auto;
            padding: 6px 10px;
            border-radius: 12px;
            font-size: 16px;
            border: 1px solid rgba(255,255,255,.2);
            cursor: pointer;
            transition: all 0.3s ease;
            color: inherit;
            position: relative;
            margin: 5px;
        }

        .clickable-container:hover {
            background-color: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,.3);
            box-shadow: 0px 2px 4px rgba(255,255,255,0.2);
        }

        /* Tooltip styles */
        .tooltip {
            position: relative;
            display: inline-block;
            width: 100%;
        }
        
        .tooltip .tooltip-text {
            visibility: hidden;
            width: auto;
            background-color: #333;
            color: #fff;
            text-align: center;
            border-radius: 4px;
            padding: 4px 8px;
            position: absolute;
            z-index: 1000;
            bottom: 125%;
            left: 50%;
            transform: translateX(-50%);
            opacity: 0;
            transition: opacity 0.6s;
            white-space: nowrap;
            font-size: 11px;
        }
        
        .tooltip:hover .tooltip-text {
            visibility: visible;
            opacity: 1;
        }

        .container-content {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .source-info {
            display: flex;
            flex-direction: column;
        }

        .file-icon {
            width: 40px;
            height: 40px;
        }

        .file-name {
            margin: 0;
            font-size: 13px;
            font-weight: bold;
        }

        .last-updated {
            font-size: 12px;
            opacity: 0.8;
            font-weight: bold;
            margin-top: -5px;
        }
        </style>
        """, unsafe_allow_html=True)

    def _get_icon_for_file(self, filename: str) -> str:
        """Determine the appropriate icon based on file extension."""
        file_extension = filename.split('.')[-1].lower()

        mapping = {
            "java": "Java",
            "py": "Python",
            "c": "C",
            "cpp": "C++",
            "h": "C++",
            "hpp": "C++",
            "cs": "C#",
            "js": "JavaScript",
            "ts": "TypeScript",
            "rb": "Ruby",
            "php": "PHP",
            "swift": "Swift",
            'md': "Markdown"
        }

        # Default to Python if unknown
        icon_key = mapping.get(file_extension, "Python")
        return self.icons[icon_key]

    def render(
            self,
            data: Dict[str, Any],

            parent: Optional[
                st.delta_generator.DeltaGenerator  # type: ignore
            ] = None
    ) -> None:
        """
        Render the source card component.

        Args:
            data: Dictionary containing 'source', 'source_url', and 'source_last_updated'
            parent: Optional Streamlit container to render within (st.sidebar, column, etc.)
        """
        # Use the provided parent or default to st
        container = parent if parent is not None else st

        # Get appropriate icon
        icon_url = self._get_icon_for_file(data['source'])

        # Create clickable container with image and content and tooltip
        container.markdown(f"""
        <div class="tooltip">
            <a href="{data['source_url']}" target="_blank" class="clickable-container" style="text-decoration: none;">
                <div class="container-content">
                    <img src="{icon_url}" class="file-icon" alt="Programming language icon">
                    <div class="source-info">
                        <p class="file-name">{data['source']}</p>
                        <span class="last-updated">{data['source_last_updated']}</span>
                    </div>
                    <span class="tooltip-text">{data['source_url']}</span>
                </div>
            </a>
        </div>
        """, unsafe_allow_html=True)


# # Example usage:
# if __name__ == "__main__":
#     st.title("Source Code Files")

#     # Create source card component
#     source_card = SourceCard()

#     with st.chat_message("ai"):
#         cols = st.columns(3)  # Changed to 3 columns for more compact display

#         source_card.render({
#             'source': 'index.js',
#             'source_url': 'https://github.com/example/repo/index.js',
#             'source_last_updated': '2025-03-09 09:15:43'
#         }, parent=cols[0])
#         source_card.render({
#             'source': 'styles.css',
#             'source_url': 'https://github.com/example/repo/styles.css',
#             'source_last_updated': '2025-03-08 11:22:37'
#         }, cols[1])
#         source_card.render({
#             'source': 'app.py',
#             'source_url': 'https://github.com/example/repo/app.py',
#             'source_last_updated': '2025-03-10 14:22:05'
#         }, cols[2])
