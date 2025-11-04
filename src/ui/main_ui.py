"""User Interface Layer for MammoChat™.

This module implements the presentation layer of the MammoChat™ application,
providing a web-based chat interface using the NiceGUI framework. It handles
user interactions, message display, and UI state management while maintaining
clear separation from business logic and data persistence.

Key responsibilities:
- Render chat messages with proper styling and theming
- Handle user input and send messages to the chat service
- Manage conversation state and UI updates
- Provide theme-aware styling for light/dark modes
- Set up static file serving

The UI follows a modular design where presentation logic is isolated from
service operations, enabling easy testing and maintenance.
"""

import asyncio
from typing import Any

from nicegui import ui  # type: ignore

from config import config
from src.models.chat import ConversationState
from src.services.chat_service import ChatService
from src.utils.text_processing import strip_markdown


def setup_colors(scene: Any) -> None:
    ui.colors(
        primary=scene["palette"]["primary"],
        secondary=scene["palette"]["secondary"],
        accent=scene["palette"]["accent"],
        positive=scene["status"]["positive"],
        negative=scene["status"]["negative"],
        info=scene["status"]["info"],
        warning=scene["status"]["warning"],
    )


def setup_head_html(scene: Any) -> None:
    """Set up PWA meta tags, fonts, and custom CSS."""
    ui.add_head_html(
        f"""
        <meta name="theme-color" content="{scene["palette"]["primary"]}">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
        <link rel="icon" type="image/svg+xml" href="/branding/icon.svg">
        <link rel="apple-touch-icon" href="/branding/apple-touch-icon.png">
        <link rel="manifest" href="/public/manifest.json">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, "
              "maximum-scale=1.0, user-scalable=no">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="{scene.get("fonts", {}).get("google_fonts_url", "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Playfair+Display:ital,wght@0,400;1,400&display=swap")}"
              rel="stylesheet">
        <style>
            * {{
                font-family: {scene.get("fonts", {}).get("primary", "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif")};
            }}

            html, body {{
                overflow-x: hidden;
                max-width: 100vw;
                margin: 0;
                padding: 0;
            }}

            body {{
                background: {scene.get("background", {}).get("gradient", "linear-gradient(135deg, #E1BEE7 0%, #FCE4EC 30%, #FAFAFA 60%, #E1BEE7 100%)")};
                background-size: {scene.get("background", {}).get("gradient_size", "800% 800%")};
                animation: gradient-animation {scene.get("background", {}).get("animation_duration", "30s")} ease infinite;
            }}

            @keyframes gradient-animation {{
                0%, 100% {{ background-position: 0% 50%; }}
                50% {{ background-position: 100% 50%; }}
            }}

            @keyframes float {{
                0%, 100% {{
                    transform: translate(0, 0) scale(1);
                }}
                33% {{
                    transform: translate(30px, -30px) scale(1.1);
                }}
                66% {{
                    transform: translate(-20px, 20px) scale(0.9);
                }}
            }}

            @keyframes float-delayed {{
                0%, 100% {{
                    transform: translate(0, 0) scale(1);
                }}
                33% {{
                    transform: translate(-30px, 30px) scale(1.05);
                }}
                66% {{
                    transform: translate(20px, -20px) scale(0.95);
                }}
            }}

            @keyframes fadeIn {{
                from {{ opacity: 0; }}
                to {{ opacity: 1; }}
            }}

            @keyframes slideUp {{
                from {{ transform: translateY(20px); opacity: 0; }}
                to {{ transform: translateY(0); opacity: 1; }}
            }}

            @keyframes gradient-shift {{
                0%, 100% {{ background-position: 0% center; }}
                50% {{ background-position: 100% center; }}
            }}

            /* Floating blob decorations */
            .floating-blob-1 {{
                position: fixed;
                top: 5rem;
                right: -200px;
                width: 800px;
                height: 800px;
                background: linear-gradient(to bottom right, #fbcfe8, #fda4af, #fecdd3);
                border-radius: 50%;
                opacity: 0.4;
                filter: blur(96px);
                animation: float 20s ease-in-out infinite;
                pointer-events: none;
                z-index: 0;
            }}

            .floating-blob-2 {{
                position: fixed;
                bottom: -200px;
                left: -200px;
                width: 600px;
                height: 600px;
                background: linear-gradient(to top right, #fda4af, #fbcfe8, #fda4af);
                border-radius: 50%;
                opacity: 0.4;
                filter: blur(96px);
                animation: float-delayed 25s ease-in-out infinite;
                pointer-events: none;
                z-index: 0;
            }}

            /* Custom scrollbar */
            ::-webkit-scrollbar {{
                width: {scene.get("scrollbar", {}).get("width", "8px")};
            }}

            ::-webkit-scrollbar-track {{
                background: {scene.get("scrollbar", {}).get("track_bg", "#f1f1f1")};
            }}

            ::-webkit-scrollbar-thumb {{
                background: {scene.get("scrollbar", {}).get("thumb_bg", "#E91E63")};
                border-radius: {scene.get("scrollbar", {}).get("border_radius", "4px")};
            }}

            ::-webkit-scrollbar-thumb:hover {{
                background: {scene.get("scrollbar", {}).get("thumb_hover_bg", "#C2185B")};
            }}

            /* Focus states */
            *:focus {{
                outline: 2px solid {scene["palette"]["primary"]};
                outline-offset: 2px;
            }}

            /* Message animations */
            .message-enter {{
                animation: slideUp 0.5s ease-out;
            }}

            /* Gradient text effect */
            .gradient-text {{
                background: {scene.get("gradients", {}).get("text", "linear-gradient(to right, #E91E63, #ec4899, #E91E63)")};
                background-clip: text;
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-size: 200% auto;
                animation: gradient-shift 3s ease infinite;
            }}

            @keyframes slideIn {{
                from {{
                    opacity: 0;
                    transform: translateY(10px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}

            @keyframes typing {{
                0%, 60%, 100% {{
                    transform: translateY(0);
                    opacity: 0.7;
                }}
                30% {{
                    transform: translateY(-8px);
                    opacity: 1;
                }}
            }}

            .q-message--received {{
                max-height: none !important;
                overflow: visible !important;
            }}

            /* Responsive padding for chat area */
            /* Tablet */
            @media (max-width: 1024px) {{
                .chat-padding {{
                    padding-top: 4rem !important;
                    padding-left: 1rem !important;
                    padding-right: 1rem !important;
                }}
            }}

            /* Mobile */
            @media (max-width: 768px) {{
                .chat-padding {{
                    padding-top: 2.5rem !important;
                    padding-left: 0.5rem !important;
                    padding-right: 0.5rem !important;
                }}
                .input-padding {{
                    padding-left: 0.75rem !important;
                    padding-right: 0.75rem !important;
                }}
                /* Hide checkmark icon on mobile */
                .hipaa-badge-icon {{
                    display: none !important;
                }}
                /* Mobile input layout - move plus button inside */
                .input-row-container {{
                    gap: 0 !important;
                }}
                .new-conv-btn-outside {{
                    display: none !important;
                }}
                .new-conv-btn-inside {{
                    display: flex !important;
                    width: 2.5rem !important;
                    height: 2.5rem !important;
                    min-width: 2.5rem !important;
                    min-height: 2.5rem !important;
                    margin-right: 0.5rem !important;
                }}
                .input-inner-container {{
                    padding-left: 0.5rem !important;
                }}
                .input-field {{
                    padding-left: 0 !important;
                }}
                /* Reduce intro card padding on mobile */
                .welcome-card {{
                    padding: 2rem !important;
                }}
            }}

            /* Small mobile */
            @media (max-width: 425px) {{
                .chat-padding {{
                    padding-top: 2rem !important;
                    padding-left: 0.25rem !important;
                    padding-right: 0.25rem !important;
                }}
                .input-padding {{
                    padding-left: 0.25rem !important;
                    padding-right: 0.25rem !important;
                }}
                /* Make logo smaller on small mobile */
                .header-logo {{
                    transform: scale(0.85) !important;
                }}
                /* Simplify HIPAA badge on small mobile */
                .hipaa-badge {{
                    background: transparent !important;
                    border: none !important;
                    padding: 0 !important;
                    font-size: 0.625rem !important;
                    color: #BE185D !important;
                }}
            }}
        </style>
        <script>
            // Chat history localStorage functions
            window.saveChatMessage = function(message, isUser) {{
                const history = JSON.parse(localStorage.getItem('mammoChat_history') || '[]');
                history.push({{ message: message, isUser: isUser, timestamp: Date.now() }});
                localStorage.setItem('mammoChat_history', JSON.stringify(history));
            }};

            window.loadChatHistory = function() {{
                return JSON.parse(localStorage.getItem('mammoChat_history') || '[]');
            }};

            window.clearChatHistory = function() {{
                localStorage.removeItem('mammoChat_history');
            }};
        </script>
    """
    )


