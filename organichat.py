# "there is high-res ascii art of ppl's ascii parts" -js
import json
from time import localtime, strftime

from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import HorizontalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    ListItem,
    ListView,
    TextArea,
)

msg_sent = ""
msg_user = ""
you = "0.0.0.0" #TODO: implement ip addr detection - public or local?
chatter_ip = ""


class LabelItem(ListItem):

    def __init__(self, label: str) -> None:
        super().__init__()
        self.label = label

    def compose( self ) -> ComposeResult:
        yield Label(self.label)

class StartDialog(Widget):
    """Widget to initiate a connection"""

    def __init__(self):
        super().__init__()

        try:
            self.saved_err = False
            self.saved_dec_err = False
            with open("saved.json", 'r') as f:
                self.saved = json.load(f)
        except json.JSONDecodeError as e:
            self.saved_dec_err = e
            self.saved = {}
        except Exception as e:
            self.saved_err = e
            self.saved = {}

    def compose(self) -> ComposeResult:
        yield Input(placeholder="ip address...", id="ipentry")

        if len(self.saved) > 0:
            yield Label("[i d]or pick from your saved devices...[/]", id="saveddevtitle")
        else:
            yield Label("[i d]save devices and they will show up below![/]", id="saveddevtitle")
        
        with ListView():
            if self.saved_err:
                yield ListItem(Label(f"Error while reading saved devices list: {self.saved_err}", variant="error"))
            elif self.saved_dec_err:
                yield ListItem(Label(f"Invalid saved devices list: {self.saved_dec_err}", variant="error"))
            for device in self.saved:
                yield LabelItem(rf"[b]{device}[/b] | [d]{self.saved[device]}[/]")

    def on_list_view_selected(self, event: ListView.Selected):
        self.app.chatter = event.item.label
        self.app.startdlg.display = False
        self.app.chatwin.display = True

    def on_input_submitted(self):
        """connect to client here"""
        self.app.chatter = self.query_one(Input).value

class TitleBar(HorizontalGroup):
    """The titlebar widget shown at the top of a conversation"""
    def compose(self):
        yield Label("Chatting with: your d", id="titletext")
        yield Button("Leave", variant="error", id="leavebutton")
    
    def update_title(self, current_chatter: str) -> None:
        self.query_one("#titletext", Label).update(f"[b]Chatting with:[/b] {current_chatter}")
    
    def on_button_pressed(self) -> None:
        self.app.chatwin.leave()

class MsgInputTxt(TextArea):
    """A widget to enter a message."""

class MsgSend(Button):
    """A widget to send a message."""

class MsgInput(HorizontalGroup):
    """A widget to enter a message."""

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield MsgInputTxt(placeholder="message...", id="msginput", language="markdown")
        yield MsgSend(label="->", tooltip="Send message", id="msgsend")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Send the message over tcp"""
        self.app.chatwin.action_send_msg()

class Msg(Widget):
    """A widget to display a given message"""

    def __init__(self) -> None:
        """Define variables"""

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


class ConnectMsg(HorizontalGroup):
    """A widget to display a message so the user can wait for the recipient to connect"""

    def compose(self) -> None:
        yield Label(f"[i d]Waiting for {self.app.chatter} to connect...[/]")
                
class ClearMsg(HorizontalGroup):
    """A widget to display a message upon chat clear"""

    def compose(self) -> None:
        yield Label("[i d]The chat was cleared[/]")

class MsgHistory(VerticalScroll):
    """A widget to display message history"""

class ChatWindow(Widget):
    """Chat window for organichat"""

    BINDINGS = [  # noqa: RUF012
        Binding("ctrl+enter", "send_msg", "Send message")
    ]

    def __init__(self):
        super().__init__()

        self.CMD_PREFIX = "!"
        self.CMDS = {
            f"{self.CMD_PREFIX}ping" : lambda: self.ping(),
            f"{self.CMD_PREFIX}clear" : lambda: self.clear(),
            f"{self.CMD_PREFIX}leave" : lambda: self.leave()
        }

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield TitleBar()
        yield MsgHistory(id="msghistory")
        self.msg_input = MsgInput(id="msginputcontainer")
        yield self.msg_input

    def on_mount(self) -> None:
        msg_input_txt = self.msg_input.query_one("#msginput", MsgInputTxt)
        msg_input_txt.focus()

    def action_send_msg(self) -> None:
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

        self.app.notify("Cleared chat successfully!")
    
    def ping(self):
        self.app.bell()
        self.app.notify("Pinged successfully!")
    
    def leave(self):
        self.app.chatwin.display = False
        self.app.startdlg.display = True


class OrganichatClient(App):
    """A Textual app to chat incognito :3"""

    CSS_PATH = "organicss.tcss"

    chatter = reactive("your dad")

    BINDINGS = [  # noqa: RUF012
        Binding("ctrl+d", "toggle_dark", "Toggle dark mode", priority=True),
        Binding("ctrl+enter", "send_msg", "Send message")
    ]

    def __init__(self):
        super().__init__()
        self.theme = "tokyo-night"
    
    def watch_chatter(self, old_value: str, new_value: str) -> None:
        title_bar = self.query_one(TitleBar)
        title_bar.update_title(new_value)
        self.clearchat()
        self.on_mount()

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        self.startdlg = StartDialog()
        yield self.startdlg
        self.chatwin = ChatWindow()
        yield self.chatwin
        # yield TitleBar()
        # yield MsgHistory(id="msghistory")
        # self.msg_input = MsgInput(id="msginputcontainer")
        # yield self.msg_input
        yield Footer()

        self.startdlg.display = True
        self.chatwin.display = False

    def on_mount(self) -> None:
        msg_input_txt = self.chatwin.msg_input.query_one("#msginput", MsgInputTxt)
        msg_input_txt.focus()

    def action_toggle_dark(self) -> None:
        """An action to toggle dark mode."""
        self.theme = (
            "tokyo-night" if self.theme == "catppuccin-latte" else "catppuccin-latte"
        )
    
    def clearchat(self):
        msgs = self.chatwin.query(Msg)
        if msgs:
            msgs.remove()

        clearmsgs = self.chatwin.query(ClearMsg)
        if clearmsgs:
            clearmsgs.remove()
        
        connmsgs = self.chatwin.query(ConnectMsg)
        if connmsgs:
            connmsgs.remove()
        
        msginput = self.chatwin.query_one(MsgInputTxt)
        msginput.text = ""

        connmsg = ConnectMsg()
        self.chatwin.query_one(MsgHistory).mount(connmsg)
        #msginput.read_only = True #TODO: once backend is done renable this to stop msg sendong until someone conn

    def ping(self):
        self.bell()
        self.notify("Pinged successfully!")


if __name__ == "__main__":
    app = OrganichatClient()
    app.run()
