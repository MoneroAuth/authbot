# authbot
**Self-Sovereign Identity Assistant**

The authbot is a self-sovereign identity assistant that utilizes the MoneroAuth protocol. It encapsulates the complexity of public key cryptography and key management away from the user. The authbot application is a program written in python, that integrates two public open source protocols:

[Monero protocol](https://www.getmonero.org/) that is used for public key cryptography and key management.

[Matrix protocol](https://www.getmonero.org/) that is used for decentralized, end-to-end encrypted, messaging.

The authbot program can run on computers (desktop, laptop, single-board computers, virtual machines, and even in the cloud, on virtual private servers). Each authbot is privately owned by it's user and serves only it's user.

The user interface to authbot, is typically an end-to-end encrypted messaging application such as [element](https://element.io/) that can be used on computers and mobile devices.

So a user's authbot program can run anywhere in the world, needing only a network connection. Users communicate with their authbot via secure, end-to-end encrypted messaging, typically with a mobile device.

# Videos

A quick [video demonstration](https://moneroauth.org/videos/WebAuth-take2.m4v) of securely authenticating to a web site using MoneroAuth

A quick [video demonstration](https://moneroauth.org/videos/MoneroAuth-SignVerify-FinalCut.m4v) of general purpose digital signature services using MoneroAuth

[MoneroAuth Resource Management](https://moneroauth.org/videos/kdenlive-ResourceManagement2.m4v). (This is a rough-cut video. A better one will be provided soon).

A quick [video demonstration](https://moneroauth.org/videos/nym-demo2.m4v) of [Nym network](https://nymtech.net) integration with the authbot.


# Installation/Dependencies

We choose to run authbot only on Linux.

**Dependencies**

[monero](https://github.com/monero-project/monero)

[matrix-eno-bot](https://github.com/8go/matrix-eno-bot)

[matrix-commander](https://github.com/8go/matrix-commander)

[QR-Code-generator](https://github.com/nayuki/QR-Code-generator)

[SQLite](https://sqlite.org/index.html)

*All software (including the dependencies) have been installed in the binary files that can be downloaded (see install directory). All you need to do then is perform some configuration steps.*

**Installation**

Installation files describing specific installation instructions for different authbot deployment targets (PC, VirtualBox virtual machine, cloud vps, and various single-board computers) can be found in the /install directory.