def create_header(scene: Any, dark: Any) -> Any:
    """Build the MammoChat header with glassmorphism and HIPAA badge."""
    header_style = f"""
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        z-index: 50;
        background: {scene.get("header", {}).get("background", "rgba(255, 255, 255, 0.8)")};
        backdrop-filter: {scene.get("header", {}).get("backdrop_filter", "blur(16px) saturate(180%)")};
        -webkit-backdrop-filter: {scene.get("header", {}).get("backdrop_filter", "blur(16px) saturate(180%)")};
        border-bottom: {scene.get("header", {}).get("border", "1px solid rgba(229, 231, 235, 0.8)")};
        border-radius: {scene.get("header", {}).get("border_radius", "0 0 1rem 1rem")};
        box-shadow: {scene.get("header", {}).get("shadow", "0 4px 16px rgba(0, 0, 0, 0.04)")};
        margin: 0;
        padding: 0;
    """

    header = ui.header().style(header_style)
    with header:
        with ui.row().classes("w-full items-center justify-between").style(
            f"max-width: {scene.get('header', {}).get('max_width', '1800px')}; "
            f"margin: 0 auto; padding: {scene.get('header', {}).get('padding', '0.75rem 2rem')};"
        ):
            # Left side: Logo and tagline
            with ui.row().classes("items-center gap-4"):
                # Custom logo SVG with gradient
                ui.html('''
                    <div class="header-logo flex items-center gap-3 scale-75 sm:scale-100 -ml-12 sm:ml-0">
                        <svg xmlns="http://www.w3.org/2000/svg" width="250" height="64" viewBox="0 0 250 64" fill="none">
                            <defs>
                                <mask id="chat-mask">
                                    <path d="M48 16C48 11.5817 44.4183 8 40 8H16C11.5817 8 8 11.5817 8 16V36C8 40.4183 11.5817 44 16 44H20V52L28 44H40C44.4183 44 48 40.4183 48 36V16Z" fill="white"></path>
                                    <path d="M28 20C28 16.6863 30.6863 14 34 14C35.6569 14 37.1569 14.6716 38.2426 15.7574C39.3284 14.6716 40.8284 14 42.4853 14C45.799 14 48.4853 16.6863 48.4853 20C48.4853 21.3062 48.0615 22.512 47.3431 23.4853L38.2426 32.5858L29.1421 23.4853C28.4237 22.512 28 21.3062 28 20Z" fill="black"></path>
                                </mask>
                                <linearGradient id="brand-gradient" x1="0" y1="32" x2="250" y2="32" gradientUnits="userSpaceOnUse">
                                    <stop offset="0%" stop-color="#EC4899"></stop>
                                    <stop offset="100%" stop-color="#F43F5E"></stop>
                                </linearGradient>
                            </defs>
                            <g id="logo-icon">
                                <path d="M48 16C48 11.5817 44.4183 8 40 8H16C11.5817 8 8 11.5817 8 16V36C8 40.4183 11.5817 44 16 44H20V52L28 44H40C44.4183 44 48 40.4183 48 36V16Z" fill="url(#brand-gradient)" mask="url(#chat-mask)"></path>
                            </g>
                            <g id="logo-text">
                                <text x="68" y="40" font-family="Inter, sans-serif" font-size="28" font-weight="700" fill="url(#brand-gradient)">Mammo</text>
                                <text x="175" y="40" font-family="Inter, sans-serif" font-size="28" font-weight="700" fill="url(#brand-gradient)">Chat</text>
                                <text x="238" y="32" font-family="Inter, sans-serif" font-size="16" font-weight="700" fill="url(#brand-gradient)">™</text>
                            </g>
                        </svg>
                    </div>
                ''', sanitize=False)

                # Tagline
                tagline_style = f"""
                    color: {scene.get("header", {}).get("tagline_color", "#757575")};
                    font-weight: {scene.get("header", {}).get("tagline_font_weight", "300")};
                """
                ui.label(scene.get("header", {}).get("tagline", "Your journey, together")).classes(
                    scene.get("header", {}).get("tagline_classes", "text-sm gt-xs")
                ).style(tagline_style)

            # Right side: HIPAA Badge
            hipaa_badge = scene.get("header", {}).get("hipaa_badge", {})
            if hipaa_badge.get("enabled", True):
                ui.html(f'''
                    <div class="hipaa-badge" style="display: inline-flex; align-items: center; gap: 0.5rem; padding: {hipaa_badge.get("padding", "0.25rem 1rem")};
                                border-radius: {hipaa_badge.get("border_radius", "9999px")}; background: {hipaa_badge.get("background", "linear-gradient(to right, #FCE4EC, #fda4af)")};
                                border: {hipaa_badge.get("border", "1px solid #FBCFE8")}; color: {hipaa_badge.get("color", "#BE185D")}; font-size: {hipaa_badge.get("font_size", "0.75rem")}; font-weight: {hipaa_badge.get("font_weight", "500")};">
                        <svg class="hipaa-badge-icon" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                        </svg>
                        {hipaa_badge.get("text", "HIPAA Compliant")}
                    </div>
                ''', sanitize=False)

    return header


