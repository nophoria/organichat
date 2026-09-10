# "there is high-res ascii art of ppl's ascii parts" -js
import re
from time import localtime, strftime

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import HorizontalGroup, VerticalScroll
from textual.widget import Widget
from textual.widgets import Button, Footer, Header, Label, TextArea

msg_sent = ""
msg_user = ""
chatter = "your dad"
you = "0.0.0.0" #TODO: implement ip addr detection - public or local?

class TitleBar(HorizontalGroup):
    """The titlebar widget shown at the top of a conversation"""
    def compose(self):
        text = f"[b]Chatting with:[/b] {chatter}"  # noqa: W605
        yield Label(text, id="titletext")
        yield Button("Leave", variant="error", id="leavebutton")

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
            msg_sent = msg.strip()
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

        md_msg = Label(msg_sent.strip(), classes="msgcontent")
        md_msg.border_title = self.text
        yield md_msg

                
class ClearMsg(HorizontalGroup):
    """A widget to display a message upon chat clear"""

    def compose(self) -> None:
        yield Label("[i d]The chat was cleared[/]")

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

        self.CMD_PREFIX = "!"
        self.CMDS = {
            f"{self.CMD_PREFIX}ping" : lambda: self.bell(),
            f"{self.CMD_PREFIX}clear" : lambda: self.clear()
        }

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield TitleBar()
        yield MsgHistory(id="msghistory")
        self.msg_input = MsgInput(id="msginputcontainer")
        yield self.msg_input
        yield Footer()

    def on_mount(self) -> None:
        msg_input_txt = self.msg_input.query_one("#msginput", MsgInputTxt)
        msg_input_txt.focus()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "tokyo-night" if self.theme == "catppuccin-latte" else "catppuccin-latte"
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

            if msg in self.CMDS:
                self.CMDS[msg]()
    
    def clear(self):
        msgs = self.query(Msg)
        if msgs:
            msgs.remove()

        msgs = self.query(ClearMsg)
        if msgs:
            msgs.remove()
        
        history = self.query_one("#msghistory", MsgHistory)
        history.mount(ClearMsg())

if __name__ == "__main__":
    app = OrganichatClient()
    app.run()
