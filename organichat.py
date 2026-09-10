# "there is high-res ascii art of ppl's ascii parts" -js
import re
from time import localtime, strftime

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Label, Markdown, TextArea

msg_sent = ""
msg_user = ""

class MsgSend(Button):
    """A widget to send a message."""

class MsgInputTxt(TextArea):
    """A widget to enter a message."""

class MsgInput(HorizontalGroup):
    """A widget to enter a message."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield MsgInputTxt(placeholder="message...", id="msginput", language="markdown")
        yield MsgSend(label="->", tooltip="Send message", id="msgsend")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Send the message over tcp"""
        global msg_sent
        global msg_user

        msg_input = self.query_one("#msginput", MsgInputTxt)
        msg_user = "0.0.0.0"

        msg = msg_input.text
        if msg.strip():
            msg = msg.strip()
            msg_sent = msg
            msg_input.text = ""
            history = self.app.query_one("#msghistory", MsgHistory)

            new_msg = Msg()
            history.mount(new_msg)
            new_msg.scroll_visible()

            msg_input.focus()

class Msg(Widget):
    """A widget to display a given message"""

    def __init__(self) -> None:
        """Define variables"""
        global msg_sent
        global msg_user

        super().__init__()

        self.time = strftime("%H:%M:%S", localtime())
        self.msg_sent = msg_sent
        self.msg_user = msg_user

        self.time = strftime("%H:%M:%S", localtime())
        self.text = f"[b]{msg_user}[/b] | [d]{self.time}[/d]"

    def on_mount(self):
        self.styles.animate("opacity", value=1.0, duration=0.8, easing="out_quart")


    def compose(self) -> ComposeResult:
        """Compose message instance"""

        md_msg = Label(msg_sent, classes="msgcontent")
        md_msg.border_title = self.text
        yield md_msg

                

class MsgHistory(VerticalScroll):
    """A widget to display message history"""

class OrganichatClient(App):
    """A Textual app to chat incognito :3"""

    CSS_PATH = "organicss.tcss"

    BINDINGS = [  # noqa: RUF012
        Binding("ctrl+d", "toggle_dark", "Toggle dark mode", priority=True),
        Binding("ctrl+enter", "send_msg", "Send message")
    ]

    def __init__(self):
        super().__init__()
        self.theme = "tokyo-night"

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield MsgHistory(id="msghistory")
        yield MsgInput()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "tokyo-night" if self.theme == "solarized-light" else "solarized-light"
        )

    def action_send_msg(self) -> None:
        """Send the message over tcp"""
        global msg_sent
        global msg_user

        msg_input = self.query_one("#msginput", MsgInputTxt)
        msg_user = "0.0.0.0"

        msg = msg_input.text
        if msg.strip():
            msg_sent = msg
            msg_input.text = ""
            history = self.query_one("#msghistory", MsgHistory)

            new_msg = Msg()
            history.mount(new_msg)
            new_msg.scroll_visible()

            msg_input.focus()


if __name__ == "__main__":
    app = OrganichatClient()
    app.run()