def create_chat_area(scene: Any, conversation: Any) -> tuple[Any, Any]:
    """Build the main chat interface with padding for fixed header/footer."""
    # Add padding container - extra top padding for fixed header and bottom for fixed input
    padding_top = scene.get("layout", {}).get("chat_padding_top", "4rem")
    padding_bottom = scene.get("layout", {}).get("chat_padding_bottom", "8rem")
    padding_x = scene.get("layout", {}).get("chat_padding_x", "1.5rem")

    with ui.column().classes("w-full chat-padding").style(
        f"padding: {padding_top} {padding_x} {padding_bottom} {padding_x}; position: relative; z-index: 1; min-height: 100vh;"
    ):
        chat_container = ui.column().classes("w-full mx-auto gap-6").style(
            f"max-width: {scene.get('layout', {}).get('chat_container_max_width', '900px')};"
        )

        # Add welcome card with icon
        with chat_container:
            welcome_card_style = scene.get("chat", {}).get("welcome_card", {})
            card_style = f"""
                background: {welcome_card_style.get("background", "white")};
                border-radius: {welcome_card_style.get("border_radius", "1.5rem")};
                padding: {welcome_card_style.get("padding", "2.5rem")};
                border: {welcome_card_style.get("border", "1px solid #FBCFE8")};
                box-shadow: {welcome_card_style.get("shadow", "0 4px 12px rgba(233, 30, 99, 0.08)")};
                width: {welcome_card_style.get("width", "100%")};
            """
            with ui.card().classes("message-enter welcome-card").style(card_style).props("flat"):
                # Header row with icon and title
                with ui.row().classes("items-center gap-3 w-full").style("margin-bottom: 1.5rem;"):
                    # Chat bubble with heart icon
                    icon_svg = scene.get("chat", {}).get("welcome_icon", {}).get("svg", "")
                    if icon_svg:
                        ui.html(icon_svg, sanitize=False)

                    # Title with gradient
                    welcome_title = scene.get("chat", {}).get("welcome_title", {})
                    title_style = f"""
                        font-size: {welcome_title.get("font_size", "1.75rem")};
                        font-weight: {welcome_title.get("font_weight", "400")};
                        margin: 0;
                    """
                    ui.html(
                        f'<h2 class="{welcome_title.get("gradient_class", "gradient-text")}" '
                        f'style="{title_style}">{welcome_title.get("text", "Welcome to MammoChat™")}</h2>',
                        sanitize=False
                    )

                # Content
                welcome_content = scene.get("chat", {}).get("welcome_content", {})
                content_style = f"""
                    color: {welcome_content.get("color", "#212121")};
                    font-weight: {welcome_content.get("font_weight", "300")};
                    line-height: {welcome_content.get("line_height", "1.8")};
                    font-size: {welcome_content.get("font_size", "1rem")};
                """
                ui.markdown(scene["chat"]["welcome_message"]).style(content_style)

    return None, chat_container


