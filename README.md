> [!Warning]
>  organichat is very much _in development_ and currently there is no networking capability. While I have build some sort of backend, I have yet to build it into the UI (I shall once I finish it).

# organichat.
Most mainstream messaging apps have end-to-end encryption, so no one can see your messages other than the recipient and the sender - right? What if your phone is stolen or someone is looking through your chats (i.e parents, friends)? 

_organichat._ is an incognito mode for talking, packaged in an accessable TUI format that can run on any device with an internet connection (and a terminal). Every chat is cleared once a session has ended.

## how it works
Self-clearing chats would be a hub for bullying and discrimination online, but you cannot just message someone in organichat, you have to get both clients to connect to each other in order to start a session. Therefore, organichat is designed to be used in conjunction with another chat program as getting 2 people online at once at the same time can be difficult without prior conversation.

### breakdown
- Both clients open _organichat._
- Both connects to each other through TCP by inputting ip and port in main menu
- Session starts
- No chat logs recorded
- Session ends when one client leaves
- Repeat!

## roadmap
- [ ] friends list
- [ ] chat capability
- [ ] emoticon library (rather than emoji)

## tty
One of my main goals of _organichat._ is having most of the functionality fully work on a regular TTY - the most basic terminal you can get. I can guarantee you that a TTY will be able to:
- send and receive messages
- have access to the emoticon library
- friending support
- any functionality in the future (with exceptions)

TTYs are obviously very limited in terms of (default) font so due to that I want to retain functionality but not all aesthetics. They will still retain the same layout and shortcuts.

## no ai
AI is a fancy info-stealer ripping code from across the internet. It infringes on people's hard work and cannot think for itself. That is why every character of code in _organichat._ is completely hand-written. If you are going to make a PR (thank you!) then expect it to be rejected if _any_ form of AI was used during it's production.

<img width="131" height="42" alt="Scripted-By-Humans-Not-By-AI-Badge-white" src="https://github.com/user-attachments/assets/ac3dc558-58ab-4c6a-9a19-aa9af4528418" />

# 

_organichat._ is built with the [Textual](https://github.com/textualize/textual/) library, a brilliant and easy to use TUI framework for python.