def create_footer(scene: Any, send: Any, new_conversation: Any) -> tuple[Any, Any]:
    """Build the footer with glassmorphism and gray input container."""
    footer_style = f"""
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 50;
        background: {scene.get("footer", {}).get("background", "rgba(255, 255, 255, 0.8)")};
        backdrop-filter: {scene.get("footer", {}).get("backdrop_filter", "blur(16px) saturate(180%)")};
        -webkit-backdrop-filter: {scene.get("footer", {}).get("backdrop_filter", "blur(16px) saturate(180%)")};
        border-top: {scene.get("footer", {}).get("border", "1px solid rgba(229, 231, 235, 0.8)")};
        border-radius: {scene.get("footer", {}).get("border_radius", "1rem 1rem 0 0")};
        box-shadow: {scene.get("footer", {}).get("shadow", "0 -4px 16px rgba(0, 0, 0, 0.04)")};
        margin: 0;
        padding: 0;
    """

    footer = ui.footer().style(footer_style)
    with footer:
        # Centered container
        with ui.column().classes("w-full input-padding").style(
            f"max-width: {scene.get('footer', {}).get('max_width', '1800px')}; "
            f"margin: 0 auto; padding: {scene.get('footer', {}).get('padding', '1.5rem')};"
        ):
            # Input row
            input_row_container = ui.row().classes("w-full items-center gap-3 input-row-container").style(
                f"max-width: {scene.get('footer', {}).get('container_max_width', '900px')}; margin: 0 auto;"
            )

            with input_row_container:
                # New conversation button with gradient
                new_btn_gradient = scene.get("footer", {}).get("new_btn_gradient",
                    "linear-gradient(to right, lab(56.9303 76.8162 -8.07021) 0%, lab(56.101 79.4328 31.4532) 100%)")
                new_btn_size = scene.get("footer", {}).get("new_btn_size", "3rem")
                new_btn_style = f"""
                    background: {new_btn_gradient};
                    color: white;
                    width: {new_btn_size};
                    height: {new_btn_size};
                    min-width: {new_btn_size};
                    min-height: {new_btn_size};
                    padding: 0;
                    transition: transform 0.2s ease, box-shadow 0.2s ease;
                """
                new_conv_btn = ui.button(on_click=new_conversation).props("round flat").style(new_btn_style).classes("new-conv-btn-outside")
                new_conv_btn.tooltip(scene.get("footer", {}).get("new_btn_tooltip", "New conversation"))
                with new_conv_btn:
                    ui.html('''
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
                             fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                             stroke-linejoin="round" style="color: white;">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                    ''', sanitize=False)

                # Input container with gray background
                input_bg = scene.get("footer", {}).get("input_background", "#f3f4f6")
                input_border = scene.get("footer", {}).get("input_border", "1px solid #d1d5db")
                input_border_radius = scene.get("footer", {}).get("input_border_radius", "9999px")
                input_padding = scene.get("footer", {}).get("input_padding", "0.5rem 1rem")
                input_min_height = scene.get("footer", {}).get("input_min_height", "3rem")

                input_container = ui.row().classes("flex-grow items-center gap-2 input-inner-container").style(
                    f"background: {input_bg}; border-radius: {input_border_radius}; "
                    f"padding: {input_padding}; border: {input_border}; "
                    f"min-height: {input_min_height}; align-items: center; position: relative;"
                )

                with input_container:
                    # New conversation button for mobile (inside input)
                    new_conv_btn_mobile = ui.button(on_click=new_conversation).props("round flat").style(
                        f"{new_btn_style} display: none;"
                    ).classes("new-conv-btn-inside")
                    new_conv_btn_mobile.tooltip(scene.get("footer", {}).get("new_btn_tooltip", "New conversation"))
                    with new_conv_btn_mobile:
                        ui.html('''
                            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
                                 fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"
                                 stroke-linejoin="round" style="color: white;">
                                <line x1="12" y1="5" x2="12" y2="19"></line>
                                <line x1="5" y1="12" x2="19" y2="12"></line>
                            </svg>
                        ''', sanitize=False)

                    text = (
                        ui.input(placeholder=scene.get("footer", {}).get("input_placeholder", "Share what's on your mind..."))
                        .props(scene.get("footer", {}).get("input_props", "borderless dense"))
                        .classes("flex-grow input-field")
                        .style("background: transparent; font-weight: 300; font-size: 0.875rem; color: #6b7280; align-self: center;")
                        .on("keydown.enter", send)
                        .tooltip(scene.get("footer", {}).get("input_tooltip", "Type your message here"))
                    )

                    # Send button with gradient
                    send_btn_gradient = scene.get("footer", {}).get("send_btn_gradient", "linear-gradient(to right, #ec4899, #f43f5e)")
                    send_btn_size = scene.get("footer", {}).get("send_btn_size", "3rem")
                    send_btn_style = f"""
                        background: {send_btn_gradient};
                        color: white;
                        width: {send_btn_size};
                        height: {send_btn_size};
                        min-width: {send_btn_size};
                        min-height: {send_btn_size};
                        padding: 0;
                        transition: transform 0.2s ease, box-shadow 0.2s ease;
                    """
                    send_btn = ui.button(on_click=send).props("round").style(send_btn_style)
                    send_btn.tooltip(scene.get("footer", {}).get("send_btn_tooltip", "Send message"))
                    with send_btn:
                        ui.html(scene.get("btn_send", {}).get("icon",
                            '''<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: white;"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>'''
                        ), sanitize=False)

    return text, send_btn


def setup_ui(chat_service: ChatService) -> None:
    """Set up the main user interface for the MammoChat application.

    This function initializes the complete UI layout including:
    - Theme configuration and color schemes
    - Header with branding and dark mode toggle
    - Message display area with chat bubbles
    - Input controls for sending messages
    - Event handlers for user interactions

    The UI is designed to be responsive and theme-aware, supporting
    both light and dark modes with consistent MammoChat branding.

    Args:
        chat_service: The chat service instance for handling message operations.
    """

    scene = config.scene

    dark = ui.dark_mode()

    # Initialize theme state on page load
    ui.run_javascript(
        f"""
        document.addEventListener('DOMContentLoaded', function() {{
            const isDark = {str(dark.value).lower()};
            if (isDark) {{
                document.body.classList.add('dark-theme');
                document.documentElement.setAttribute('data-theme', 'dark');
            }} else {{
                document.body.classList.remove('dark-theme');
                document.documentElement.setAttribute('data-theme', 'light');
            }}
        }});
    """
    )

    setup_colors(scene)
    setup_head_html(scene)

    # Add floating blob decorations
    ui.html('<div class="floating-blob-1"></div><div class="floating-blob-2"></div>', sanitize=False)

    conversation = ConversationState()

    async def send() -> None:
        """Handle sending a user message and processing the AI response."""
        question = text.value
        text.value = ""
        if not question.strip():
            return

        text.disable()
        send_btn.disable()

        with message_container:
            # User message with gradient background
            user_msg = scene.get("chat", {}).get("user_message", {})
            user_style = f"""
                background: {user_msg.get("background", "linear-gradient(to right, lab(56.9303 76.8162 -8.07021) 0%, lab(56.101 79.4328 31.4532) 100%)")};
                border: {user_msg.get("border", "1px solid #FBCFE8")};
                border-radius: {user_msg.get("border_radius", "1.5rem 0.25rem 1.5rem 1.5rem")};
                padding: {user_msg.get("padding", "1.25rem 1.75rem")};
                box-shadow: {user_msg.get("shadow", "0 4px 12px rgba(233, 30, 99, 0.1)")};
                max-width: {user_msg.get("max_width", "75%")};
            """
            with ui.row().classes("w-full justify-end message-enter"):
                with ui.card().props("flat").style(user_style):
                    ui.label(question).style(
                        f"color: {user_msg.get('color', '#ffffff')}; "
                        f"font-weight: {user_msg.get('font_weight', '300')}; "
                        f"line-height: {user_msg.get('line_height', '1.7')}; "
                        f"font-size: {user_msg.get('font_size', '1rem')};"
                    )

            # Assistant message with avatar and white background
            assistant_msg = scene.get("chat", {}).get("assistant_message", {})
            assistant_row = ui.row().classes("w-full items-start message-enter").style("gap: 8px;")
            with assistant_row:
                # Bot avatar
                avatar_svg = scene.get("chat", {}).get("assistant_avatar", {}).get("icon", "")
                if avatar_svg:
                    ui.html(f'''
                        <div style="width: 2rem; height: 2rem; border-radius: 9999px;
                                    background: linear-gradient(to bottom right, #ec4899, #f43f5e);
                                    display: flex; align-items: center; justify-content: center; flex-shrink: 0;">
                            {avatar_svg}
                        </div>
                    ''', sanitize=False)

                # Message card with white background
                message_style = f"""
                    background: white;
                    border: {assistant_msg.get("border", "1px solid rgba(255, 255, 255, 0.3)")};
                    border-radius: {assistant_msg.get("border_radius", "0.25rem 1.5rem 1.5rem 1.5rem")};
                    padding: {assistant_msg.get("padding", "1.25rem 1.75rem")};
                    box-shadow: {assistant_msg.get("shadow", "0 4px 12px rgba(233, 30, 99, 0.2)")};
                    max-width: {assistant_msg.get("max_width", "75%")};
                """
                response_message = ui.card().props("flat").style(message_style)

        with response_message:
            ui.spinner()

        # Use NiceGUI's native task processing with refreshable UI
        response_state = {"content": "", "error": None}

        @ui.refreshable  # type: ignore[misc]
        def response_display() -> None:
            """Refreshable UI component for streaming response."""
            assistant_msg = scene.get("chat", {}).get("assistant_message", {})
            typing_indicator = scene.get("chat", {}).get("typing_indicator", {})
            text_style = f"""
                color: {assistant_msg.get('color', '#212121')};
                font-weight: {assistant_msg.get('font_weight', '300')};
                line-height: {assistant_msg.get('line_height', '1.7')};
                font-size: {assistant_msg.get('font_size', '1rem')};
            """
            if response_state["error"]:
                ui.label(f"Error: {response_state['error']}").classes("text-left").style(text_style)
            elif not response_state["content"]:
                ui.spinner("dots", size="sm").style(f"color: {typing_indicator.get('spinner_color', '#EC4899')};")
            else:
                ui.label(strip_markdown(response_state["content"])).classes("text-left").style(text_style)

        # Clear and show initial spinner
        response_message.clear()
        with response_message:
            response_display()

        async def stream_worker() -> None:
            """NiceGUI native worker for streaming chat responses."""
            try:
                async for event in chat_service.stream_chat(conversation, question):
                    if event.event_type == "MESSAGE_CHUNK":
                        chunk = event.payload.get("content", "")
                        response_state["content"] += chunk
                        # Refresh the UI component
                        response_display.refresh()
                    elif event.event_type == "MESSAGE_END":
                        # Final refresh
                        response_display.refresh()
            except Exception as e:
                response_state["error"] = str(e)
                response_display.refresh()
            finally:
                # Re-enable UI controls
                text.enable()
                send_btn.enable()

        # Start the worker using NiceGUI's task system
        ui.timer(0.1, lambda: asyncio.create_task(stream_worker()), once=True)

        # Autoscroll to bottom after message is added
        await asyncio.sleep(0.1)  # Brief delay to ensure DOM updates
        ui.run_javascript("window.scrollTo({ top: document.body.scrollHeight, behavior: 'smooth' });")

    def new_conversation() -> None:
        """Start a new conversation."""
        conversation.clear_messages()
        message_container.clear()
        with message_container:
            assistant_row_classes = scene.get("chat", {}).get(
                "assistant_row_classes", "w-full justify-start"
            )
            welcome_props = scene.get("chat", {}).get(
                "welcome_message_props", "bg-color=accent text-color=grey-8"
            )
            welcome_classes = scene.get("chat", {}).get(
                "welcome_message_classes",
                "bg-white border border-slate-200 text-slate-700 shadow-md "
                "rounded-2xl p-5 max-w-[70%] animate-[slideIn_0.3s_ease-out] "
                "leading-relaxed transition-all duration-300",
            )
            with ui.row().classes(assistant_row_classes):
                ui.chat_message(
                    text=scene["chat"]["welcome_message"], sent=False
                ).props(welcome_props).classes(welcome_classes)
        # No autoscroll on new conversation to preserve welcome message visibility

    create_header(scene, dark)
    _, message_container = create_chat_area(scene, conversation)
    text, send_btn = create_footer(scene, send, new_conversation)
